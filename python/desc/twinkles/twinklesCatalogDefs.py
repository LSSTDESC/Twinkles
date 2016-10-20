"""Instance Catalog"""
from __future__ import absolute_import, division, print_function
import numpy
from lsst.sims.utils import SpecMap, defaultSpecMap
from lsst.sims.catalogs.definitions import InstanceCatalog
from lsst.sims.utils import arcsecFromRadians
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import PhosimInputBase
from lsst.sims.catUtils.mixins import PhoSimAstrometryGalaxies, \
                                      EBVmixin, VariabilityStars
from .twinklesVariabilityMixins import VariabilityTwinkles


__all__ = ['TwinklesCatalogZPoint', 'TwinklesPhoSimCatalogSN']

class TwinklesCatalogZPoint(PhosimInputBase, PhoSimAstrometryGalaxies, EBVmixin, VariabilityTwinkles):

    catalog_type = 'twinkles_catalog_ZPOINT'
    column_outputs = ['prefix', 'uniqueId','raPhoSim','decPhoSim','phoSimMagNorm','sedFilepath',
                      'redshift','shear1','shear2','kappa','raOffset','decOffset',
                      'spatialmodel','galacticExtinctionModel','galacticAv','galacticRv',
                      'internalExtinctionModel']
    default_columns = [('shear1', 0., float), ('shear2', 0., float), ('kappa', 0., float),
                       ('raOffset', 0., float), ('decOffset', 0., float), ('spatialmodel', 'ZPOINT', (str, 6)),
                       ('galacticExtinctionModel', 'CCM', (str,3)),
                       ('galacticAv', 0.1, float),
                       ('galacticRv', 3.1, float),
                       ('internalExtinctionModel', 'none', (str,4))]
    default_formats = {'S':'%s', 'f':'%.9g', 'i':'%i'}
    delimiter = " "
    spatialModel = "point"
    transformations = {'raPhoSim':numpy.degrees, 'decPhoSim':numpy.degrees}

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
