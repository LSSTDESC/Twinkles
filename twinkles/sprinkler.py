'''
Created on Feb 6, 2015

@author: cmccully
'''


class sprinkler():
    def __init__(self, catsim_cat):
        return

    def sprinkle(self):
        # For each galaxy in the catsim catalog
        self.find_lens()
        # If there aren't any lensed sources at this redshift from OM10 move on the next object
        return

    def find_lens(self):
        # search the OM10 catalog for all sources +- 0.05 in redshift from the catsim source
        # Randomly choose one the lens systems (can decide with or without replacement)
        return

    def update_catsim(self):
        # Remove the catsim object
        # Add lensed images to the catsim given source brightness and magnifications
        # Add lens galaxy to catsim
        return

    def catsim_to_phosim(self):
        # Pass this catsim to phosim to make images
        return
