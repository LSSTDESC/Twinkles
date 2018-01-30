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
from lsst.sims.catalogs.definitions import CompoundInstanceCatalog
from lsst.sims.catalogs.db import CompoundCatalogDBObject


#__all__ = ['TwinklesCatalogZPoint', 'TwinklesPhoSimCatalogSN']


__all__ = ["TwinklesCatalogPoint", "TwinklesCatalogSersic2D",
           "TwinklesCatalogZPoint", "TwinklesCatalogSN", "TwinklesCompoundInstanceCatalog"]

twinkles_sn_sed_dir = 'spectra_files'
twinkles_spec_map = psmp
twinkles_spec_map.subdir_map['(^specFile_)'] = twinkles_sn_sed_dir

class TwinklesCatalogPoint(PhoSimCatalogPoint):

    specFileMap = twinkles_spec_map

class TwinklesCatalogSersic2D(PhoSimCatalogSersic2D):

    specFileMap = twinkles_spec_map

class TwinklesCatalogZPoint(PhoSimCatalogZPoint, VariabilityTwinkles, VariabilityAGN):
    """
    PhoSim Instance Catalog Class for strongly lensed (and therefore time-delayed)
    AGN
    """

    specFileMap = twinkles_spec_map

    catalog_type = 'twinkles_catalog_ZPOINT'

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

class TwinklesCompoundInstanceCatalog(CompoundInstanceCatalog):

    use_spec_map = twinkles_spec_map

    def write_catalog(self, filename, chunk_size=None, write_header=True, write_mode='w'):
        """
        Write the stored list of InstanceCatalogs to a single ASCII output catalog.
        @param [in] filename is the name of the file to be written
        @param [in] chunk_size is an optional parameter telling the CompoundInstanceCatalog
        to query the database in manageable chunks (in case returning the whole catalog
        takes too much memory)
        @param [in] write_header a boolean specifying whether or not to add a header
        to the output catalog (Note: only one header will be written; there will not be
        a header for each InstanceCatalog in the CompoundInstanceCatalog; default True)
        @param [in] write_mode is 'w' if you want to overwrite the output file or
        'a' if you want to append to an existing output file (default: 'w')
        """

        instantiated_ic_list = [None]*len(self._ic_list)

        # first, loop over all of the InstanceCatalog and CatalogDBObject classes, pre-processing
        # them (i.e. verifying that they have access to all of the columns they need)
        for ix, (icClass, dboClass) in enumerate(zip(self._ic_list, self._dbo_list)):
            dbo = dboClass()

            ic = icClass(dbo, obs_metadata=self._obs_metadata)

            # assign all non-private member variables of the CompoundInstanceCatalog
            # to the instantiated InstanceCatalogs
            for kk in self.__dict__:
                if kk[0] != '_' and not hasattr(self.__dict__[kk], '__call__'):
                    setattr(ic, kk, self.__dict__[kk])

            for kk in self.__class__.__dict__:
                if kk[0] != '_' and not hasattr(self.__class__.__dict__[kk], '__call__'):
                    setattr(ic, kk, self.__class__.__dict__[kk])

            ic._write_pre_process()
            instantiated_ic_list[ix] = ic

        for row in self._dbObjectGroupList:
            if len(row) == 1:
                ic = instantiated_ic_list[row[0]]
                ic._query_and_write(filename, chunk_size=chunk_size,
                                    write_header=write_header, write_mode=write_mode,
                                    obs_metadata=self._obs_metadata,
                                    constraint=self._constraint)
                write_mode = 'a'
                write_header = False

        default_compound_dbo = None
        if self._compoundDBclass is not None:
            if not hasattr(self._compoundDBclass, '__getitem__'):
                default_compound_dbo = CompoundCatalogDBObject
            else:
                for dbo in self._compoundDBclass:
                    if dbo._table_restriction is None:
                        default_compound_dbo = dbo
                        break

                if default_compound_dbo is None:
                    default_compound_dbo is CompoundCatalogDBObject

        for row in self._dbObjectGroupList:
            if len(row) > 1:
                dbObjClassList = [self._dbo_list[ix] for ix in row]
                catList = [instantiated_ic_list[ix] for ix in row]
                for cat in catList:
                    cat._pre_screen = True

                if self._compoundDBclass is None:
                    compound_dbo = CompoundCatalogDBObject(dbObjClassList)
                elif not hasattr(self._compoundDBclass, '__getitem__'):
                    # if self._compoundDBclass is not a list
                    try:
                        compound_dbo = self._compoundDBclass(dbObjClassList)
                    except:
                        compound_dbo = default_compound_dbo(dbObjClassList)
                else:
                    compound_dbo = None
                    for candidate in self._compoundDBclass:
                        use_it = True
                        if False in [candidate._table_restriction is not None and
                                     dbo.tableid in candidate._table_restriction
                                     for dbo in dbObjClassList]:

                            use_it = False

                        if use_it:
                            compound_dbo = candidate(dbObjClassList)
                            break

                    if compound_dbo is None:
                        compound_dbo = default_compound_dbo(dbObjClassList)

                compound_dbo.mjd = self._obs_metadata.mjd.TAI
                compound_dbo.specFileMap = self.use_spec_map

                self._write_compound(catList, compound_dbo, filename,
                                     chunk_size=chunk_size, write_header=write_header,
                                     write_mode=write_mode)
                write_mode = 'a'
                write_header = False
