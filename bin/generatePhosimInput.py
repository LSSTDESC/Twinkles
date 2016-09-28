"""
Script to run the generation of phoSim instance catalogs
"""
from __future__ import with_statement, absolute_import, division, print_function
import os
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from desc.twinkles import TwinklesSky
import argparse
import pandas as pd
from sqlalchemy import create_engine
import time

opSimDBPath = '/Users/rbiswas/data/LSST/OpSimData/minion_1016_sqlite.db'
engine = create_engine('sqlite:///' + opSimDBPath)
obsHistIDList =  [230]

def phoSimInputFileName(obsHistID,
                        prefix='InstanceCatalogs/PhoSim_input',
                        suffix='.txt',
                        location='./'):
    """
    function to return the absolute path to a filename for writing the phoSim
    input corresponding to obsHistID.

    Parameters
    ----------
    prefix : string, optional
    suffix : string, optional, defaults to '.txt'
    location : string, optional, defaults to './'
    """

    return os.path.join(location, prefix + '_{}'.format(obsHistID) + suffix)

def _sql_constraint(obsHistIDList):
    """
    sql constraint to get OpSim pointing records for a list of obsHistID

    Parameters
    ----------
    obsHistIDList : list of integers, mandatory
        list of obsHistIDs of interest
    """
    sql_string = 'SELECT * FROM Summary WHERE ObsHistID in ('
    sql_string += ', '.join(map(str, obsHistIDList))
    sql_string += ')'
    return sql_string

obs_gen = ObservationMetaDataGenerator(database=opSimDBPath)

# Read in all of the OpSim records relevant for Twinkles or from a list
# of obsHistID
# df = pd.read_sql_query('SELECT * FROM Summary WHERE FieldID == 1427', engine)
sql_query = _sql_constraint(obsHistIDList)
df = pd.read_sql_query(sql_query, engine)
recs = df.to_records()
obsMetaDataResults = []
obsMetaDataResults = obs_gen.ObservationMetaDataFromPointingArray(recs)

availConns = None
for obs_metaData in obsMetaDataResults:
    tstart = time.time()
    obs_metaData.boundLength = 0.3
    print(obs_metaData.summary)
    obsHistID = obs_metaData._OpsimMetaData['obsHistID']

    # all but first two are default values of optional parameters
    # Kept in script to emphasize inputs
    tSky = TwinklesSky(obs_metadata=obs_metaData,
                       availableConnections=availConns,
                       brightestStar_gmag_inCat=11.0,
                       brightestGal_gmag_inCat=1.0,
                       sntable='TwinkSN',
                       sn_sedfile_prefix='spectra_files/specFile_')
    fname = phoSimInputFileName(obsHistID)  
    if not os.path.exists(os.path.dirname(fname)):
        os.makedirs(os.path.dirname(fname))
    tSky.writePhoSimCatalog(fname)
    availConns = tSky.availableConnections
    tend = time.time()
    print (obsHistID, tend - tstart)
