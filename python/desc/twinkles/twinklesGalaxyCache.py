import numpy as np
import os
from lsst.utils import getPackageDir
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catalogs.db import fileDBObject
from lsst.sims.catalogs.db import CatalogDBObject, CompoundCatalogDBObject
from lsst.sims.catUtils.baseCatalogModels import GalaxyObj, GalaxyTileObj
from desc.twinkles import sprinkler

__all__ = ["_galaxy_cache_db_name",
           "create_galaxy_cache",
           "GalaxyCacheDiskObj", "GalaxyCacheBulgeObj",
           "GalaxyCacheAgnObj", "GalaxyCacheSprinklerObj"]


# the name of the text file that will contain the galaxy cache
_galaxy_cache_file_name = os.path.join(getPackageDir('twinkles'), 'data',
                                       'twinkles_galaxy_cache.txt')

# the name of the table containing the galaxies in the galaxy cache database
_galaxy_cache_table_name = 'galaxy_cache'

# the name of the sqlite database produced from the galaxy cache
_galaxy_cache_db_name = os.path.join(getPackageDir('twinkles'), 'data',
                                     'galaxy_cache.db')

# the dtype describing the contents of the galaxy cache
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


class GalaxyTileObjDegrees(GalaxyTileObj):
    """
    We needed to sub-class GalaxyTileObj so that we can replace
    _final_pass, which requires you to query for
    (raJ2000, decJ2000), rather than (ra, dec)
    """
    def _final_pass(self, results):
        return results


def create_galaxy_cache():
    """
    Create an sqlite .db file in data/ containing all of the galaxies
    in the Twinkles field of view.
    """

    obs = ObservationMetaData(pointingRA=53.0091385,
                              pointingDec=-27.4389488,
                              boundType='circle',
                              boundLength=0.31)

    db = GalaxyTileObjDegrees()

    col_names = list(_galaxy_cache_dtype.names)

    result_iterator = db.query_columns(colnames=col_names, chunk_size=100000,
                                       obs_metadata=obs)

    with open(_galaxy_cache_file_name, 'w') as output_file:
        output_file.write('# galtileid ')
        for name in col_names:
            output_file.write('%s ' % name)
        output_file.write('\n')
        for chunk in result_iterator:
            for line in chunk:
                output_file.write(('%ld;%.17g;%.17g;%s;%.17g;%s;%.17g;%s;%.17g;%s;%.17g;%.17g;'
                                   % (line[0], line[1], line[2],
                                      line[3], line[4], line[5],
                                      line[6], line[7], line[8],
                                      line[9], line[10], line[11])).replace('nan', 'NULL').replace('None', 'NULL')
                                   + ('%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g'
                                      % (line[12], line[13], line[14],
                                         line[15], line[16], line[17],
                                         line[18], line[19], line[20],
                                         line[21], line[22], line[23])).replace('nan', 'NULL').replace('None', 'NULL')
                                   + '\n')

    if os.path.exists(_galaxy_cache_db_name):
        os.unlink(_galaxy_cache_db_name)

    dbo = fileDBObject(_galaxy_cache_file_name, driver='sqlite',
                       runtable=_galaxy_cache_table_name,
                       database=_galaxy_cache_db_name,
                       dtype=_galaxy_cache_dtype,
                       delimiter=';',
                       idColKey='galtileid')


    if os.path.exists(_galaxy_cache_file_name):
        os.unlink(_galaxy_cache_file_name)

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
