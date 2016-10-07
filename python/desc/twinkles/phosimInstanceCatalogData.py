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

__all__ = ['PhoSimInputCatalog', 'PhoSimHeaders']

class PhoSimHeaders:
    """
    Class for headers for different phoSim catalogs. The values of
    the attributes change depending on the value of `keepObsHistID`.
    For `keepObsHistID=True`, The 'object' column is replaced by `ObsHistID`.
    If this is False, the object column is dropped.

    Attributes
    ----------
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
    """
    def __init__(self, fname, checkSpectralFileNamesForEquality=False):
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
        return self.metadata.obshistid.values[0]

    def get_data(self, dataType='point'):
        """
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
        val = copy(other.keepObsHistID)
        other.keepObsHistID = self.keepObsHistID
        metadata = False
        pointData = False
        galaxyData = False
        metadata = assert_frame_equal(other.metadata, self.metadata,
                                      check_exact=False)

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
            print('testing ', galaxyHeader, self.galaxyData.columns)
            galaxyData = assert_frame_equal(self.galaxyData[galaxyHeader],
                                            other.galaxyData[galaxyHeader],
                                            check_exact=False)


        if self.pointData is None:
            if other.pointData is None:
                pointData = True 
        else:
            pointData = assert_frame_equal(self.pointData[pointHeader],
                                           other.pointData[pointHeader],
                                           check_exact=False)
        other.keepObsHistID = val
        other.checkSpectralFileNamesForEquality = val2
        return metaData and pointData and galaxyData
if __name__ == '__main__':
    pc = PhoSimInputCatalog('testScript.dat')
    df = pc.parse_phosimInstanceCatalogs('testScript.dat')
    print(df)
