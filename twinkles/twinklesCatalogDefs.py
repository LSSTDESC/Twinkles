"""Instance Catalog"""
import numpy
from lsst.sims.utils import SpecMap, defaultSpecMap
from lsst.sims.catalogs.measures.instance import InstanceCatalog
from lsst.sims.utils import arcsecFromRadians
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import PhosimInputBase
from lsst.sims.catUtils.mixins import AstrometryStars, AstrometryGalaxies, \
                                      EBVmixin, VariabilityStars
from twinklesVariabilityMixins import VariabilityTwinkles

class TwinklesCatalogZPoint(PhosimInputBase, AstrometryGalaxies, EBVmixin, VariabilityTwinkles):

    catalog_type = 'twinkles_catalog_ZPOINT'
    column_outputs = ['prefix', 'uniqueId','raPhoSim','decPhoSim','phoSimMagNorm','sedFilepath',
                      'redshift','shear1','shear2','kappa','raOffset','decOffset',
                      'spatialmodel','galacticExtinctionModel','galacticAv','galacticRv',
                      'internalExtinctionModel']
    default_columns = [('shear1', 0., float), ('shear2', 0., float), ('kappa', 0., float),
                       ('raOffset', 0., float), ('decOffset', 0., float), ('spatialmodel', 'ZPOINT', (str, 6)),
                       ('galacticExtinctionModel', 'CCM', (str,3)),
                       ('galacticAv', 0.1, float),
                       ('internalExtinctionModel', 'none', (str,4))]
    default_formats = {'S':'%s', 'f':'%.9g', 'i':'%i'}
    delimiter = " "
    spatialModel = "point"
    transformations = {'raPhoSim':numpy.degrees, 'decPhoSim':numpy.degrees}

    def get_phoSimMagNorm(self):
            """
            This getter returns the magnitude normalization expected by PhoSim (the magnitude at
            500 nm).
            To account for variability, the getter adds the delta_lsst_x column from the Variability
            mixin where 'x' is the bandpass defined by self.observation_metadata.bandpass (assuming
            that self.observation_metadata.bandpass is not list-like; if it is list-like, then no
            variability is added to the magNorm value).
            Redshift is currently ignored.  That may or may  not be appropriate.  This requires
            further investigation into the behavior of PhoSim.
            """

            magNorm = self.column_by_name('magNorm')
            varName = None
            if self.obs_metadata is not None:
                if self.obs_metadata.bandpass is not None:
                    if not hasattr(self.obs_metadata.bandpass, '__iter__'):
                        varName = 'delta_lsst_' + self.obs_metadata.bandpass

            if varName is not None and varName in self._all_available_columns:
                magNorm_out = magNorm + self.column_by_name(varName)

            return magNorm_out

    def _query_and_write(self, filename, chunk_size=None, write_header=True,
                         write_mode='w', obs_metadata=None, constraint=None):
        """
        This method queries db_obj, and then writes the resulting recarray
        to the specified ASCII output file.
        @param [in] filename is the name of the ASCII file to be written
        @param [in] obs_metadata is an ObservationMetaData instantiation
        characterizing the telescope pointing (optional)
        @param [in] constraint is an optional SQL constraint applied to the database query.
        @param [in] chunk_size is an optional parameter telling the CompoundInstanceCatalog
        to query the database in manageable chunks (in case returning the whole catalog
        takes too much memory)
        @param [in] write_header a boolean specifying whether or not to add a header
        to the output catalog (default True)
        @param [in] write_mode is 'w' if you want to overwrite the output file or
        'a' if you want to append to an existing output file (default: 'w')
        """


        file_handle = open(filename, write_mode)
        if write_header:
            self.write_header(file_handle)

        query_result = self.db_obj.query_columns(colnames=self._active_columns,
                                                 obs_metadata=obs_metadata,
                                                 constraint=constraint,
                                                 chunk_size=chunk_size)

        for chunk in query_result:
            print chunk.dtype.fields
            self._write_recarray(chunk, file_handle)

        file_handle.close()
