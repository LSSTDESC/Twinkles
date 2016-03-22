"""
Classes to fill the ForcedSource and CcdVisit tables as described at
https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline
using data from the Twinkles Level 2 output repository.
"""
import os
import sys
from collections import OrderedDict
import numpy as np
import sqlite3
import MySQLdb
import astropy.io.fits
import astropy.time
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
    _table_name = ''
    def __init__(self, **kwds):
        """
        Constructor to make the connection attribute and create the
        table if it doesn't already exist.
        """
        global _mysql_connection
        if _mysql_connection is None:
            _mysql_connection = MySQLdb.connect(**kwds)
        query = "show tables like '%s'" % self._table_name
        if not self.apply(query, lambda curs : [x for x in curs]):
            self._create_table()

    def _create_table(self):
        "Default do-nothing function."
        pass

    def close(self):
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
        self._table_name = 'CcdVisit'
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
        query = """select taiObs, visit, filter, raft, ccd,
                expTime from raw where channel='0,0' order by visit asc"""
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
        self._table_name = 'ForcedSource'
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
        hdulist = astropy.io.fits.open(source_catalog)
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
            query = """insert into ForcedSource values
                    (%i, %i, %15.7e, %15.7e, %i)
                    on duplicate key update
                    psFlux=%15.7e, psFlux_Sigma=%15.7e, flags=%i""" \
                % (objectId, ccdVisitId, flux, fluxerr, flags,
                   flux, fluxerr, flags)
            self.apply(query)
            nrows += 1
        print "!"

    @staticmethod
    def _process_rows(cursor):
        results = []
        dtype = [('mjd', float), ('ra', float), ('dec', float),
                 ('flux', float), ('fluxerr', float), ('visit', int)]
        for entry in cursor:
            obs_start, ra, dec, flux, fluxerr, visit = tuple(entry)
            mjd = astropy.time.Time(obs_start).mjd
            results.append((mjd, ra, dec, flux, fluxerr, visit))
        results = np.array(results, dtype=dtype)
        return results

    def get_light_curves(self, objectId):
        """
        Return the forced source light curves in ugrizy bands for
        objectId.
        """
        light_curves = OrderedDict()
        for band in 'ugrizy':
            query = """select cv.obsStart, obj.psRa, obj.psDecl,
                    fs.psFlux, fs.psFlux_Sigma, fs.ccdVisitId
                    from CcdVisit cv join ForcedSource fs
                    on cv.ccdVisitId=fs.ccdVisitId join Object obj
                    on fs.objectId=obj.objectId
                    where cv.filterName='%(band)s' and fs.objectId=%(objectId)i
                    order by cv.obsStart asc""" % locals()
            light_curves[band] = self.apply(query, self._process_rows)
        return light_curves

class ObjectTable(LsstDatabaseTable):
    "Abstraction for Object table."
    def __init__(self, **kwds):
        self._table_name = 'Object'
        super(ObjectTable, self).__init__(**kwds)

    def _create_table(self):
        """
        Create a vastly truncated version of the Object table. See
        https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline&t=Object
        """
        query = """create table Object (objectId BIGINT,
                parentObjectId BIGINT,
                numChildren INT,
                psRa DOUBLE,
                psDecl DOUBLE,
                primary key (objectId))"""
        self.apply(query)

    def ingestRefCatalog(self, ref_catalog):
        "Ingest the reference catalog from the merged coadds."
        hdulist = astropy.io.fits.open(ref_catalog)
        data = hdulist[1].data
        nobjs = len(data['id'])
        print "ingesting %i objects" % nobjs
        sys.stdout.flush()
        nrows = 0
        for objectId, ra, dec, parent in zip(data['id'],
                                             data['coord_ra'],
                                             data['coord_dec'],
                                             data['parent']):
            if nrows % (nobjs/20) == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
            ra_val = ra*180./np.pi
            dec_val = dec*180./np.pi
            query = """insert into Object values (%i, %i, 0, %17.9e, %17.9e)
                    on duplicate key update psRa=%17.9e, psDecl=%17.9e""" \
                % (objectId, parent, ra_val, dec_val, ra_val, dec_val)
            self.apply(query)
            nrows += 1
        print "!"
        self.updateNumChildren()

    def updateNumChildren(self):
        """Update the Object table with the number of deblended
        children for each object."""
        query = '''select objectId, parentObjectId from Object where
                parentObjectId!=0'''

        def count_children(curs):
            results = dict()
            for entry in curs:
                objectId, parent = tuple(entry)
                if not results.has_key(parent):
                    results[parent] = 0
                results[parent] += 1
            return results

        results = self.apply(query, count_children)
        for parentId, numChildren in results.items():
            query = '''update Object set numChildren=%(numChildren)i
                    where objectId=%(parentId)i''' % locals()
            self.apply(query)
