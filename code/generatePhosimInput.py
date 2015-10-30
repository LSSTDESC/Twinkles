"""
This file shows how to generate a phoSim input catalog named phoSim_example.txt

"""


from __future__ import with_statement
import os
import eups
import numpy
from lsst.sims.catalogs.measures.instance import InstanceCatalog
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogZPoint

from lsst.sims.catUtils.baseCatalogModels import *

opsimDB = os.path.join('.','enigma_1189_sqlite.db')

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
    doHeader= True
    for starName in starObjNames:
        print starName
        while True:
            try:
                stars = CatalogDBObject.from_objid(starName)
                star_phoSim=PhoSimCatalogPoint(stars,obs_metadata=obs_metadata) #the class for phoSim input files
                break
            except RuntimeError:
                continue
                                                                    #containing point sources
        if (doHeader):
            with open(filename,"w") as fh:
                star_phoSim.write_header(fh)
            doHeader = False

        #below, write_header=False prevents the code from overwriting the header just written
        #write_mode = 'a' allows the code to append the new objects to the output file, rather
        #than overwriting the file for each different class of object.
        star_phoSim.write_catalog(filename,write_mode='a',write_header=False,chunk_size=20000)


    #now append a bunch of objects with 2D sersic profiles to our output file
    while True:
        try:
            gals = CatalogDBObject.from_objid('galaxyBulge')
            galaxy_phoSim = PhoSimCatalogSersic2D(gals, obs_metadata=obs_metadata)
            break
        except RuntimeError:
            continue
    galaxy_phoSim.write_catalog(filename,write_mode='a',write_header=False,chunk_size=20000)
    print 'bulge'

    while True:
        try:
            gals = CatalogDBObject.from_objid('galaxyDisk')
            galaxy_phoSim = PhoSimCatalogSersic2D(gals, obs_metadata=obs_metadata)
            break
        except RuntimeError:
            continue
    galaxy_phoSim.write_catalog(filename,write_mode='a',write_header=False,chunk_size=20000)
    print 'disk'


    #PhoSimCatalogZPoint is the phoSim input class for extragalactic point sources (there will be no parallax
    #or proper motion)
    while True:
        try:
            gals = CatalogDBObject.from_objid('galaxyAgn')
            galaxy_phoSim = PhoSimCatalogZPoint(gals, obs_metadata=obs_metadata)
            break
        except RuntimeError:
            continue
    galaxy_phoSim.write_catalog(filename,write_mode='a',write_header=False,chunk_size=20000)
    print 'agn'
