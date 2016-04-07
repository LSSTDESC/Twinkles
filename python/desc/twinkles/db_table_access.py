"""
Classes to fill the ForcedSource, CcdVisit, Object tables as described
at https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline
using data from the Twinkles Level 2 output repository.
"""
from __future__ import absolute_import, print_function, division
from builtins import zip, range, object, dict
import os
import sys
import copy
from collections import OrderedDict
import json
import numpy as np
import sqlite3
import MySQLdb
import astropy.io.fits
import astropy.time
from .registry_tools import get_visits, find_registry

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
    __connection_pool = dict()
    __connection_refs = dict()
    def __init__(self, **kwds):
        """
        Constructor to make the connection object and check for the
        desired db table.
        """
        self._get_mysql_connection(kwds)
        self._check_for_table()

    def __del__(self):
        """
        Decrement reference counts to the connection object and close
        it if ref counts is zero.
        """
        self.__connection_refs[self._conn_key] -= 1
        if self.__connection_refs[self._conn_key] == 0:
            self._mysql_connection.close()
            del self.__connection_pool[self._conn_key]
            del self.__connection_refs[self._conn_key]

    def _get_mysql_connection(self, kwds_par):
        """
        Update the connection pool and reference counts, and set the
        self._mysql_connection reference.
        """
        kwds = copy.deepcopy(kwds_par)
        try:
            del kwds['table_name']
        except KeyError:
            pass
        # Serialize the kwds dict to obtain a hashable key for the
        # self.__connection_pool and self.__connection_refs dicts.
        self._conn_key = json.dumps(kwds, sort_keys=True)

        if self._conn_key not in self.__connection_pool:
            # Create a new mysql connection object.
            self.__connection_pool[self._conn_key] = MySQLdb.connect(**kwds)

        # Update the reference counts for the connection objects.
        try:
            self.__connection_refs[self._conn_key] += 1
        except KeyError:
            self.__connection_refs[self._conn_key] = 1

        self._mysql_connection = self.__connection_pool[self._conn_key]

    def _check_for_table(self):
        """
        Check if the desired table, as specified in the subclass,
        exists.  If not, then create it.
        """
        try:
            self._table_name
        except AttributeError:
            self._table_name = ''
        query = "show tables like '%s'" % self._table_name
        if not self.apply(query, lambda curs : [x for x in curs]):
            self._create_table()

    def _create_table(self):
        "Default do-nothing function."
        pass

    def apply(self, query, cursorFunc=_nullFunc):
        """
        Apply the query, optionally using the cursorFunc to process
        the query results.
        """
        cursor = self._mysql_connection.cursor()
        try:
            cursor.execute(query)
            results = cursorFunc(cursor)
        except MySQLdb.DatabaseError as message:
            cursor.close()
            raise MySQLdb.DatabaseError(message)
        cursor.close()
        if cursorFunc is _nullFunc:
            self._mysql_connection.commit()
        return results

