'''
Created on Feb 6, 2015

@author: cmccully
'''
from __future__ import absolute_import, division, print_function
from future.utils import iteritems
import om10
import numpy as np
import re
import json
import os
import pandas as pd
import copy
import gzip
import shutil
from lsst.utils import getPackageDir
from lsst.sims.utils import SpecMap
from lsst.sims.catUtils.baseCatalogModels import GalaxyTileCompoundObj
from lsst.sims.photUtils.matchUtils import matchBase
from lsst.sims.photUtils.BandpassDict import BandpassDict
from lsst.sims.photUtils.Sed import Sed
from lsst.sims.utils import radiansFromArcsec
from lsst.sims.catUtils.supernovae import SNObject

__all__ = ['sprinklerCompound', 'sprinkler']
class sprinklerCompound(GalaxyTileCompoundObj):
    objid = 'sprinklerCompound'
    objectTypeId = 66

    def _final_pass(self, results):
        #From the original GalaxyTileCompoundObj final pass method
        for name in results.dtype.fields:
            if 'raJ2000' in name or 'decJ2000' in name:
                results[name] = np.radians(results[name])

        # the stored procedure on fatboy that queries the galaxies
        # constructs galtileid by taking
        #
        # tileid*10^8 + galid
        #
        # this causes galtileid to be so large that the uniqueIDs in the
        # Twinkles InstanceCatalogs are too large for PhoSim to handle.
        # Since Twinkles is only focused on one tile on the sky, we will remove
        # the factor of 10^8, making the uniqueIDs a more manageable size
        # results['galtileid'] = results['galtileid']#%100000000

        #Use Sprinkler now
        sp = sprinkler(results, self.mjd, self.specFileMap, density_param=1.0)
        results = sp.sprinkle()

        return results

