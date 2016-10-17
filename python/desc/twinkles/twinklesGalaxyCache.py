import numpy as np
import os
from lsst.utils import getPackageDir
from lsst.sims.catalogs.db import fileDBObject
from lsst.sims.catalogs.db import CatalogDBObject, CompoundCatalogDBObject
from lsst.sims.catUtils.baseCatalogModels import GalaxyObj
from desc.twinkles import sprinkler

__all__ = ["_galaxy_cache_file_name",
           "_galaxy_cache_dtype",
           "getGalaxyCacheConnection",
           "GalaxyCacheDiskObj", "GalaxyCacheBulgeObj",
           "GalaxyCacheAgnObj", "GalaxyCacheSprinklerObj"]


_galaxy_cache_file_name = 'twinkles_galaxy_cache.txt'

_galaxy_cache_table_name = 'galaxy_cache'

_galaxy_cache_db_name = os.path.join(getPackageDir('twinkles'), 'data',
                                     'galaxy_cache.db')

_galaxy_cache_dtype = np.dtype([('galtileid', int),
                                ('ra', float), ('dec', float),
                                ('sedname_disk', str, 50), ('magnorm_disk', float),
                                ('sedname_bulge', str, 50), ('magnorm_bulge', float),
                                ('sedname_agn', str, 50), ('magnorm_agn', float),
                                ('varParamStr', str, 256), ('redshift', float),
                                ('g_ab', float), ('a_b', float), ('b_b', float),
                                ('pa_bulge', float), ('a_d', float), ('b_d', float),
                                ('pa_disk', float),('bulge_n', float), ('disk_n', float),
                                ('av_b', float), ('rv_b', float), ('av_d', float),
                                ('rv_d', float)])


def getGalaxyCacheConnection():
    """
    Read in the galaxy cache, convert it to a database, and return a
    connection to that database.
    """

    file_name = os.path.join(getPackageDir('twinkles'), 'data',
                             _galaxy_cache_file_name)

    if os.path.exists(_galaxy_cache_db_name):
        os.unlink(_galaxy_cache_db_name)

    dbo = fileDBObject(file_name, driver='sqlite',
                       runtable=_galaxy_cache_table_name,
                       database=_galaxy_cache_db_name,
                       dtype=_galaxy_cache_dtype,
                       delimiter=';',
                       idColKey='galtileid')

    return dbo.connection


# the code below defines a series of CatalogDBObjects
# specifically designed to access the off-line Twinkles
# galaxy cache, but otherwise mimic the behavior of
# GalaxyDiskObj,GalaxyBulgeObj, and GalaxyAgnObj

class GalaxyCacheBase(CatalogDBObject):
    tableid = _galaxy_cache_table_name
    idColKey = 'galtileid'
    raColName = 'ra'
    decColName = 'dec'
    database = _galaxy_cache_db_name
    host = None
    port = None
    driver = 'sqlite'


class GalaxyCacheDiskObj(GalaxyCacheBase):
    objid = 'galaxyDisk'
    objectTypeId = 27

    columns = [('galtileid', None, np.int64),
               ('raJ2000', 'ra*PI()/180.0', float),
               ('decJ2000', 'dec*PI()/180.0', float),
               ('magNorm', 'magnorm_disk', float),
               ('sedFilename', 'sedname_disk', str, 50),
               ('majorAxis', 'a_d*PI()/648000.0', float),
               ('minorAxis', 'b_d*PI()/648000.0', float),
               ('positionAngle', 'pa_disk*PI()/180.0', float),
               ('internalAv', 'av_d', float),
               ('internalRv', 'rv_d', float),
               ('sindex', 'disk_n', float)]


class GalaxyCacheBulgeObj(GalaxyCacheBase):
    objid = 'galaxyBulge'
    objectTypeId = 26

    columns = [('galtileid', None, np.int64),
               ('raJ2000', 'ra*PI()/180.0', float),
               ('decJ2000', 'dec*PI()/180.0', float),
               ('magNorm', 'magnorm_bulge', float),
               ('sedFilename', 'sedname_bulge', str, 50),
               ('majorAxis', 'a_b*PI()/648000.0', float),
               ('minorAxis', 'b_b*PI()/648000.0', float),
               ('positionAngle', 'pa_bulge*PI()/180.0', float),
               ('internalAv', 'av_b', float),
               ('internalRv', 'rv_b', float),
               ('sindex', 'bulge_n', float)]


class GalaxyCacheAgnObj(GalaxyCacheBase):
    objid = 'galaxyAgn'
    objectTypeId = 28

    columns = [('galtileid', None, np.int64),
               ('raJ2000', 'ra*PI()/180.0', float),
               ('decJ2000', 'dec*PI()/180.0', float),
               ('magNorm', 'magnorm_agn', float),
               ('sedFilename', 'sedname_agn', str, 50),
               ('variabilityParameters', 'varParamStr', str, 256)]


# This CompoundCatalogDBObject deploys the sprinkler
# on the CatalogDBObjects defined above.  It differs from
# sprinklerCompound in that it does not cast 'raJ2000' and
# 'decJ2000' into radians in the _final_pass() method.
# That operation was an artifact of how GalaxyTileObj differs
# from all other CatalogDBObjects.  Since we are no longer
# connecting to GalaxyTileObj, we no longer have to perform
# the operation.

class GalaxyCacheSprinklerObj(CompoundCatalogDBObject):
    objid = 'galaxyCacheSprinkler'
    objectTypeId = 66
    def _final_pass(self, results):

        # the stored procedure on fatboy that queries the galaxies
        # constructs galtileid by taking
        #
        # tileid*10^8 + galid
        #
        # this causes galtileid to be so large that the uniqueIDs in the
        # Twinkles InstanceCatalogs are too large for PhoSim to handle.
        # Since Twinkles is only focused on one tile on the sky, we will remove
        # the factor of 10^8, making the uniqueIDs a more manageable size
        results['galtileid'] = results['galtileid']%100000000

        #Use Sprinkler now
        sp = sprinkler(results, density_param = 1.0)
        results = sp.sprinkle()

        return results
