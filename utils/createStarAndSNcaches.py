from __future__ import with_statement
import numpy as np
import os
from lsst.utils import getPackageDir
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catalogs.db import fileDBObject
from lsst.sims.catUtils.baseCatalogModels import (StarObj, CepheidStarObj,
                                                  SNDBObj)


_obs = ObservationMetaData(pointingRA=53.0091385,
                           pointingDec=-27.4389488,
                           boundType='circle',
                           boundLength=0.31)

def create_star_cache(db=None):
    """
    Read the stars from a database and cache them in
    $TWINKLES_DIR/data/star_cache.db
    in the table 'star_cache_table'

    Params
    ------
    db is a CatalogDBObject connecting to the database from which to read
    the data.  If None, this will use the CatSim class StarObj(), which
    connects to the star table on fatboy.
    """
    star_dtype = np.dtype([('simobjid', int),
                           ('ra', float), ('decl', float),
                           ('magNorm', float),
                           ('mura', float), ('mudecl', float),
                           ('parallax', float), ('ebv', float),
                           ('vrad', float), ('varParamStr', str, 256),
                           ('sedfilename', unicode, 40),
                           ('gmag', float)])

    col_names = list(star_dtype.names)
    star_cache_name = os.path.join(getPackageDir('twinkles'), 'data',
                                   'twinkles_star_cache.txt')

    star_db_name = os.path.join(getPackageDir('twinkles'), 'data',
                                'star_cache.db')

    if db is None:
        db = StarObj()

    result_iterator = db.query_columns(colnames=col_names, chunk_size=100000,
                                       obs_metadata=_obs)
    with open(star_cache_name, 'w') as output_file:
        output_file.write('# ')
        for name in col_names:
            output_file.write('%s ' % name)
        output_file.write('\n')
        for chunk in result_iterator:
            for line in chunk:
                print line
                output_file.write(('%d;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%s;%s;%.17g\n' %
                                  (line[1], line[2], line[3], line[4], line[5], line[6], line[7],
                                   line[8], line[9], str(line[10]), str(line[11]),line[12])).replace('nan','NULL').replace('None','NULL'))

    if os.path.exists(star_db_name):
        os.unlink(star_db_name)

    dbo = fileDBObject(star_cache_name, driver='sqlite', runtable='star_cache_table',
                       database=star_db_name, dtype=star_dtype, delimiter=';',
                       idColKey='simobjid')

    if os.path.exists(star_cache_name):
        os.unlink(star_cache_name)


def create_sn_cache(db=None):
    """
    Read the supernova data from a database and cache it in the file
    $TWINKLES_DIR/data/sn_cache.db
    in the table 'sn_cache_table'

    Param
    -----
    db is a CatalogDBObject from which to read the data.  If None,
    use the CatSim class SNDBObj, which will connect to the
    TwinkSN_run3 table on fatboy.
    """
    sn_dtype = np.dtype([('id', int), ('galtileid', int),
                        ('snra', float), ('sndec', float),
                        ('t0', float), ('x0', float), ('x1', float),
                        ('c', float), ('redshift', float)])
    col_names = list(sn_dtype.names)
    sn_cache_name = os.path.join(getPackageDir('twinkles'), 'data', 'twinkles_sn_cache.txt')
    if os.path.exists(sn_cache_name):
        os.unlink(sn_cache_name)

    sn_db_name = os.path.join(getPackageDir('twinkles'), 'data', 'sn_cache.db')
    if db is None:
        db = SNDBObj(table='TwinkSN_run3')

    result_iterator = db.query_columns(colnames=col_names, chunk_size=10000,
                                       obs_metadata = _obs)

    with open(sn_cache_name, 'w') as output_file:
        output_file.write('# ')
        for name in col_names:
            output_file.write('%s ' % name)
        output_file.write('\n')
        for chunk in result_iterator:
            for line in chunk:
                output_file.write(('%d;%ld;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g\n' %
                                   (line[0], line[1], line[2], line[3],
                                    line[4], line[5], line[6], line[7],
                                    line[8])).replace('nan', 'NULL').replace('None','NULL'))

    if os.path.exists(sn_db_name):
        os.unlink(sn_db_name)

    dbo = fileDBObject(sn_cache_name, driver='sqlite', runtable='sn_cache_table',
                       database=sn_db_name, dtype=sn_dtype, delimiter=';', idColKey='id')

    if os.path.exists(sn_cache_name):
        os.unlink(sn_cache_name)


if __name__ == "__main__":
    """
    Right now, __main__ is configured to read from a dummy fatboy database
    created for testing while fatboy is down.
    """

    #from desc.twinkles import create_galaxy_cache
    #create_galaxy_cache()
    create_star_cache()
    create_sn_cache()


    """
    from create_dummy_fatboy import createDummyFatboy
    db_name = os.path.join(getPackageDir('twinkles'), 'data', 'scratch_database.db')
    if os.path.exists(db_name):
        os.unlink(db_name)
    createDummyFatboy(db_name)

    from lsst.sims.catalogs.db import CatalogDBObject
    class dummyStars(CatalogDBObject):
        tableid='StarAllForceSeek'
        idColKey='simobjid'
        raColName='ra'
        decColName='decl'
        database=db_name
        host=None
        port=None
        driver='sqlite'

    db = dummyStars()
    create_star_cache(db=db)

    class dummySN(CatalogDBObject):
        tableid='TwinkSN_run3'
        idColKey='galtileid'
        raColName='snra'
        decColName='sndec'
        database=db_name
        host=None
        port=None
        driver='sqlite'

    db = dummySN()
    create_sn_cache(db=db)
    """
