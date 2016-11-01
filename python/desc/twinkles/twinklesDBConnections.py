import os
from lsst.utils import getPackageDir
from lsst.sims.catalogs.db import CatalogDBObject
from lsst.sims.catUtils.baseCatalogModels import SNDBObj

__all__ = ["StarCacheDBObj"]

class StarCacheDBObj(CatalogDBObject):
    tableid = 'star_cache_table'
    database = os.path.join(getPackageDir('twinkles'), 'data', 'star_cache.db')
    host = None
    port = None
    driver = 'sqlite'
    objectTypeId = 4
    idColKey = 'simobjid'
    raColName = 'ra'
    decColName = 'decl'

    columns = [('id','simobjid', int),
               ('raJ2000', 'ra*PI()/180.'),
               ('decJ2000', 'decl*PI()/180.'),
               ('glon', 'gal_l*PI()/180.'),
               ('glat', 'gal_b*PI()/180.'),
               ('properMotionRa', '(mura/(1000.*3600.))*PI()/180.'),
               ('properMotionDec', '(mudecl/(1000.*3600.))*PI()/180.'),
               ('parallax', 'parallax*PI()/648000000.'),
               ('galacticAv', 'CONVERT(float, ebv*3.1)'),
               ('radialVelocity', 'vrad'),
               ('variabilityParameters', 'varParamStr', str, 256),
               ('sedFilename', 'sedfilename', unicode, 40)]


class SNCacheDBObj(CatalogDBObject):
    database = os.path.join(getPackageDir('twinkles'), 'data', 'sn_cache.db')
    host = None
    port = None
    tableid = 'sn_cache_table'
    driver = 'sqlite'

    objid = 'TwinkUnlensedSN'
    # From now on the tableid should be specified in instantiating the class
    # table = 'TwinkSN' or 'TwinkSNKraken'
    idColKey = 'galtileid'
    raColName = 'snra'
    decColName = 'sndec'
    objectTypeId = 42

    columns = [('raJ2000', 'snra*PI()/180.'),
               ('decJ2000', 'sndec*PI()/180.'),
               ('Tt0', 't0'),
               ('Tx0', 'x0'),
               ('Tx1', 'x1'),
               ('Tc', 'c'),
               ('Tsnid', 'id'),
               ('Tredshift', 'redshift'),
               ('Tgaltileid', 'galtileid')
              ]
