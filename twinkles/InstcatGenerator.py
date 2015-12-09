"""
Based upon examples by Scott Daniel (scottvalscott@gmail.com) found here:
https://stash.lsstcorp.org/projects/SIM/repos/sims_catutils/browse/python/lsst/sims/
        catUtils/exampleCatalogDefinitions/phoSimCatalogExamples.py
"""

from lsst.sims.catalogs.measures.instance import CompoundInstanceCatalog
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogZPoint
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
#from sprinkler import sprinklerCompound

class InstcatGenerator(object):
    _starObjNames = ['msstars', 'bhbstars', 'wdstars', 'rrlystars',
                     'cepheidstars']
    def __init__(self, opsim_db, fieldRA, fieldDec, boundLength=0.3):
        gen = ObservationMetaDataGenerator(database=opsim_db,
                                           driver='sqlite')
        self.obs_md_results = gen.getObservationMetaData(fieldRA=fieldRA, 
                                                         fieldDec=fieldDec,
                                                         boundLength=boundLength)

    def find_visits(self, bandpass, nmax=None):
        visits = []
        for obs_metadata in self.obs_md_results:
            if nmax is not None and len(visits) == nmax:
                break
            if obs_metadata.bandpass == bandpass:
                visits.append(obs_metadata)
        return visits

    def __call__(self, outfile, obs_metadata):
        catalogs = []

        # Add Instance Catalogs for phoSim stars.
        for starName in self._starObjNames:
            starDBObj = CatalogDBObject.from_objid(starName)
            catalogs.append(PhoSimCatalogPoint(starDBObj, 
                                               obs_metadata=obs_metadata))

        # Add phosim Galaxy Instance Catalogs to compound Instance Catalog.
        galsBulge = CatalogDBObject.from_objid('galaxyBulge')
        catalogs.append(PhoSimCatalogSersic2D(galsBulge,
                                              obs_metadata=obs_metadata))
        galsDisk = CatalogDBObject.from_objid('galaxyDisk')
        catalogs.append(PhoSimCatalogSersic2D(galsDisk,
                                              obs_metadata=obs_metadata))
        galsAGN = CatalogDBObject.from_objid('galaxyAgn')
        catalogs.append(PhoSimCatalogZPoint(galsAGN,
                                            obs_metadata=obs_metadata))

        # Write the catalogs to the output file one at a time.
        write_header = True
        for catalog in catalogs:
            catalog.write_catalog(outfile, write_mode='a',
                                  write_header=write_header,
                                  chunk_size=20000)
            write_header = False

if __name__ == '__main__':
    import os
    import pickle
    import time

    # This following is a deep drilling field ID for enigma_1189, but
    # fieldID is not one of the selection options in
    # getObservationMetaData(...), so we need to continue using
    # fieldRA, fieldDec
    fieldID = 1427
    
    fieldRA = (53, 54)
    fieldDec = (-29, -27)

    opsim_db = '/nfs/slac/g/ki/ki18/jchiang/DESC/Twinkles/work/enigma_1189_sqlite.db'
    pickle_file = 'instcat_generator_enigma_1189_%(fieldID)i.pickle' % locals()

    t0 = time.time()
    if not os.path.isfile(pickle_file):
        print "Extracting visits from %s:" % os.path.basename(opsim_db)
        generator = InstcatGenerator(opsim_db, fieldRA, fieldDec)
        pickle.dump(generator, open(pickle_file, 'w'))
        print "execution time:", time.time() - t0
    else:
        print "Loading pickle file with visits:", pickle_file
        generator = pickle.load(open(pickle_file))
        print "execution time:", time.time() - t0

    nmax = 1
    for bandpass in 'ugrizy':
        print "band pass:", bandpass
        visits = generator.find_visits(bandpass, nmax=nmax)
        for visit in visits:
            obshistid = visit.phoSimMetaData['Opsim_obshistid'][0]
            outfile = 'phosim_input_%s_%07i.txt' % (bandpass, obshistid)
            print outfile
            generator(outfile, visit)
