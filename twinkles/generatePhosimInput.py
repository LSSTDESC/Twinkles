# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 14:29:08 2015

@author: Bryce Kalmbach (jbkalmbach@gmail.com)
Based upon examples by Scott Daniel (scottvalscott@gmail.com) found here:
https://stash.lsstcorp.org/projects/SIM/repos/sims_catutils/browse/python/lsst/sims/
        catUtils/exampleCatalogDefinitions/phoSimCatalogExamples.py
"""

from __future__ import with_statement
from lsst.sims.catalogs.measures.instance import InstanceCatalog, CompoundInstanceCatalog
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogZPoint
from sprinkler import sprinklerCompound

def generatePhosimInput():

    starObjNames = ['msstars', 'bhbstars', 'wdstars', 'rrlystars', 'cepheidstars']

    obsMD = OpSim3_61DBObject()
    obs_metadata = obsMD.getObservationMetaData(88625744, 0.05, makeCircBounds = True)

    compoundICList = []

    #Add Instance Catalogs for phoSim stars
    for starName in starObjNames:
        starDBObj = CatalogDBObject.from_objid(starName)
        compoundICList.append(PhoSimCatalogPoint(starDBObj, obs_metadata=obs_metadata))

    #Add phosim Galaxy Instance Catalogs to compound Instance Catalog
    galsBulge = CatalogDBObject.from_objid('galaxyBulge')
    compoundICList.append(PhoSimCatalogSersic2D(galsBulge, obs_metadata=obs_metadata))
    galsDisk = CatalogDBObject.from_objid('galaxyDisk')
    compoundICList.append(PhoSimCatalogSersic2D(galsDisk, obs_metadata=obs_metadata))
    galsAGN = CatalogDBObject.from_objid('galaxyAgn')
    compoundICList.append(PhoSimCatalogZPoint(galsAGN, obs_metadata=obs_metadata))

    totalCat = CompoundInstanceCatalog(compoundICList, obs_metadata=obs_metadata, compoundDBclass=sprinklerCompound)
    totalCat.write_catalog("phosim_example.txt")

if __name__ == "__main__":
    generatePhosimInput()