class CcdVisitTable(LsstDatabaseTable):
    "Abstraction for the CcdVisit table."
    def __init__(self, **kwds):
        try:
            self._table_name = kwds['table_name']
        except KeyError:
            self._table_name = 'CcdVisit'
        super(CcdVisitTable, self).__init__(**kwds)

    def _create_table(self):
        """
        This function creates a CcdVisit table following the schema at
        https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline&t=CcdVisit
        """
        query = """create table %s (ccdVisitId BIGINT,
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
                primary key (ccdVisitId))""" % self._table_name
        self.apply(query)

    def ingestRegistry(self, registry_file):
        "Ingest some relevant data from a registry.sqlite3 file."
        table_name = self._table_name
        registry = sqlite3.connect(registry_file)
        query = """select taiObs, visit, filter, raft, ccd,
                expTime from raw where channel='0,0' order by visit asc"""
        for row in registry.execute(query):
            taiObs, visit, filter_, raft, ccd, expTime = tuple(row)
            taiObs = taiObs[:len('2016-03-18 00:00:00.000000')]
            query = """insert into %(table_name)s set ccdVisitId=%(visit)i,
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
            except MySQLdb.DatabaseError as eobj:
                print("query:", query)
                raise eobj

class ForcedSourceTable(LsstDatabaseTable):
    "Abstraction for the ForcedSource table."
    def __init__(self, **kwds):
        try:
            self._table_name = kwds['table_name']
        except KeyError:
            self._table_name = 'ForcedSource'
        super(ForcedSourceTable, self).__init__(**kwds)

    def _create_table(self):
        """
        This function creates a ForcedSource table following the schema at
        https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline&t=ForcedSource
        """
        query = """create table %s (objectId BIGINT,
                ccdVisitId BIGINT,
                psFlux FLOAT,
                psFlux_Sigma FLOAT,
                flags TINYINT,
                primary key (objectId, ccdVisitId))""" % self._table_name
        self.apply(query)

    def _generate_strides(self, npts, stride_length):
        """
        Generate a list of sublists of index values up to npts.  Each sublist
        will have a length of stride_length, except perhaps for the last
        one, which will have the remaining index values.
        """
        strides = []
        for leg in range(int(npts/stride_length) + 1):
            row = [leg*stride_length + j for j in range(stride_length)
                   if leg*stride_length + j < npts]
            if row:
                strides.append(row)
        return strides

    def ingestSourceCatalog(self, source_catalog, ccdVisitId, stride_length=30):
        """
        Ingest a forced source FITS catalog.
        Inputs:
        source_catalog = path the forced source catalog
        ccdVisitId = This is primary key from the ccdVisitId table and
                     uniquely identifies the CCD and visit combination.
        stride_length = number of rows to insert per query.  The efficiency
                        starts to plateau at 30 rows.
        """
        table_name = self._table_name
        hdulist = astropy.io.fits.open(source_catalog)
        data = hdulist[1].data
        nobjs = len(data['objectId'])
        print("ingesting %i sources" % nobjs)
        sys.stdout.flush()
        strides = self._generate_strides(nobjs, stride_length)
        flags = 0
        nrows = 0
        for stride in strides:
            values_list = []
            for index in stride:
                objectId = data['objectId'][index]
                flux = data['base_PsfFlux_flux'][index]
                fluxerr = data['base_PsfFlux_fluxSigma'][index]
                if np.isnan(flux) or np.isnan(fluxerr):
                    continue
                row_tuple = objectId, ccdVisitId, flux, fluxerr, flags
                values_list.append('(%i, %i, %15.7e, %15.7e, %i)' % row_tuple)
                nrows += 1
                if nrows % int(nobjs/20) == 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()
            values = ','.join(values_list) + ';'
            query = "insert into %(table_name)s values %(values)s" % locals()
            try:
                self.apply(query)
            except Exception as eobj:
                print(query)
                raise eobj
        print("!")

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
        table_name = self._table_name
        for band in 'ugrizy':
            query = """select cv.obsStart, obj.psRa, obj.psDecl,
                    fs.psFlux, fs.psFlux_Sigma, fs.ccdVisitId
                    from CcdVisit cv join %(table_name)s fs
                    on cv.ccdVisitId=fs.ccdVisitId join Object obj
                    on fs.objectId=obj.objectId
                    where cv.filterName='%(band)s' and fs.objectId=%(objectId)i
                    order by cv.obsStart asc""" % locals()
            light_curves[band] = self.apply(query, self._process_rows)
        return light_curves

class ObjectTable(LsstDatabaseTable):
    "Abstraction for Object table."
    def __init__(self, **kwds):
        try:
            self._table_name = kwds['table_name']
        except KeyError:
            self._table_name = 'Object'
        super(ObjectTable, self).__init__(**kwds)

    def _create_table(self):
        """
        Create a vastly truncated version of the Object table. See
        https://lsst-web.ncsa.illinois.edu/schema/index.php?sVer=baseline&t=Object
        """
        query = """create table %s (objectId BIGINT,
                parentObjectId BIGINT,
                numChildren INT,
                psRa DOUBLE,
                psDecl DOUBLE,
                primary key (objectId))""" % self._table_name
        self.apply(query)

    def ingestRefCatalog(self, ref_catalog):
        "Ingest the reference catalog from the merged coadds."
        hdulist = astropy.io.fits.open(ref_catalog)
        data = hdulist[1].data
        nobjs = len(data['id'])
        print("ingesting %i objects" % nobjs)
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
            query = """insert into %s values (%i, %i, 0, %17.9e, %17.9e)
                    on duplicate key update psRa=%17.9e, psDecl=%17.9e""" \
                % (self._table_name, objectId, parent, ra_val, dec_val,
                   ra_val, dec_val)
            self.apply(query)
            nrows += 1
        print("!")
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
                if parent not in results:
                    results[parent] = 0
                results[parent] += 1
            return results

        results = self.apply(query, count_children)
        for parentId, numChildren in results.items():
            query = '''update Object set numChildren=%(numChildren)i
                    where objectId=%(parentId)i''' % locals()
            self.apply(query)
