"""
Classes to fill the ForcedSource and CcdVisit tables as described at
https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline
using data from the Twinkles Level 2 output repository.
"""
import os
import sys
import numpy as np
import sqlite3
import MySQLdb
import astropy.io.fits as fits
from registry_tools import get_visits, find_registry

_mysql_connection = None

def _nullFunc(*args):
    """
    Default do-nothing function for processing data from a MySQLdb
    cursor object.
    """
    return None

class LsstDatabaseTable(object):
    """
    Base class for LSST database tables.
    """
    def __init__(self, **kwds):
        """
        Constructor to create the connection attribute and create the
        table if it doesn't already exist.
        """
        global _mysql_connection
        if _mysql_connection is None:
            _mysql_connection = MySQLdb.connect(**kwds)
        try:
            self._create_table()
        except MySQLdb.DatabaseError, eobj:
            # If table already exists, do nothing, otherwise re-raise
            # the exception.
            if eobj[0][0] != 1050:
                raise eobj

    def __del__(self):
        "Close the db connection."
        global _mysql_connection
        try:
            _mysql_connection.close()
        except AttributeError:
            pass
        _mysql_connection = None

    def apply(self, query, cursorFunc=_nullFunc):
        """
        Apply the query, optionally using the cursorFunc to process
        the query results.
        """
        global _mysql_connection
        cursor = _mysql_connection.cursor()
        try:
            cursor.execute(query)
            results = cursorFunc(cursor)
        except MySQLdb.DatabaseError, message:
            cursor.close()
            raise MySQLdb.DatabaseError(message)
        cursor.close()
        if cursorFunc is _nullFunc:
            _mysql_connection.commit()
        return results

class CcdVisitTable(LsstDatabaseTable):
    "Abstraction for the CcdVisit table."
    def __init__(self, **kwds):
        super(CcdVisitTable, self).__init__(**kwds)

    def _create_table(self):
        """
        This function creates a CcdVisit table following the schema at
        https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline&t=CcdVisit
        """
        query = """create table CcdVisit (ccdVisitId BIGINT,
                visitId INTEGER,
                ccdName CHAR(3),
                raftName CHAR(3),
                filterName CHAR(1),
                nExposures INT,
                ra DOUBLE,
                decl DOUBLE,
                zenithDistance FLOAT,
                llcx INTEGER,
                llcy INTEGER,
                ulcx INTEGER,
                ulcy INTEGER,
                urcx INTEGER,
                urcy INTEGER,
                lrcx INTEGER,
                lrcy INTEGER,
                xSize INTEGER,
                ySize INTEGER,
                obsStart TIMESTAMP,
                expMidpt DOUBLE,
                expTime DOUBLE,
                darkTime DOUBLE,
                ccdTemp FLOAT,
                binX INTEGER,
                binY INTEGER,
                WCS BLOB,
                zeroPoint FLOAT,
                seeing FLOAT,
                skyBg FLOAT,
                skyNoise FLOAT,
                flags INTEGER,
                primary key (ccdVisitId))"""
        self.apply(query)

    def ingestRegistry(self, registry_file):
        "Ingest some relevant data from a registry.sqlite3 file."
        registry = sqlite3.connect(registry_file)
        query = "select taiObs, visit, filter, raft, ccd, expTime from raw where channel='0,0' order by visit asc"
        for row in registry.execute(query):
            taiObs, visit, filter_, raft, ccd, expTime = tuple(row)
            taiObs = taiObs[:len('2016-03-18 00:00:00.000000')]
            query = """insert into CcdVisit set ccdVisitId=%(visit)i,
                       visitId=%(visit)i, ccdName='%(ccd)s',
                       raftName='%(raft)s', filterName='%(filter_)s',
                       obsStart='%(taiObs)s'
                       on duplicate key update
                       visitId=%(visit)i, ccdName='%(ccd)s',
                       raftName='%(raft)s', filterName='%(filter_)s',
                       obsStart='%(taiObs)s'""" \
                % locals()
            try:
                self.apply(query)
            except MySQLdb.DatabaseError, eobj:
                print "query:", query
                raise eobj

class ForcedSourceTable(LsstDatabaseTable):
    "Abstraction for the ForcedSource table."
    def __init__(self, **kwds):
        super(ForcedSourceTable, self).__init__(**kwds)

    def _create_table(self):
        """
        This function creates a ForcedSource table following the schema at
        https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline&t=ForcedSource
        """
        query = """create table ForcedSource (objectId BIGINT,
                ccdVisitId BIGINT,
                psFlux FLOAT,
                psFlux_Sigma FLOAT,
                flags TINYINT,
                primary key (objectId, ccdVisitId))"""
        self.apply(query)

    def ingestSourceCatalog(self, source_catalog, ccdVisitId):
        """
        Ingest a forced source FITS catalog.
        """
        hdulist = fits.open(source_catalog)
        data = hdulist[1].data
        nobjs = len(data['objectId'])
        print "ingesting %i sources" % nobjs
        sys.stdout.flush()
        nrows = 0
        for objectId, flux, fluxerr in zip(data['objectId'],
                                           data['base_PsfFlux_flux'],
                                           data['base_PsfFlux_fluxsigma']):
            if nrows % (nobjs/20) == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
            if np.isnan(flux) or np.isnan(fluxerr):
                continue
            flags = 0
            query = "insert into ForcedSource values (%i, %i, %15.7e, %15.7e, %i) on duplicate key update objectId=%i" % (objectId, ccdVisitId, flux, fluxerr, flags, objectId)
            self.apply(query)
            nrows += 1
        print "!"

if __name__ == '__main__':
    data_repo = '/nfs/farm/g/lsst/u1/users/tonyj/Twinkles/run1/985visits'
    db_info = dict(db='jc_desc', read_default_file='~/.my.cnf')

    ccd_visit_table = CcdVisitTable(**db_info)
    registry_file = find_registry(data_repo)
    ccd_visit_table.ingestRegistry(registry_file)

    forced_src_table = ForcedSourceTable(**db_info)
    visits = get_visits(data_repo)
    for band, visit_list in visits.items():
        if band == 'r':
            continue
        print "processing band", band, "for", len(visit_list), "visits."
        for ccdVisitId in visit_list[:10]:
            visit_name = 'v%i-f%s' % (ccdVisitId, band)
            catalog = os.path.join(data_repo, 'forced', '0',
                                   visit_name, 'R22', 'S11.fits')
            print "Processing", visit_name
            forced_src_table.ingestSourceCatalog(catalog, ccdVisitId)
