"""
Based upon examples by Scott Daniel (scottvalscott@gmail.com) found here:
https://stash.lsstcorp.org/projects/SIM/repos/sims_catutils/browse/python/lsst/sims/
        catUtils/exampleCatalogDefinitions/phoSimCatalogExamples.py
"""
from __future__ import absolute_import, print_function
from builtins import object, dict
import os
from collections import OrderedDict
import pickle
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catalogs.measures.instance import CompoundInstanceCatalog
from lsst.sims.catUtils.baseCatalogModels import GalaxyTileCompoundObj
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogZPoint
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from .sprinkler import sprinklerCompound

class InstcatFactory(object):
    def __init__(self, objid, phosimCatalogObject):
        while True:
        # This loop is a workaround for UW catsim db connection intermittency.
            try:
                self.db_obj = CatalogDBObject.from_objid(objid)
                break
            except RuntimeError:
                continue
        self.cat_obj = phosimCatalogObject
    def __call__(self, obs_metadata):
        return self.cat_obj(self.db_obj, obs_metadata=obs_metadata)

class InstcatGenerator(object):
    def __init__(self, opsim_db, fieldRA, fieldDec, boundLength=0.3,
                 pickle_file=None, sprinkle=True):
        self._set_instcatFactories()
        self._set_obs_md_results(opsim_db, fieldRA, fieldDec, boundLength,
                                 pickle_file)
        self.sprinkle = sprinkle

    def _set_instcatFactories(self):
        self._instcatFactories = {}
        starObjNames = ['msstars', 'bhbstars', 'wdstars', 'rrlystars',
                        'cepheidstars']
        for objid in starObjNames:
            self.update_factories(objid, PhoSimCatalogPoint)
        self.update_factories('galaxyBulge', PhoSimCatalogSersic2D)
        self.update_factories('galaxyDisk', PhoSimCatalogSersic2D)
        self.update_factories('galaxyAgn', PhoSimCatalogZPoint)

    def update_factories(self, objid, catobj):
        self._instcatFactories[objid] = InstcatFactory(objid, catobj)

    def _set_obs_md_results(self, opsim_db, fieldRA, fieldDec, boundLength,
                            pickle_file):
        if pickle_file is not None and os.path.isfile(pickle_file):
            self.obs_md_results = pickle.load(open(pickle_file))
        else:
            # Generate the observation metadata from the db file.
            gen = ObservationMetaDataGenerator(database=opsim_db,
                                               driver='sqlite')
            self.obs_md_results = gen.getObservationMetaData(fieldRA=fieldRA, 
                                                             fieldDec=fieldDec,
                                                             boundLength=boundLength)
            if pickle_file is not None:
                pickle.dump(self.obs_md_results, open(pickle_file, 'w'))

    def find_visits(self, bandpass, nmax=None):
        # Use an OrderedDict to gather the visits since a visit will
        # have multiple entries in the Summary table if it is part of
        # more than one proposal.
        visits = OrderedDict()
        for obs_metadata in self.obs_md_results:
            if nmax is not None and len(visits) == nmax:
                break
            if obs_metadata.bandpass == bandpass:
                obshistid = obs_metadata.phoSimMetaData['Opsim_obshistid'][0]
                visits[obshistid] = obs_metadata
        return visits

    def write_catalog(self, outfile, obs_metadata, clobber=True):
        if clobber and os.path.isfile(outfile):
            os.remove(outfile)
        cat_list = []
        for objid in self._instcatFactories:
            cat_list.append(self._instcatFactories[objid](obs_metadata))
        if self.sprinkle:
            compoundDBclass = sprinklerCompound
        else:
            compoundDBclass = GalaxyTileCompoundObj
        while True:
            try:
                my_cat = CompoundInstanceCatalog(cat_list,
                                                 obs_metadata=obs_metadata,
                                                 compoundDBclass=compoundDBclass)
                break
            except RuntimeError:
                continue
        my_cat.write_catalog(outfile)

if __name__ == '__main__':
    import os
    import time

    fieldID = 1427
    fieldRA = (53, 54)
    fieldDec = (-29, -27)

    opsim_db = '/nfs/slac/g/ki/ki18/jchiang/DESC/Twinkles/work/enigma_1189_sqlite.db'
    pickle_file = 'obs_metadata_enigma_1189_%(fieldID)i.pickle' % locals()

    t0 = time.time()
    generator = InstcatGenerator(opsim_db, fieldRA, fieldDec,
                                 pickle_file=pickle_file)
    print("Set up time:", time.time() - t0)

    nmax = 20
    for bandpass in 'ugrizy':
        print("band pass:", bandpass)
        visits = generator.find_visits(bandpass, nmax=nmax)
        i = 0
        for obshistid, visit in visits.items():
            i += 1
            outfile = 'phosim_input_%s_%07i.txt' % (bandpass, obshistid)
            print(i, outfile)
            if os.path.isfile(outfile):
                continue
            while True:
                try:
                    generator.write_catalog(outfile, visit)
                    break
                except KeyError as eobj:
                    print(eobj, "trying again")
                    os.remove(outfile)
