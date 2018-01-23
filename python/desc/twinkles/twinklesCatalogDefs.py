"""PhoSim Instance Catalog"""
from __future__ import absolute_import, division, print_function
import numpy as np
from lsst.sims.catUtils.exampleCatalogDefinitions import (PhoSimCatalogZPoint,
                                                          PhoSimCatalogPoint,
                                                          PhoSimCatalogSersic2D,
                                                          PhoSimCatalogSN)
from .twinklesVariabilityMixins import VariabilityTwinkles
from lsst.sims.catUtils.mixins import VariabilityAGN, PhotometryGalaxies
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import PhoSimSpecMap as psmp


__all__ = ['TwinklesCatalogZPoint', 'TwinklesPhoSimCatalogSN']


__all__ = ["TwinklesCatalogPoint", "TwinklesCatalogSersic2D",
           "TwinklesCatalogZPoint", "TwinklesCatalogSN"]

twinkles_sn_sed_dir = 'spectra_files'
twinkles_spec_map = psmp
twinkles_spec_map.subdir_map['(^specFile_)'] = twinkles_sn_sed_dir

class TwinklesCatalogPoint(PhoSimCatalogPoint):

    specFileMap = twinkles_spec_map

    column_outputs = ['prefix', 'uniqueId', 'raPhoSim', 'decPhoSim', 'phoSimMagNorm', 'sedFilepath',
                      'redshift', 'gamma1', 'gamma2', 'kappa', 'raOffset', 'decOffset',
                      'spatialmodel', 'internalExtinctionModel',
                      'galacticExtinctionModel', 'galacticAv', 'galacticRv']

class TwinklesCatalogSersic2D(PhoSimCatalogSersic2D):

    specFileMap = twinkles_spec_map

    column_outputs = ['prefix', 'uniqueId', 'raPhoSim', 'decPhoSim', 'phoSimMagNorm', 'sedFilepath',
                      'redshift', 'gamma1', 'gamma2', 'kappa', 'raOffset', 'decOffset',
                      'spatialmodel', 'majorAxis', 'minorAxis', 'positionAngle', 'sindex',
                      'internalExtinctionModel', 'internalAv', 'internalRv',
                      'galacticExtinctionModel', 'galacticAv', 'galacticRv']

class TwinklesCatalogZPoint(PhoSimCatalogZPoint, VariabilityTwinkles, VariabilityAGN):
    """
    PhoSim Instance Catalog Class for strongly lensed (and therefore time-delayed)
    AGN
    """

    specFileMap = twinkles_spec_map

    catalog_type = 'twinkles_catalog_ZPOINT'

    column_outputs = ['prefix', 'uniqueId', 'raPhoSim', 'decPhoSim', 'phoSimMagNorm', 'sedFilepath',
                      'redshift', 'gamma1', 'gamma2', 'kappa', 'raOffset', 'decOffset',
                      'spatialmodel', 'internalExtinctionModel',
                      'galacticExtinctionModel', 'galacticAv', 'galacticRv']

class TwinklesCatalogSN(PhoSimCatalogSN):
    """
    Modification of the PhoSimCatalogSN mixin to provide shorter sedFileNames
    by leaving out the parts of the directory name 
    """
    def get_shorterFileNames(self):
        fnames = self.column_by_name('sedFilepath')
        sep = 'spectra_files/specFile_'
        split_names = []
        for fname in fnames:
            if 'None' not in fname:
                fname = sep + fname.split(sep)[-1] 
            else:
                fname = 'None'
            split_names.append(fname)
        return np.array(split_names)

    # column_outputs = PhoSimCatalogSN.column_outputs
    # column_outputs[PhoSimCatalogSN.column_outputs.index('sedFilepath')] = \
    #    'shorterFileNames'
    column_outputs = ['prefix', 'uniqueId', 'raPhoSim', 'decPhoSim',
                      'phoSimMagNorm', 'shorterFileNames', 'redshift',
                      'gamma1', 'gamma2', 'kappa', 'raOffset', 'decOffset',
                      'spatialmodel', 'internalExtinctionModel',
                      'galacticExtinctionModel', 'galacticAv', 'galacticRv']
    cannot_be_null = ['x0', 't0', 'z', 'shorterFileNames']
