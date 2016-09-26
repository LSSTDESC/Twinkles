"""PhoSim Instance Catalog"""
from __future__ import absolute_import, division, print_function
from lsst.sims.catUtils.exampleCatalogDefinitions import PhoSimCatalogZPoint
from twinklesVariabilityMixins import VariabilityTwinkles

class TwinklesCatalogZPoint(PhoSimCatalogZPoint, VariabilityTwinkles):
    """
    PhoSim Instance Catalog Class for strongly lensed (and therefore time-delayed)
    AGN
    """

    catalog_type = 'twinkles_catalog_ZPOINT'
