"""
Module describing the Twinkles Sky composed of each astrophysical source.
The module provides access to 
- TwinklesSky : a class describing the astrophysical sources used in Twinkles
- TwinklesPhoSimHeader : A dict which describes the observing conditions as recorded
    in header files of PhoSim instance catalogs.
"""
from __future__ import with_statement, absolute_import, division, print_function
import time
import copy
from lsst.sims.catUtils.baseCatalogModels import (StarObj,
                                                  CepheidStarObj,
                                                  GalaxyBulgeObj,
                                                  GalaxyDiskObj,
                                                  GalaxyAgnObj,
                                                  SNDBObj)
from lsst.sims.catalogs.definitions import CompoundInstanceCatalog
from lsst.sims.catUtils.exampleCatalogDefinitions import\
    (PhoSimCatalogPoint,
     PhoSimCatalogSN,
     DefaultPhoSimHeaderMap,
     DefaultPhoSimInstanceCatalogCols)
from .twinklesCatalogDefs import TwinklesCatalogZPoint, TwinklesCatalogSersic2D
from .sprinkler import sprinklerCompound

__all__ = ['TwinklesPhoSimHeader', 'TwinklesSky']

# sims_catUtils provides a Dictionary called DefaultPhoSimHeaderMap
# We modify that to provide a dictionary where `nsnap` and visit times
# `vistime` have been adjusted to a single effective snap
TwinklesPhoSimHeader = copy.deepcopy(DefaultPhoSimHeaderMap)
TwinklesPhoSimHeader['nsnap'] = 1
TwinklesPhoSimHeader['vistime'] = 30.0

class TwinklesSky(object):
    """
    Class to describe the Twinkles Sky for a particular pointing through its
    obs_metadata. The Twinkles Sky includes
    - stars : (compried of stars, cephids)
    - Galaxies (comprised of GalaxyBulge, GalaxyDisk, GalaxyAgn)
    - Supernovae Type Ia 
    """
    def __init__(self,
                 obs_metadata,
                 brightestStar_gmag_inCat=11.0,
                 brightestGal_gmag_inCat=11.0,
                 availableConnections=None,
                 sntable='TwinkSN',
                 sn_sedfile_prefix='spectra_files/specFile_'):
        """
        Parameters
        ----------
        obs_metadata : instance of `lsst.sims.utils.ObservationMetaData`
            Observational MetaData associated with an OpSim Pointing
        brightestStar_gmag_inCat : optional, float, defaults to 11.0
            brightest star allowed in terms of its g band magnitude in
            'ab' magsys. The reason for this constraint is to keep phosim
            catalog generation times in check.
        brightestGal_gmag_inCat : optional, float, defaults to 11.0
            brightest galaxy allowed in terms of its g band magnitude in
            'ab' magsys. The reason for this constraint is to keep phosim
            catalog generation times in check.
        availableConnections : list of connections, optional, defaults to None
            list of available connections for DBObject
        sntable : string, optional, defaults to `TwinkSN`
            Name of the table on fatboy with the SN parameters desired. 
        sn_sedfile_prefix : string, optional, defaults to `spectra_files/specFile_'
            prefix for sed of the supernovae.
        Attributes
        ----------
        snObj : CatalogDBObj for SN
        available_connections : available connections

        ..notes : 
        """
        # Observation MetaData
        self.obs_metadata = obs_metadata

        # Constraint on the brightest star: 
        self.brightestStar_gmag_inCat = brightestStar_gmag_inCat
        self.brightestStarMag = 'gmag > {}'.format(self.brightestStar_gmag_inCat)

        # Constraint on brightest galaxy
        self.brightestGal_gmag_inCat = brightestGal_gmag_inCat
        self.brightestGalMag = 'g_ab > {}'.format(self.brightestGal_gmag_inCat)

        self.availableConnections = availableConnections

        # Lists of component phosim Instance Catalogs and CatalogDBObjects
        # Stars
        self.compoundStarDBList = [StarObj, CepheidStarObj]
        self.compoundStarICList = [PhoSimCatalogPoint, PhoSimCatalogPoint]

        # Galaxies
        self.compoundGalDBList = [GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj]
        self.compoundGalICList = [TwinklesCatalogSersic2D, TwinklesCatalogSersic2D,
                                  TwinklesCatalogZPoint]

        # SN 
        ## SN catalogDBObject
        if self.availableConnections is None:
            self.availableConnections = list()
            self.snObj = SNDBObj(table=sntable, connection=None)
            self.availableConnections.append(self.snObj.connection)
        else:
            self.snObj = SNDBObj(table=sntable, connection=self.availableConnections[0])
        
        self.sn_sedfile_prefix = sn_sedfile_prefix

    def writePhoSimCatalog(self, fileName):
        """
        write the phosim instance catalogs of stars, galaxies and supernovae in
        the Twinkles Sky to fileName

        Parameters
        ----------
        fileName : string, mandatory
            Name of the file to which the phoSim Instance Catalog will be
            written

        """
        starCat = CompoundInstanceCatalog(self.compoundStarICList,
                                          self.compoundStarDBList,
                                          obs_metadata=self.obs_metadata,
                                          constraint=self.brightestStarMag)

        starCat._active_connections += self.availableConnections # append already open fatboy connections
        starCat.phoSimHeaderMap = TwinklesPhoSimHeader

        t_before_starCat = time.time()
        print("writing starCat ")
        starCat.write_catalog(fileName, chunk_size=10000)
        t_after_starCat = time.time()

        galCat = CompoundInstanceCatalog(self.compoundGalICList,
                                         self.compoundGalDBList,
                                         obs_metadata=self.obs_metadata,
                                         constraint=self.brightestGalMag,
                                         compoundDBclass=sprinklerCompound)

        galCat._active_connections = starCat._active_connections # pass along already open fatboy connections
        t_before_galCat = time.time()
        print("writing galCat")
        galCat.write_catalog(fileName, write_mode='a', chunk_size=10000,
                             write_header=False)

        t_after_galCat = time.time()
        snphosim = PhoSimCatalogSN(db_obj=self.snObj,
                                        obs_metadata=self.obs_metadata)
        ### Set properties
        snphosim.writeSedFile = True
        snphosim.suppressDimSN = True
        snphosim.sn_sedfile_prefix = self.sn_sedfile_prefix
        print("writing sne")
        t_before_snCat = time.time()
        snphosim.write_catalog(fileName, write_header=False,
                               write_mode='a', chunk_size=10000)
        t_after_snCat = time.time()
