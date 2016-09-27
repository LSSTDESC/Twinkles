"""
Class describing the Twinkles Sky
"""
from __future__ import with_statement, absolute_import, division, print_function
import time
import logging
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
     PhoSimCatalogSersic2D,
     PhoSimCatalogSN,
     DefaultPhoSimHeaderMap,
     DefaultPhoSimInstanceCatalogCols)
from twinklesCatalogDefs import TwinklesCatalogZPoint
from sprinkler import sprinklerCompound

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
                 sn_sedfile_prefix='spectra_files/spec'):
        """
        Parameters
        ----------
        obs_metadata : instance of `lsst.sims.utils.ObservationMetaData`
            Observational MetaData associated with an OpSim Pointing
        brightestStar_gmag_inCat : optional, defaults to 11.0
            brightest star allowed in terms of its magnitude in g band
            The reason for this constraint is to keep phosim catalog generation
            times in check.
        sntable : string, optional, defaults to `TwinkSN`
            Name of the table on fatboy with the SN parameters desired. 

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

        if availableConnections is None:
            self.availableConnections = list()
        else:
            self.availableConnections = availableConnections

        # SN catalogDBObject
        self.snObj = SNDBObj(table=sntable)
        
        # Lists of component phosim Instance Catalogs and CatalogDBObjects
        
        # Stars
        self.compoundStarDBList = [StarObj, CepheidStarObj]
        self.compoundStarICList = [PhoSimCatalogPoint, PhoSimCatalogPoint]

        # Galaxies
        self.compoundGalDBList = [GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj]
        self.compoundGalICList = [PhoSimCatalogSersic2D, PhoSimCatalogSersic2D,
                                  TwinklesCatalogZPoint]

        self.sn_sedfile_prefix = sn_sedfile_prefix

    def writePhoSimCatalog(self, fileName):
        # PhoSim Instance Catalogs
        
        ## SN 
        print ('self.availableConnections', self.availableConnections)
        # Add the connection to the list of connections
        self.availableConnections.append(self.snObj.connection)
        
        snphosim = PhoSimCatalogSN(db_obj=self.snObj,
                                        obs_metadata=self.obs_metadata)
        ### Set properties
        snphosim.writeSedFile = True
        snphosim.suppressDimSN = True
        snphosim.sn_sedfile_prefix = self.sn_sedfile_prefix

        # Stars
        print('write Star Catalog')
        starCat = CompoundInstanceCatalog(self.compoundStarICList,
                                          self.compoundStarDBList,
                                          obs_metadata=self.obs_metadata,
                                          constraint=self.brightestStarMag,
                                          compoundDBclass=sprinklerCompound)
        ## Now there is already an active connection, use it
	starCat._active_connections = self.availableConnections
	starCat.phoSimHeaderMap = TwinklesPhoSimHeader
        starCat.write_catalog(fileName, chunk_size=10000)

        print('write Gal Catalog')
        galCat = CompoundInstanceCatalog(self.compoundGalICList,
                                         self.compoundGalDBList,
                                         obs_metadata=self.obs_metadata,
                                         compoundDBclass=sprinklerCompound)

        galCat._active_connections = self.availableConnections
        galCat.write_catalog(fileName, write_mode='a',
                                     write_header=False)

        print('write SN Catalog')
        snphosim.write_catalog(filename, write_header=False,
                               write_mode='a')

