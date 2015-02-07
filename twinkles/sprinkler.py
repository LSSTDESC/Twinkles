'''
Created on Feb 6, 2015

@author: cmccully
'''
import om10
import numpy as np
from lsst.sims.catUtils.baseCatalogModels import GalaxyAgnObj, GalaxyBulgeObj
import random
import os


class sprinklerAGN(GalaxyAgnObj):
    objid = 'sprinklerAGN'
    objectTypeID = 1024

    def _final_pass(self, results):
        sp = sprinkler(results)
        results = sp.sprinkle()
        return results


class sprinklerLens(GalaxyBulgeObj):
    objid = 'sprinklerLens'
    objectTypeID = 1025

    def _final_pass(self, results):
        # Find the first non nan magNorm
        for row in results:
            if not np.isnan(row['magNorm']):
                template_row = row.copy()
                break
        # Read in the lens data file
        lensdata = np.genfromtxt('lens.dat')
        # For each lens
        for row in lensdata:
        # create a new row based on the lens data
            newrow = template_row.copy()
            newrow['redshift'] = row[2]
        # Fix ME
        if row[-1] == 0:
            reff = 0.5
        else:
            reff  = row[-1]
            newrow['minorAxis']
            newrow['majorAxis']
            newrow['positionAngle']
            newrow['raJ2000']
            newrow['decJ2000']
            #This is just normalized to I which should be fixed
            newrow['magNorm']
            newrow['sedFilename']
            import pdb; pdb.set_trace()
        # Append the row to the results
        
        return results


class sprinkler():
    def __init__(self, catsim_cat):
        self.catalog = catsim_cat
        # ****** THIS ASSUMES THAT THE ENVIRONMENT VARIABLE OM10_DIR IS SET *******
        lensdb = om10.DB(catalog=os.environ['OM10_DIR']+"/data/qso_mock.fits")
        self.lenscat = lensdb.lenses.copy()
        return

    def sprinkle(self):
        # Define a list that we can write out to a text file
        lenslines = []
        # For each galaxy in the catsim catalog
        updated_catalog = self.catalog.copy()
        for row in self.catalog:
            if not np.isnan(row['magNorm']):
                candidates = self.find_lens_candidates(row['redshift'])
            # If there aren't any lensed sources at this redshift from OM10 move on the next object
                if len(candidates) > 0:
                    # Randomly choose one the lens systems
                    # (can decide with or without replacement)
                    newlens = random.choice(candidates)

                    # Append the lens galaxy
                    # For each image, append the lens images
                    for i in range(newlens['NIMG']):
                        lensrow = row.copy()
                        # XIMG and YIMG are in arcseconds
                        # raPhSim and decPhoSim are in radians
                        print lensrow['raJ2000']
                        print (newlens['XIMG'][i] - newlens['XSRC']) / 3600.0 / 180.0 * np.pi
                        lensrow['raJ2000'] += (newlens['XIMG'][i] - newlens['XSRC']) / 3600.0 / 180.0 * np.pi
                        lensrow['decJ2000'] += (newlens['YIMG'][i] - newlens['YSRC']) / 3600.0 / 180.0 * np.pi
                        lensrow['magNorm'] += newlens['MAG'][i]
                        updated_catalog = np.append(updated_catalog, lensrow)
                        
                        #Write out info about the lens galaxy to a text file
                        lenslines.append('%f %f %f %f %f %f %f\n'%(lensrow['raJ2000'], lensrow['decJ2000'], newlens['ZSRC'], newlens['APMAG_I'],
                                         newlens['ELLIP'], newlens['PHIE'], newlens['REFF']))

                    # TODO: Maybe Lens original AGN or delete original source
        f = open('lens.dat','w')
        f.writelines(lenslines)
        f.close()
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
