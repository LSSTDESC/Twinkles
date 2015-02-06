'''
Created on Feb 6, 2015

@author: cmccully
'''
import om10
import numpy as np
from lsst.sims.catalogs.generation.db import CatalogDBObject


class sprinklerdb(CatalogDBObject):
    def _final_pass(self, results):
        return results


class sprinkler():
    def __init__(self, catsim_cat):
        self.catalog = catsim_cat
        # ****** THIS ASSUMES THAT THE ENVIRONMENT VARIABLE OM10_DIR IS SET *******
        lensdb = om10.DB(catalog="data/qso_mock.fits")
        self.lenscat = lensdb.lenses.copy()
        return

    def sprinkle(self):
        # For each galaxy in the catsim catalog
        self.find_lens_candidates()
        # If there aren't any lensed sources at this redshift from OM10 move on the next object
        # Randomly choose one the lens systems (can decide with or without replacement)
        return

    def find_lens_candidates(self, galz):
        # search the OM10 catalog for all sources +- 0.05 in redshift from the catsim source
        w = np.where(np.abs(self.lenses['ZSRC'] - galz) <= 0.05)[0]
        lens_candidates = self.lenses[w]

        return lens_candidates

    def update_catsim(self):
        # Remove the catsim object
        # Add lensed images to the catsim given source brightness and magnifications
        # Add lens galaxy to catsim
        return

    def catsim_to_phosim(self):
        # Pass this catsim to phosim to make images
        return
