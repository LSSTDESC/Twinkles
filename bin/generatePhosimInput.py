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

# Choose OpSim Output database
OpSimDB = 'minion_1016_sqlite.db'
# Combine the environment variable setup using `source setup/setup_locations.sh`
# after modifying the variable
opSimDBPath = os.path.join(os.environ['OpSimDir'], OpSimDB)
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
# of obsHistID (remove limit 4 part of the query
df = pd.read_sql_query('SELECT * FROM Summary WHERE FieldID == 1427 and propID in (54, 56) limit 4', engine).drop_duplicates(subset='obsHistID')
sql_query = _sql_constraint(obsHistIDList)
# Use if you want to use a list of obsHistIDs
# df = pd.read_sql_query(sql_query, engine)
recs = df.to_records()
obsMetaDataResults = []
obsMetaDataResults = obs_gen.ObservationMetaDataFromPointingArray(recs)
sn_sed_file_dir = 'spectra_files'

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
                       brightestGal_gmag_inCat=11.0,
                       sntable='TwinkSN',
                       sn_sedfile_prefix=os.path.join(sn_sed_file_dir, 'specFile_'))
    fname = phoSimInputFileName(obsHistID)  
    if not os.path.exists(os.path.dirname(fname)):
        os.makedirs(os.path.dirname(fname))
    if not os.path.exists(os.path.dirname(sn_sed_file_dir)):
        os.makedirs(sn_sed_file_dir)
    tSky.writePhoSimCatalog(fname)
    availConns = tSky.availableConnections
    tend = time.time()
    print (obsHistID, tend - tstart)
