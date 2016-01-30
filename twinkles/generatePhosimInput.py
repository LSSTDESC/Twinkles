# -*- coding: utf-8 -*-
"""
Generate phoSim input catalog that has sprinkled lens systems inside.
"""

from __future__ import with_statement
import os
import numpy
from lsst.sims.catalogs.measures.instance import InstanceCatalog, CompoundInstanceCatalog
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catalogs.generation.db.dbConnection import DBConnection
from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject, StarObj, MsStarObj, \
        BhbStarObj, WdStarObj, RRLyStarObj, CepheidStarObj, GalaxyBulgeObj, GalaxyDiskObj, \
        GalaxyAgnObj
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D
from sprinkler import sprinklerCompound
from twinklesCatalogDefs import TwinklesCatalogZPoint

def generatePhosimInput():

    opsimDB = os.path.join('/Users/Bryce/Desktop/','enigma_1189_sqlite.db')

    #you need to provide ObservationMetaDataGenerator with the connection
    #string to an OpSim output database.  This is the connection string
    #to a test database that comes when you install CatSim.
    generator = ObservationMetaDataGenerator(database=opsimDB, driver='sqlite')
    obsMetaDataResults = generator.getObservationMetaData(fieldRA=(53, 54), fieldDec=(-29, -27), boundLength=0.3)

    rVisits = []
    for md in obsMetaDataResults:
        if md.bandpass == 'r':
            rVisits.append(md)

    starObjNames = ['msstars', 'bhbstars', 'wdstars', 'rrlystars', 'cepheidstars']

    for obs_metadata in rVisits[:10]:
        filename = "phosim_input_%s.txt"%(obs_metadata.phoSimMetaData['Opsim_obshistid'][0])
        obs_metadata.phoSimMetaData['SIM_NSNAP'] = (1, numpy.dtype(int))
        obs_metadata.phoSimMetaData['SIM_VISTIME'] = (30, numpy.dtype(float))
        print 'Starting Visit: ', obs_metadata.phoSimMetaData['Opsim_obshistid'][0]

        compoundDBList = [MsStarObj, BhbStarObj, WdStarObj, RRLyStarObj, CepheidStarObj, GalaxyBulgeObj,
                          GalaxyDiskObj, GalaxyAgnObj]
        compoundICList = [PhoSimCatalogPoint, PhoSimCatalogPoint, PhoSimCatalogPoint, PhoSimCatalogPoint,
                          PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogSersic2D, TwinklesCatalogZPoint]

        while True:
            try:
                totalCat = CompoundInstanceCatalog(compoundICList, compoundDBList, obs_metadata=obs_metadata,
                                                   compoundDBclass=sprinklerCompound)
                break
            except RuntimeError:
                continue

        totalCat.write_catalog(filename)
        print "Finished Writing Visit: ", obs_metadata.phoSimMetaData['Opsim_obshistid'][0]

if __name__ == "__main__":
    generatePhosimInput()
