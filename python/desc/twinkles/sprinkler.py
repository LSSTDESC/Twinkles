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
from lsst.utils import getPackageDir
from lsst.sims.utils import SpecMap
from lsst.sims.catUtils.baseCatalogModels import GalaxyTileCompoundObj
from lsst.sims.photUtils.matchUtils import matchBase
from lsst.sims.photUtils.BandpassDict import BandpassDict
from lsst.sims.photUtils.Sed import Sed
from lsst.sims.utils import radiansFromArcsec

__all__ = ['sprinklerCompound', 'sprinkler']
class sprinklerCompound(GalaxyTileCompoundObj):
    objid = 'sprinklerCompound'
    objectTypeID = 1024

    def _final_pass(self, results):
        #From the original GalaxyTileCompoundObj final pass method
        for name in results.dtype.fields:
            if 'raJ2000' in name or 'decJ2000' in name:
                results[name] = np.radians(results[name])

        #Use Sprinkler now
        sp = sprinkler(results, density_param = 1.0)
        results = sp.sprinkle()

        return results

class sprinkler():
    def __init__(self, catsim_cat, om10_cat='twinkles_tdc_rung4.fits',
                 density_param=1.):
        """
        Parameters
        ----------
        catsim_cat: catsim catalog
            The results array from an instance catalog.
        om10_cat: optional, defaults to 'twinkles_tdc_rung4.fits
            fits file with OM10 catalog
        density_param: `np.float`, optioanl, defaults to 1.0
            the fraction of eligible agn objects that become lensed and should
            be between 0.0 and 1.0.
        
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

        specFileStart = 'Burst'
        for key, val in sorted(iteritems(SpecMap.subdir_map)):
            if re.match(key, specFileStart):
                galSpecDir = str(val)
        galDir = str(getPackageDir('sims_sed_library') + '/' + galSpecDir + '/')
        self.LRG_name = 'Burst.25E09.1Z.spec'
        self.LRG = Sed()
        self.LRG.readSED_flambda(str(galDir + self.LRG_name))
        #return

        #Calculate imsimband magnitudes of source galaxies for matching
        agn_sed = Sed()
        agn_fname = str(getPackageDir('sims_sed_library') + '/agnSED/agn.spec.gz')
        agn_sed.readSED_flambda(agn_fname)
        src_iband = self.lenscat['MAGI_IN']
        self.src_mag_norm = []
        for src in src_iband:
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
                if ((len(candidates) > 0) and (pick_value <= self.density_param)):
                    # Randomly choose one the lens systems
                    # (can decide with or without replacement)
                    newlens = np.random.choice(candidates)

                    # Append the lens galaxy
                    # For each image, append the lens images
                    for i in range(newlens['NIMG']):
                        lensrow = row.copy()
                        # XIMG and YIMG are in arcseconds
                        # raPhSim and decPhoSim are in radians
                        #Shift all parts of the lensed object, not just its agn part
                        for lensPart in ['galaxyBulge', 'galaxyDisk', 'galaxyAgn']:
                            lensrow[str(lensPart + '_raJ2000')] += np.radians(newlens['XIMG'][i]/(np.cos(np.radians(lensrow[str(lensPart + '_decJ2000')]))*3600.))
                            lensrow[str(lensPart + '_decJ2000')] += np.radians(newlens['YIMG'][i]/3600.)
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
                    row['galaxyBulge_sedFilename'] = self.LRG_name
                    row['galaxyBulge_redshift'] = newlens['ZLENS']
                    row['galaxyDisk_redshift'] = newlens['ZLENS']
                    row['galaxyAgn_redshift'] = newlens['ZLENS']
                    row['galaxyBulge_magNorm'] = matchBase().calcMagNorm([newlens['APMAG_I']], self.LRG, self.bandpassDict) #Changed from i band to imsimband
                    newlens['REFF'] = 1.0 #Hard coded for now. See issue in OM10 github.
                    row['galaxyBulge_majorAxis'] = radiansFromArcsec(newlens['REFF'])
                    row['galaxyBulge_minorAxis'] = radiansFromArcsec(newlens['REFF'] * (1 - newlens['ELLIP']))
                    #Convert orientation angle to west of north from east of north by *-1.0 and convert to radians
                    row['galaxyBulge_positionAngle'] = newlens['PHIE']*(-1.0)*np.pi/180.0
                    #Replace original entry with new entry
                    updated_catalog[rowNum] = row

        return updated_catalog

    def find_lens_candidates(self, galz, gal_mag):
        # search the OM10 catalog for all sources +- 0.05 in redshift from the catsim source
        w = np.where((np.abs(np.log10(self.lenscat['ZSRC']) - np.log10(galz)) <= 0.1) &
                     (np.abs(self.src_mag_norm - gal_mag) <= .25))[0]
        lens_candidates = self.lenscat[w]

        return lens_candidates

    def update_catsim(self):
        # Remove the catsim object
        # Add lensed images to the catsim given source brightness and magnifications
        # Add lens galaxy to catsim
        return

    def catsim_to_phosim(self):
        # Pass this catsim to phosim to make images
        return
