from __future__ import absolute_import, division, print_function
import numpy as np
from lsst.sims.catUtils.exampleCatalogDefinitions \
    import DefaultPhoSimInstanceCatalogCols
from cStringIO import StringIO
import string
import pandas as pd
from collections import OrderedDict as odict
from pandas.util.testing import assert_frame_equal
from copy import deepcopy

__all__ = ['PhoSimInputCatalog', 'PhoSimHeaders']

class PhoSimHeaders:
    """
    Class supplying headers for different phoSim catalogs

    Attributes
    ----------
    keepObsHistID : Bool, defaults to True
        keep first column 'ObsHistID' instead of 'object'
    PointHeader :  
    GalaxyHeader :  
    numPointCols :
    numGalaxyCols :
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
    Class to represent a phosim instance catalog data as a collection of tables
    """
    def __init__(self, fname, checkSpectralFileNamesForEquality=False):
        self.fname = fname 
        self._data = self.parsePhoSimInstanceCatalog(self.fname)
        # with NumNulls, self.data has samenumber of columns as the original
        # data
        self.maxnumCols = self.data.columns.size - 1
        #self.activeCols = self.maxnumCols - np.array(self.numNulls)
        self._obshistid = None
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
        x[['nsnap', 'seed', 'filter', 'obshistid']] = x[['nsnap', 'seed', 'filter',
                                                         'obshistid']].astype(int)
        return x
    @property
    def obsHistID(self):
        return self.metadata.obshistid.values[0]

    def _get_data(self, dataType='point'):
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
        x = self.cats.get_group(numNulls).dropna(axis=1).copy()

        x.drop('NumNulls', axis=1, inplace=True)
        if self.keepObsHistID:
            x['a'] = self.obsHistID
        else:
            x.drop('a', axis=1, inplace=True)
        cols = x.columns

        x.rename(columns=dict(zip(cols, self.PointHeader)), inplace=True)
        return x

    def _remove_extracols(self, df):
        df.drop('NumNulls', axis=1, inplace=True)
        if self.keepObsHistID:
            df['a'] = self.obsHistID
        else:
            df.drop('a', axis=1, inplace=True)
        cols = df.columns
        return cols, df

    @property
    def galaxyData(self):
        return self._get_data(dataType='galaxy')
    @property
    def pointData(self):
        return self._get_data(dataType='point')
    @property
    def _pointData(self):
        # extraCols = 0
        # if self.keepObsHistID:
        #    extraCols = 1
        dataCols = len(self.PointHeader) # - extraCols
        numNulls = self.maxnumCols - dataCols
        x = self.cats.get_group(numNulls).dropna(axis=1).copy()
        cols, x = self._remove_extracols(x) 
        x.rename(columns=dict(zip(cols, self.PointHeader)), inplace=True)
        return x

    @property
    def __galaxyData(self):
        dataCols = len(self.GalaxyHeader) # - extrCols
        numNulls = self.maxnumCols - dataCols
        x = self.cats.get_group(numNulls).dropna(axis=1).copy()
        cols, x = self._remove_extracols(x) 
        x.rename(columns=dict(zip(cols, self.PointHeader)), inplace=True)

        if self.keepObsHistID:
            x['a'] = self.obsHistID
        x.drop('NumNulls', axis=1)
        x.rename(columns=dict(zip(pc.GalaxyHeader, pc.pointData.columns)),
                 inplace=True)
        return x

if __name__ == '__main__':
    pc = PhoSimInputCatalog('testScript.dat')
    df = pc.parse_phosimInstanceCatalogs('testScript.dat')
    print(df)
