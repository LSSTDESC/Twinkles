'''
Created on Feb 6, 2015

@author: cmccully
'''
import om10
import numpy as np
from lsst.sims.catUtils.baseCatalogModels import GalaxyTileCompoundObj
import random
import os


class sprinklerCompound(GalaxyTileCompoundObj):
    objid = 'sprinklerCompound'
    objectTypeID = 1024

    def _final_pass(self, results):
        sp = sprinkler(results)
        results = sp.sprinkle()
        return results

class sprinkler():
    def __init__(self, catsim_cat, density_param = 0.1):
        """
        Input:
        catsim_cat:
            The results array from an instance catalog.

        density_param:
            A float between 0. and 1.0 that determines the fraction of eligible agn objects that become lensed.

        Output:
        updated_catalog:
            A new results array with lens systems added.
        """


        self.catalog = catsim_cat
        # ****** THIS ASSUMES THAT THE ENVIRONMENT VARIABLE OM10_DIR IS SET *******
        lensdb = om10.DB(catalog=os.environ['OM10_DIR']+"/data/qso_mock.fits")
        self.lenscat = lensdb.lenses.copy()
        self.density_param = density_param
        #return

    def sprinkle(self):
        # Define a list that we can write out to a text file
        lenslines = []
        # For each galaxy in the catsim catalog
        updated_catalog = self.catalog.copy()
        print "Running sprinkler. Catalog Length: ", len(self.catalog)
        for rowNum, row in enumerate(self.catalog):
            if rowNum % 1000 == 0:
                print "Gone through ", rowNum, " lines of catalog."
            if not np.isnan(row['galaxyAgn_magNorm']):
                candidates = self.find_lens_candidates(row['galaxyAgn_redshift'])
                pick_value = np.random.uniform()
            # If there aren't any lensed sources at this redshift from OM10 move on the next object
                if ((len(candidates) > 0) and (pick_value <= self.density_param)):
                    # Randomly choose one the lens systems
                    # (can decide with or without replacement)
                    newlens = random.choice(candidates)

                    # Append the lens galaxy
                    # For each image, append the lens images
                    for i in range(newlens['NIMG']):
                        lensrow = row.copy()
                        # XIMG and YIMG are in arcseconds
                        # raPhSim and decPhoSim are in radians
                        #Shift all parts of the lensed object, not just its agn part
                        for lensPart in ['galaxyBulge', 'galaxyDisk', 'galaxyAgn']:
                            lensrow[str(lensPart + '_raJ2000')] += (newlens['XIMG'][i] - newlens['XSRC']) / 3600.0 / 180.0 * np.pi
                            lensrow[str(lensPart + '_decJ2000')] += (newlens['YIMG'][i] - newlens['YSRC']) / 3600.0 / 180.0 * np.pi
                        ###Should this 'mag' be added to all parts? How should we update the ids for the lensed objects?
                        lensrow['galaxyAgn_magNorm'] += newlens['MAG'][i]
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
                    row['galaxyBulge_sedFilename'] = 'Burst.25E09.02Z.spec'
                    row['galaxyBulge_redshift'] = newlens['ZLENS']
                    row['galaxyDisk_redshift'] = newlens['ZLENS']
                    row['galaxyAgn_redshift'] = newlens['ZLENS']
                    row['galaxyBulge_magNorm'] = newlens['APMAG_I'] #Need to convert this to correct band
                    arcsec2rad = 4.84813681109536e-06 #To convert from arcsec to radians for catalog
                    newlens['REFF'] = 1.0 #Hard coded for now. See issue in OM10 github.
                    row['galaxyBulge_majorAxis'] = newlens['REFF'] * arcsec2rad
                    row['galaxyBulge_minorAxis'] = newlens['REFF'] * (1 - newlens['ELLIP']) * arcsec2rad
                    #Convert orientation angle to west of north from east of north by *-1.0 and convert to radians
                    row['galaxyBulge_positionAngle'] = newlens['PHIE']*(-1.0)*np.pi/180.0
                    #Replace original entry with new entry
                    updated_catalog[rowNum] = row

        return updated_catalog

    def find_lens_candidates(self, galz):
        # search the OM10 catalog for all sources +- 0.05 in redshift from the catsim source
        w = np.where(np.abs(self.lenscat['ZSRC'] - galz) <= 0.05)[0]
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
