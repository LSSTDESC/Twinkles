"""
Classes to represent the data in PhoSim instance Catalogs. PhoSim instance
Catalogs are ascii files used as inputs for PhoSim. The format includes a
few lines summarizing metadata, and then tables (without headers) describing
sources. The tables are non-rectangular because sources of different types have
different numbers of columns.

- PhoSimHeaders : Class for headers needed for phosim Instance catalogs
- PhoSimInputCatalog : Data in a phosim instance catalog splitted into three
    tables. It is possible to test for (approximate) equality of instances of such classes
"""
from __future__ import absolute_import, division, print_function
import numpy as np
from lsst.sims.catUtils.exampleCatalogDefinitions \
    import DefaultPhoSimInstanceCatalogCols
from cStringIO import StringIO
import string
import pandas as pd
from collections import OrderedDict as odict
from pandas.util.testing import assert_frame_equal
from copy import deepcopy, copy

__all__ = ['PhoSimInputCatalog', 'PhoSimHeaders', 'PhoSimCentroidData']

class PhoSimHeaders:
    """
    Class for headers for different phoSim catalogs. The values of
    the attributes change depending on the value of `keepObsHistID`.
    For `keepObsHistID=True`, The 'object' column is replaced by `ObsHistID`.
    If this is False, the object column is dropped.

    Attributes
    ----------
    defaultHeaders: a tuple of defaultHeaders (not customized to different
        kinds of sources obtained from `sims.catUtils.exampleCatalogDefinitions`
        This is not to be modified and is only kept as a deepcopy
    keepObsHistID : Bool, defaults to True
        keep first column 'ObsHistID' instead of 'object'
    PointHeader : sequence of strings
        Column names for Sources of Type Points
    GalaxyHeader : sequence of strings
        Column names for Sources of Type Galaxy
    numPointCols : int
        number of columns for Points
    numGalaxyCols : int
        number of columns for Points
    """
    defaultHeaders = deepcopy(DefaultPhoSimInstanceCatalogCols)
    keepObsHistID = True

    def _remove_object(self, keepObsHistID):
        x = list(self.defaultHeaders)
        if keepObsHistID:
            x[0] = 'ObsHistID'
        else:
            x.pop(0)
        return x

    @property
    def PointHeader(self):
        x = self._remove_object(self.keepObsHistID)
        _ = list(x.remove(l) for l in ('source_pars', 'dust_pars_1a',
                                       'dust_pars_1b'))
        return x
    @property
    def numPointCols(self):
        return len(self.PointHeader)

    @property
    def numGalaxyCols(self):
        return len(self.GalaxyHeader)

    @property
    def GalaxyHeader(self):
        x = self._remove_object(self.keepObsHistID)
        ind = x.index('source_pars')
        return x[:ind] + ['a', 'b', 'pa', 'sindex'] + x[ind + 1:]

