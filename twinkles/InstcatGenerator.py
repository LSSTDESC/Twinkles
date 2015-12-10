"""
Based upon examples by Scott Daniel (scottvalscott@gmail.com) found here:
https://stash.lsstcorp.org/projects/SIM/repos/sims_catutils/browse/python/lsst/sims/
        catUtils/exampleCatalogDefinitions/phoSimCatalogExamples.py
"""
import os
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogZPoint
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
#from sprinkler import sprinklerCompound

class InstcatGenerator(object):
    def __init__(self, opsim_db, fieldRA, fieldDec, boundLength=0.3):
        starObjNames = ['msstars', 'bhbstars', 'wdstars', 'rrlystars',
                        'cepheidstars']
        self._phosimCatDefs = dict([(objid, PhoSimCatalogPoint) for objid 
                                    in starObjNames])
        self._phosimCatDefs.update(dict(galaxyBulge=PhoSimCatalogSersic2D,
                                        galaxyDisk=PhoSimCatalogSersic2D,
                                        galaxyAgn=PhoSimCatalogZPoint))
        gen = ObservationMetaDataGenerator(database=opsim_db, driver='sqlite')
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
    def _processDbObject(self, objid, outfile, obs_md, write_header=False):
        while True:
            try:
                db_obj = CatalogDBObject.from_objid(objid)
                inst_cat = self._phosimCatDefs[objid](db_obj,
                                                      obs_metadata=obs_md)
                break
            except RuntimeError:
                continue
        inst_cat.write_catalog(outfile, write_mode='a',
                               write_header=write_header, chunk_size=20000)
    def write_catalog(self, outfile, obs_metadata, clobber=True):
        if clobber and os.path.isfile(outfile):
            os.remove(outfile)
        write_header = True
        for objid in self._phosimCatDefs:
            self._processDbObject(objid, outfile, obs_metadata,
                                  write_header=write_header)
            write_header = False

if __name__ == '__main__':
    import os
    import pickle
    import time

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

    nmax = 20
    for bandpass in 'ugrizy':
        print "band pass:", bandpass
        visits = generator.find_visits(bandpass, nmax=nmax)
        for i, visit in enumerate(visits):
            obshistid = visit.phoSimMetaData['Opsim_obshistid'][0]
            outfile = 'phosim_input_%s_%07i.txt' % (bandpass, obshistid)
            print i, outfile
            generator.write_catalog(outfile, visit)