class sprinkler():
    def __init__(self, catsim_cat, visit_mjd, specFileMap, om10_cat='twinkles_lenses_v2.fits',
                 sne_cat = 'dc2_sne_cat.csv', density_param=1., cached_sprinkling=True):
        """
        Parameters
        ----------
        catsim_cat: catsim catalog
            The results array from an instance catalog.
        visit_mjd: float
            The mjd of the visit
        specFileMap: 
            This will tell the instance catalog where to write the files
        om10_cat: optional, defaults to 'twinkles_lenses_v2.fits
            fits file with OM10 catalog
        sne_cat: optional, defaults to 'dc2_sne_cat.csv'
        density_param: `np.float`, optioanl, defaults to 1.0
            the fraction of eligible agn objects that become lensed and should
            be between 0.0 and 1.0.
        cached_sprinkling: boolean
            If true then pick from a preselected list of galtileids

        Returns
        -------
        updated_catalog:
            A new results array with lens systems added.
        """

        twinklesDir = getPackageDir('Twinkles')
        om10_cat = os.path.join(twinklesDir, 'data', om10_cat)
        self.catalog = catsim_cat
        # ****** THIS ASSUMES THAT THE ENVIRONMENT VARIABLE OM10_DIR IS SET *******
        lensdb = om10.DB(catalog=om10_cat)
        self.lenscat = lensdb.lenses.copy()
        self.density_param = density_param
        self.bandpassDict = BandpassDict.loadTotalBandpassesFromFiles(bandpassNames=['i'])

        self.sne_catalog = pd.read_csv(os.path.join(twinklesDir, 'data', sne_cat))
        #self.sne_catalog = self.sne_catalog.iloc[:101] ### Remove this after testing
        self.used_systems = []
        self.visit_mjd = visit_mjd
        self.sn_obj = SNObject(0., 0.)
        self.write_dir = specFileMap.subdir_map['(^specFile_)']

        self.cached_sprinkling = cached_sprinkling
        if self.cached_sprinkling is True:
            agn_cache_file = os.path.join(twinklesDir, 'data', 'test_agn_galtile_cache.csv')
            self.agn_cache = pd.read_csv(agn_cache_file)
            sne_cache_file = os.path.join(twinklesDir, 'data', 'test_sne_galtile_cache.csv')
            self.sne_cache = pd.read_csv(sne_cache_file)
        else:
            self.agn_cache = None
            self.sne_cache = None

        specFileStart = 'Burst'
        for key, val in sorted(iteritems(SpecMap.subdir_map)):
            if re.match(key, specFileStart):
                galSpecDir = str(val)
        self.galDir = str(getPackageDir('sims_sed_library') + '/' + galSpecDir + '/')
        #self.LRG_name = 'Burst.25E09.1Z.spec'
        #self.LRG = Sed()
        #self.LRG.readSED_flambda(str(galDir + self.LRG_name))
        #return

        #Calculate imsimband magnitudes of source galaxies for matching

        agn_fname = str(getPackageDir('sims_sed_library') + '/agnSED/agn.spec.gz')
        src_iband = self.lenscat['MAGI_IN']
        src_z = self.lenscat['ZSRC']
        self.src_mag_norm = []
        for src, s_z in zip(src_iband, src_z):
            agn_sed = Sed()
            agn_sed.readSED_flambda(agn_fname)
            agn_sed.redshiftSED(s_z, dimming=True)
            self.src_mag_norm.append(matchBase().calcMagNorm([src],
                                                             agn_sed,
                                                             self.bandpassDict))
        #self.src_mag_norm = matchBase().calcMagNorm(src_iband,
        #                                            [agn_sed]*len(src_iband),
        #                                            self.bandpassDict)


    def sprinkle(self):
        # Define a list that we can write out to a text file
        lenslines = []
        # For each galaxy in the catsim catalog
        updated_catalog = self.catalog.copy()
        print("Running sprinkler. Catalog Length: ", len(self.catalog))
        for rowNum, row in enumerate(self.catalog):
            if rowNum == 100 or rowNum % 100000==0:
                print("Gone through ", rowNum, " lines of catalog.")
            if not np.isnan(row['galaxyAgn_magNorm']):
                candidates = self.find_lens_candidates(row['galaxyAgn_redshift'],
                                                       row['galaxyAgn_magNorm'])
                varString = json.loads(row['galaxyAgn_varParamStr'])
                varString['pars']['t0_mjd'] = 59300.0
                row['galaxyAgn_varParamStr'] = json.dumps(varString)
                np.random.seed(row['galtileid'] % (2^32 -1))
                pick_value = np.random.uniform()
            # If there aren't any lensed sources at this redshift from OM10 move on the next object
                if (((len(candidates) > 0) and (pick_value <= self.density_param) and (self.cached_sprinkling is False)) | 
                    ((self.cached_sprinkling is True) and (row['galtileid'] in self.agn_cache['galtileid'].values))):
                    # Randomly choose one the lens systems
                    # (can decide with or without replacement)
                    # Sort first to make sure the same choice is made every time
                    if self.cached_sprinkling is True:
                        twinkles_sys_cache = self.agn_cache.query('galtileid == %i' % row['galtileid'])['twinkles_system'].values[0]
                        newlens = self.lenscat[np.where(self.lenscat['twinklesId'] == twinkles_sys_cache)[0]][0]
                    else:
                        candidates = candidates[np.argsort(candidates['twinklesId'])]
                        newlens = np.random.choice(candidates)
                    # Append the lens galaxy
                    # For each image, append the lens images
                    for i in range(newlens['NIMG']):
                        lensrow = row.copy()
                        # XIMG and YIMG are in arcseconds
                        # raPhSim and decPhoSim are in radians
                        #Shift all parts of the lensed object, not just its agn part
                        for lensPart in ['galaxyBulge', 'galaxyDisk', 'galaxyAgn']:
                            lens_ra = lensrow[str(lensPart+'_raJ2000')]
                            lens_dec = lensrow[str(lensPart+'_decJ2000')]
                            delta_ra = np.radians(newlens['XIMG'][i] / 3600.0) / np.cos(lens_dec)
                            delta_dec = np.radians(newlens['YIMG'][i] / 3600.0)
                            lensrow[str(lensPart + '_raJ2000')] = lens_ra + delta_ra
                            lensrow[str(lensPart + '_decJ2000')] = lens_dec + delta_dec
                        mag_adjust = 2.5*np.log10(np.abs(newlens['MAG'][i]))
                        lensrow['galaxyAgn_magNorm'] -= mag_adjust
                        varString = json.loads(lensrow['galaxyAgn_varParamStr'])
                        varString['pars']['t0Delay'] = newlens['DELAY'][i]
                        varString['varMethodName'] = 'applyAgnTimeDelay'
                        lensrow['galaxyAgn_varParamStr'] = json.dumps(varString)
                        lensrow['galaxyDisk_majorAxis'] = 0.0
                        lensrow['galaxyDisk_minorAxis'] = 0.0
                        lensrow['galaxyDisk_positionAngle'] = 0.0
                        lensrow['galaxyDisk_internalAv'] = 0.0
                        lensrow['galaxyDisk_magNorm'] = np.nan
                        lensrow['galaxyDisk_sedFilename'] = None
                        lensrow['galaxyBulge_majorAxis'] = 0.0
                        lensrow['galaxyBulge_minorAxis'] = 0.0
                        lensrow['galaxyBulge_positionAngle'] = 0.0
                        lensrow['galaxyBulge_internalAv'] = 0.0
                        lensrow['galaxyBulge_magNorm'] = np.nan
                        lensrow['galaxyBulge_sedFilename'] = None
                        lensrow['galaxyBulge_redshift'] = newlens['ZSRC']
                        lensrow['galaxyDisk_redshift'] = newlens['ZSRC']
                        lensrow['galaxyAgn_redshift'] = newlens['ZSRC']
                        #To get back twinklesID in lens catalog from phosim catalog id number
                        #just use np.right_shift(phosimID-28, 10). Take the floor of the last
                        #3 numbers to get twinklesID in the twinkles lens catalog and the remainder is
                        #the image number minus 1.
                        lensrow['galtileid'] = (lensrow['galtileid']*10000 +
                                                newlens['twinklesId']*4 + i)

                        updated_catalog = np.append(updated_catalog, lensrow)

                    #Now manipulate original entry to be the lens galaxy with desired properties
                    #Start by deleting Disk and AGN properties
                    if not np.isnan(row['galaxyDisk_magNorm']):
                        row['galaxyDisk_majorAxis'] = 0.0
                        row['galaxyDisk_minorAxis'] = 0.0
                        row['galaxyDisk_positionAngle'] = 0.0
                        row['galaxyDisk_internalAv'] = 0.0
                        row['galaxyDisk_magNorm'] = np.nan
                        row['galaxyDisk_sedFilename'] = None
                    row['galaxyAgn_magNorm'] = np.nan
                    row['galaxyAgn_sedFilename'] = None
                    #Now insert desired Bulge properties
                    row['galaxyBulge_sedFilename'] = newlens['lens_sed']
                    row['galaxyBulge_redshift'] = newlens['ZLENS']
                    row['galaxyDisk_redshift'] = newlens['ZLENS']
                    row['galaxyAgn_redshift'] = newlens['ZLENS']
                    row_lens_sed = Sed()
                    row_lens_sed.readSED_flambda(str(self.galDir + newlens['lens_sed']))
                    row_lens_sed.redshiftSED(newlens['ZLENS'], dimming=True)
                    row['galaxyBulge_magNorm'] = matchBase().calcMagNorm([newlens['APMAG_I']], row_lens_sed, 
                                                                         self.bandpassDict) #Changed from i band to imsimband
                    row['galaxyBulge_majorAxis'] = radiansFromArcsec(newlens['REFF'] / np.sqrt(1 - newlens['ELLIP']))
                    row['galaxyBulge_minorAxis'] = radiansFromArcsec(newlens['REFF'] * np.sqrt(1 - newlens['ELLIP']))
                    #Convert orientation angle to west of north from east of north by *-1.0 and convert to radians
                    row['galaxyBulge_positionAngle'] = newlens['PHIE']*(-1.0)*np.pi/180.0
                    #Replace original entry with new entry
                    updated_catalog[rowNum] = row
            else:
                if self.cached_sprinkling is True:
                    if row['galtileid'] in self.sne_cache['galtileid'].values:
                        use_system = self.sne_cache.query('galtileid == %i' % row['galtileid'])['twinkles_system'].values
                        use_df = self.sne_catalog.query('twinkles_sysno == %i' % use_system)
                        self.used_systems.append(use_system)
                    else:
                        continue
                else:
                    lens_sne_candidates = self.find_sne_lens_candidates(row['galaxyDisk_redshift'])
                    candidate_sysno = np.unique(lens_sne_candidates['twinkles_sysno'])
                    num_candidates = len(candidate_sysno)
                    if num_candidates == 0:
                        continue
                    used_already = np.array([sys_num in self.used_systems for sys_num in candidate_sysno])
                    unused_sysno = candidate_sysno[~used_already]
                    if len(unused_sysno) == 0:
                        continue
                    np.random.seed(row['galtileid'] % (2^32 -1))
                    use_system = np.random.choice(unused_sysno)
                    use_df = self.sne_catalog.query('twinkles_sysno == %i' % use_system)
                
                for i in range(len(use_df)):
                    lensrow = row.copy()
                    for lensPart in ['galaxyBulge', 'galaxyDisk', 'galaxyAgn']:
                        lens_ra = lensrow[str(lensPart+'_raJ2000')]
                        lens_dec = lensrow[str(lensPart+'_decJ2000')]
                        delta_ra = np.radians(use_df['x'].iloc[i] / 3600.0) / np.cos(lens_dec)
                        delta_dec = np.radians(use_df['y'].iloc[i] / 3600.0)
                        lensrow[str(lensPart + '_raJ2000')] = lens_ra + delta_ra
                        lensrow[str(lensPart + '_decJ2000')] = lens_dec + delta_dec
                    lensrow['galaxyAgn_magNorm'] = use_df['mag'].iloc[i] #This will need to be adjusted to proper band
                    # varString = json.loads(lensrow['galaxyAgn_varParamStr'])
                    varString = 'None'
                    lensrow['galaxyAgn_varParamStr'] = varString
                    lensrow['galaxyDisk_majorAxis'] = 0.0
                    lensrow['galaxyDisk_minorAxis'] = 0.0
                    lensrow['galaxyDisk_positionAngle'] = 0.0
                    lensrow['galaxyDisk_internalAv'] = 0.0
                    lensrow['galaxyDisk_magNorm'] = np.nan
                    lensrow['galaxyDisk_sedFilename'] = None
                    lensrow['galaxyBulge_majorAxis'] = 0.0
                    lensrow['galaxyBulge_minorAxis'] = 0.0
                    lensrow['galaxyBulge_positionAngle'] = 0.0
                    lensrow['galaxyBulge_internalAv'] = 0.0
                    lensrow['galaxyBulge_magNorm'] = np.nan
                    lensrow['galaxyBulge_sedFilename'] = None
                    z_s = use_df['zs'].iloc[i]
                    lensrow['galaxyBulge_redshift'] = z_s
                    lensrow['galaxyDisk_redshift'] = z_s
                    lensrow['galaxyAgn_redshift'] = z_s
                    #To get back twinklesID in lens catalog from phosim catalog id number
                    #just use np.right_shift(phosimID-28, 10). Take the floor of the last
                    #3 numbers to get twinklesID in the twinkles lens catalog and the remainder is
                    #the image number minus 1.
                    lensrow['galtileid'] = (lensrow['galtileid']*10000 +
                                            use_system*4 + i)

                    add_to_cat = self.create_sn_sed(use_df.iloc[i], lensrow['galaxyAgn_raJ2000'],
                                                    lensrow['galaxyAgn_decJ2000'], self.visit_mjd)
                    lensrow['galaxyAgn_sedFilename'] = 'specFile_tsn_%i_%i_%f.txt' % (use_system, use_df['imno'].iloc[i],
                                                                                           self.visit_mjd)
                    
                    if add_to_cat is True:
                        updated_catalog = np.append(updated_catalog, lensrow)
                    else:
                        continue
                    #Now manipulate original entry to be the lens galaxy with desired properties
                    #Start by deleting Disk and AGN properties
                if not np.isnan(row['galaxyDisk_magNorm']):
                    row['galaxyDisk_majorAxis'] = 0.0
                    row['galaxyDisk_minorAxis'] = 0.0
                    row['galaxyDisk_positionAngle'] = 0.0
                    row['galaxyDisk_internalAv'] = 0.0
                    row['galaxyDisk_magNorm'] = np.nan
                    row['galaxyDisk_sedFilename'] = None
                row['galaxyAgn_magNorm'] = np.nan
                row['galaxyAgn_sedFilename'] = None
                #Now insert desired Bulge properties
                row['galaxyBulge_sedFilename'] = use_df['lens_sed'].iloc[0]
                row['galaxyBulge_redshift'] = use_df['zl'].iloc[0]
                row['galaxyDisk_redshift'] = use_df['zl'].iloc[0]
                row['galaxyAgn_redshift'] = use_df['zl'].iloc[0]
                row['galaxyBulge_magNorm'] = use_df['bulge_magnorm'].iloc[0]
                # row['galaxyBulge_magNorm'] = matchBase().calcMagNorm([newlens['APMAG_I']], self.LRG, self.bandpassDict) #Changed from i band to imsimband
                row['galaxyBulge_majorAxis'] = radiansFromArcsec(use_df['r_eff'].iloc[0] / np.sqrt(1 - use_df['e'].iloc[0]))
                row['galaxyBulge_minorAxis'] = radiansFromArcsec(use_df['r_eff'].iloc[0] * np.sqrt(1 - use_df['e'].iloc[0]))
                #Convert orientation angle to west of north from east of north by *-1.0 and convert to radians
                row['galaxyBulge_positionAngle'] = use_df['theta_e'].iloc[0]*(-1.0)*np.pi/180.0
                #Replace original entry with new entry
                updated_catalog[rowNum] = row

                    
        return updated_catalog

    def find_lens_candidates(self, galz, gal_mag):
        # search the OM10 catalog for all sources +- 0.1 dex in redshift
        # and within .25 mags of the CATSIM source
        w = np.where((np.abs(np.log10(self.lenscat['ZSRC']) - np.log10(galz)) <= 0.1) &
                     (np.abs(self.src_mag_norm - gal_mag) <= .25))[0]
        lens_candidates = self.lenscat[w]

        return lens_candidates

    def find_sne_lens_candidates(self, galz):
        
        w = np.where((np.abs(np.log10(self.sne_catalog['zs']) - np.log10(galz)) <= 0.1))
        lens_candidates = self.sne_catalog.iloc[w]

        return lens_candidates

    def create_sn_sed(self, system_df, sn_ra, sn_dec, sed_mjd):

        sn_param_dict = copy.deepcopy(self.sn_obj.SNstate)
        sn_param_dict['_ra'] = sn_ra
        sn_param_dict['_dec'] = sn_dec
        sn_param_dict['z'] = system_df['zs']
        sn_param_dict['c'] = system_df['c']
        sn_param_dict['x0'] = system_df['x0']
        sn_param_dict['x1'] = system_df['x1']
        sn_param_dict['t0'] = system_df['t_start'] # +1500. ### For testing only
        
        current_sn_obj = self.sn_obj.fromSNState(sn_param_dict)
        sn_sed_obj = current_sn_obj.SNObjectSED(time=sed_mjd, 
                                                wavelen=self.bandpassDict['i'].wavelen)
        flux_500 = sn_sed_obj.flambda[np.where(sn_sed_obj.wavelen >= 499.99)][0]

        if flux_500 > 0.:
            add_to_cat = True
            sed_filename = '%s/specFile_tsn_%i_%i_%f.txt' % (self.write_dir, system_df['twinkles_sysno'], 
                                                                       system_df['imno'], sed_mjd)
            sn_sed_obj.writeSED(sed_filename)
            with open(sed_filename, 'rb') as f_in, gzip.open(str(sed_filename + '.gz'), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(sed_filename)
        else:
            add_to_cat = False


        return add_to_cat

    def update_catsim(self):
        # Remove the catsim object
        # Add lensed images to the catsim given source brightness and magnifications
        # Add lens galaxy to catsim
        return

    def catsim_to_phosim(self):
        # Pass this catsim to phosim to make images
        return
