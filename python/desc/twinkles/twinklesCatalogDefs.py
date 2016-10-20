"""PhoSim Instance Catalog"""
from __future__ import absolute_import, division, print_function
from lsst.sims.catUtils.exampleCatalogDefinitions import PhoSimCatalogZPoint
from .twinklesVariabilityMixins import VariabilityTwinkles
__all__ = ['TwinklesCatalogZPoint', 'TwinklesPhoSimCatalogSN']

class TwinklesCatalogZPoint(PhosimInputBase, PhoSimAstrometryGalaxies, EBVmixin, VariabilityTwinkles):

class TwinklesCatalogZPoint(PhoSimCatalogZPoint, VariabilityTwinkles):
    """
    PhoSim Instance Catalog Class for strongly lensed (and therefore time-delayed)
    AGN
    """
    catalog_type = 'twinkles_catalog_ZPOINT'

class TwinklesPhoSimCatalogSN(PhoSimCatalogSN):
    """
    Modification of the PhoSimCatalogSN mixin to provide shorter sedFileNames
    by leaving out the parts of the directory name 
    """
    def get_shorterFileNames(self):
        fnames = self.column_by_name('sedFilepath')
        sep = 'spectra_files/specFile_'
        split_names = list(sep + fname.split(sep)[-1] for fname in fnames)
        return split_names

    self.column_outputs[self.column_outputs.index('sedFilepath')] = \
            shorterFileNames
