"""
Class describing the Twinkles Sky
"""
import time
import logging
from lsst.sims.catUtils.baseCatalogModels import (StarObj,
                                                  CepheidStarObj,
                                                  GalaxyBulgeObj,
                                                  GalaxyDiskObj,
                                                  GalaxyAgnObj,
                                                  SNDBObj)

from lsst.sims.catUtils.exampleCatalogDefinitions import\
    (PhoSimCatalogPoint,
     PhoSimCatalogSersic2D,
     PhoSimCatalogSN,
     DefaultPhoSimHeaderMap,
     DefaultPhoSimInstanceCatalogCols)

from sprinkler import sprinklerCompound
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
                 sntable='TwinkSN'):
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
        # Constrain on the brightest star 
        self.brightestStar_gmag_inCat = brightestStar_gmag_inCat
        self.brightestStarMag = 'g_ab > {}'.format(self.brightestStar_gmag_inCat)

        # SN catalogDBObject
        self.snObj = SNDBObj(table=sntable)
        self.available_connections = [snObj.connection] # an list of open connections to fatboy
        self.compoundStarDBList = [StarObj, CepheidStarObj]
        self.compoundGalDBList = [GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj]
        
        # Lists of phosim Instance Catalogs
        self.compoundStarICList = [PhoSimCatalogPoint, PhoSimCatalogPoint]
        self.compoundGalICList = [PhoSimCatalogSersic2D, PhoSimCatalogSersic2D,
                             TwinklesCatalogZPoint]

        self.snphosim = PhoSimCatalogSN(db_obj=self.snObj,
                                   obs_metadata=obs_metadata)
        self.availableConnections = list()

    def phosimStarCatalog(self):

        starCat = CompoundInstanceCatalog(sellf.compoundStarICList,
                                          self.compoundStarDBList,
                                          obs_metadata=self.obs_metadata,
                                          constraint=self.brightestStarMag,
                                          compoundDBclass=sprinklerCompound)
	starCat._active_connections = self.availableConnections
	starCat.phoSimHeaderMap = DefaultPhoSimHeaderMap

    def writePhoSimStarCatalog(fileName):