class PhoSimCentroidData(object):
    """
    Class to describe data in PhoSim centroid Files
    """
    def __init__(self, fname):
        """
        """
        self.fname = fname
        self.df = pd.read_csv(ed_csv(self.fname, skiprows=1,
                              delim_whitespace=True,
                              names=('sourceID', 'photons', 'avgX', 'avgY'))

        self.df[['sourceID', 'photons']] = self.df[['sourceID', 'photons']].astype(np.int)

        
class PhoSimInputCatalog(PhoSimHeaders):
    """
    Class to represent a phosim instance catalog data as a collection of tables.
    Currently, we expect  there to be at most three tables per PhoSim Instance
    catalog, which are available as attributes.
    
    Attributes
    ----------
    keepObsHistID : Bool, defaults to True
        Whether we should add a column of `ObsHistID` to the dataframe of
        phosim instance catalog data
    metadata : `pd.DataFrame`
        The PhoSim header information is stored as a dataframe
    pointData : `pd.DataFrame`
        The phoSim instance catalog data for sources of type 'POINT' are
        stored as a dataframe. The column in a PhoSim instance catalog with
        the word 'object' is replaced with a column of `ObsHistID` if
        `keepObsHistID` is True, If False, this column is dropped. The dataframe
        is sorted by values of uniqueID
    galaxyData : `pd.DataFrame`
        The phoSim instance catalog data for sources of type 'SERSIC2D' are
        stored as a dataframe. The column in a PhoSim instance catalog with
        the word 'object' is replaced with a column of `ObsHistID` if
        `keepObsHistID` is True, If False, this column is dropped. The dataframe
        is sorted by values of uniqueID

    Methods
    -------
    parsePhoSimInstanceCatalog
    getdata
    """
    def __init__(self, fname, checkSpectralFileNamesForEquality=True):
        """
        Parameters
        ----------
        fname : string, mandatory
            absolute path to filename of PhoSim Instance Catalog
        checkSpectralFileNamesForEquality : Bool, default to True 
            Two phosim instance catalogs may have the same data except for
            locations of where the spectral files are located (for example
            if they are on two different computers). Equality can then be
            checked by ignoring the file name column, by setting this parameter
            to be False.
        """
        self.fname = fname 
        self._data = self.parsePhoSimInstanceCatalog(self.fname)
        self.maxnumCols = self.data.columns.size - 1
        self._obshistid = None
        self.checkSpectralFileNamesForEquality = checkSpectralFileNamesForEquality

    @property
    def data(self):
        data = self._data.copy()
        data['NumNulls'] = data.isnull().sum(axis=1)
        return data
    @property
    def numNulls(self):
        return self.cats.groups.keys()

    @property
    def cats(self):
        return self.data.groupby('NumNulls')

    @staticmethod
    def parsePhoSimInstanceCatalog(fname):
        """
        parses the PhoSim Instance Catalog file to a dataframe
        """
        with open(fname, 'r') as fh:
            data = fh.read()
        maxlen = max(map(len, map(lambda x: x.split(), data.split('\n'))))
        names = list(string.ascii_lowercase[:maxlen])
        df = pd.read_csv(StringIO(data), names=names, delim_whitespace=True,
                         low_memory=False)
        return df

    @property
    def metadata(self):
        dataCols = 2
        numNulls = self.maxnumCols - dataCols
        x = self.cats.get_group(numNulls).dropna(axis=1)\
                .drop('NumNulls', axis=1).set_index('a').transpose()
        x[['nsnap', 'seed', 'filter', 'obshistid']] = x[['nsnap',
                                                         'seed',
                                                         'filter',
                                                         'obshistid']].astype(int)
        return x
    @property
    def obsHistID(self):
        if self._obshistid is None:
            self._obshistid = self.metadata.obshistid.values[0]
        return self._obshistid

    def get_data(self, dataType='point'):
        """
        Parses the PhoSim Instance Catalog records of astrophysical sources
        of a particular type. 
        dataType : {'point', 'galaxy'}
        """
        if dataType.lower() == 'point':
            headerCols = self.PointHeader
        elif dataType.lower() == 'galaxy':
            headerCols = self.GalaxyHeader

        extraCols = 1
        if self.keepObsHistID:
            extraCols = 0
        dataCols = len(headerCols) + extraCols
        numNulls = self.maxnumCols - dataCols
        if numNulls not in self.numNulls:
            print('No group of required size found')
            return None

        x = self.cats.get_group(numNulls).dropna(axis=1).copy()

        x.drop('NumNulls', axis=1, inplace=True)
        if self.keepObsHistID:
            x['a'] = self.obsHistID
        else:
            x.drop('a', axis=1, inplace=True)
        cols = x.columns

        x.rename(columns=dict(zip(cols, headerCols)), inplace=True)
        x.uniqueID = x.uniqueID.astype(np.int)
        x.sort_values(by='uniqueID')
        return x

    @property
    def galaxyData(self):
        return self.get_data(dataType='galaxy')
    @property
    def pointData(self):
        return self.get_data(dataType='point')


    def __eq__(self, other):
        """
        Defined to be equal if
        - each of the metadata, pointData, galaxyData are equal
        - each of those are equal if they are both None, or the dataframe
        on the subset of desired columns are equal (with check_exact=False)
        """
        val = copy(other.keepObsHistID)
        other.keepObsHistID = self.keepObsHistID
        metaData = False
        pointData = False
        galaxyData = False
        assert_frame_equal(other.metadata, self.metadata,
                                      check_exact=False)
        metaData = True

        val2 = copy(other.checkSpectralFileNamesForEquality) 
        if not self.checkSpectralFileNamesForEquality:
            pointHeader = deepcopy(self.PointHeader)
            pointHeader.remove('SED_NAME')
            galaxyHeader = deepcopy(self.GalaxyHeader)
            galaxyHeader.remove('SED_NAME')
            other.checkSpectralFileNamesForEquality = False
        else:
            pointHeader = self.PointHeader
            galaxyHeader = self.GalaxyHeader
            other.checkSpectralFileNamesForEquality = True

        if self.galaxyData is None:
            if other.galaxyData is None:
                galaxyData = True 
        else:
            assert_frame_equal(self.galaxyData[galaxyHeader],
                               other.galaxyData[galaxyHeader],
                               check_exact=False)
            galaxyData = True

        if self.pointData is None:
            if other.pointData is None:
                pointData = True 
        else:
            assert_frame_equal(self.pointData[pointHeader],
                               other.pointData[pointHeader],
                               check_exact=False)
            pointData = True
        other.keepObsHistID = val
        other.checkSpectralFileNamesForEquality = val2
        return metaData and pointData and galaxyData
