from __future__ import absolute_import
import numpy
import os
from lsst.utils import getPackageDir
from lsst.sims.catalogs.db import CatalogDBObject
from lsst.sims.catUtils.baseCatalogModels import SNDBObj, GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj

__all__ = ["StarCacheDBObj", "TwinklesBulgeObj", "TwinklesDiskObj", "TwinklesAgnObj"]

class StarCacheDBObj(CatalogDBObject):
    tableid = 'star_cache_table'
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
               ('sedFilename', 'sedfilename', str, 40)]


class SNCacheDBObj(SNDBObj, CatalogDBObject):
    host = None
    port = None
    tableid = 'sn_cache_table'
    driver = 'sqlite'

    def query_columns(self, *args, **kwargs):
        return CatalogDBObject.query_columns(self, *args, **kwargs)

class TwinklesBulgeObj(GalaxyBulgeObj):

    database = 'LSSTCATSIM'
    port = 1433
    host = 'fatboy.phys.washington.edu'
    driver = 'mssql+pymssql'

    objid = 'galaxyBulge'

class TwinklesDiskObj(GalaxyDiskObj):

    database = 'LSSTCATSIM'
    port = 1433
    host = 'fatboy.phys.washington.edu'
    driver = 'mssql+pymssql'

    objid = 'galaxyDisk'

class TwinklesAgnObj(GalaxyAgnObj):

    database = 'LSSTCATSIM'
    port = 1433
    host = 'fatboy.phys.washington.edu'
    driver = 'mssql+pymssql'

    objid = 'galaxyAgn'

    columns = [('galtileid', None, numpy.int64),
               ('galid', None, str, 30),
               ('componentra', 'agnra*PI()/180.'),
               ('componentdec', 'agndec*PI()/180.'),
               #: This is actually a problem with the stored procedure.
               #: We need to be able to map columns other than
               #: just ra/dec to raJ2000/decJ2000.  This gets
               #: important when we start perturbing the three galaxy components
               ('raJ2000', 'ra'),
               ('decJ2000', 'dec'),
               ('magNorm', 'magnorm_agn'),
               ('magNormAgn', 'magnorm_agn'),
               ('sedFilename', 'sedname_agn', str, 40),
               ('sedFilenameAgn', 'sedname_agn', str, 40),
               ('variabilityParameters', 'varParamStr', str, 256),
               ('lsst_u', 'u_ab'),
               ('lsst_g', 'g_ab'),
               ('lsst_r', 'r_ab'),
               ('lsst_i', 'i_ab'),
               ('lsst_z', 'z_ab'),
               ('lsst_y', 'y_ab')]
