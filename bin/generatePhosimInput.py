"""
Script to run the generation of phoSim instance catalogs
"""
from __future__ import with_statement, absolute_import, division, print_function
import os
import pandas as pd
from sqlalchemy import create_engine
import time
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from desc.twinkles import TwinklesSky
import argparse



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

def generateSinglePointing(obs_metaData, availableConns, sntable,
                            fname,
                            sn_sed_file_dir):
    tstart = time.time()
    obs_metaData.boundLength = 0.3
    print(obs_metaData.summary)
    obsHistID = obs_metaData._OpsimMetaData['obsHistID']

    # all but first two are default values of optional parameters
    # Kept in script to emphasize inputs
    tSky = TwinklesSky(obs_metadata=obs_metaData,
                       availableConnections=availableConns,
                       brightestStar_gmag_inCat=11.0,
                       brightestGal_gmag_inCat=11.0,
                       sntable='TwinkSN',
                       sn_sedfile_prefix=os.path.join(sn_sed_file_dir, 'specFile_'))
    #fname = phoSimInputFileName(obsHistID)  
    if not os.path.exists(os.path.dirname(fname)):
        os.makedirs(os.path.dirname(fname))
    if not os.path.exists(sn_sed_file_dir):
        os.makedirs(sn_sed_file_dir)
    tSky.writePhoSimCatalog(fname)
    availConns = tSky.availableConnections
    tend = time.time()
    print (obsHistID, tend - tstart)


if __name__ == '__main__':
     
    parser = argparse.ArgumentParser(description='Write phoSim Instance Catalogs'
                                     'and SN spectra to disk')
    parser.add_argument('--opsimDB',
                       type=str,
                       help='OpSim database sqlite filename',
                       default='minion_1016_sqlite.db')
    parser.add_argument('visit',
                        type=int,
                        help='Visit number (obsHistID)')
    parser.add_argument('--OpSimDBDir',
                        help='absolute path to dir with the opsimBD',
                        type=str,
                        default='./')
    parser.add_argument('--outfile', type=str, default=None,
                        help='output filename for instance catalog')
    parser.add_argument('--seddir',
                        type=str,
                        default=None,
                        help='directory to contain SED files')
    args = parser.parse_args()

    # Set up OpSim database
    opSimDBPath = os.path.join(args.OpSimDBDir, args.opsimDB)
    engine = create_engine('sqlite:///' + opSimDBPath)
    
    obs_gen = ObservationMetaDataGenerator(database=opSimDBPath)
    sql_query = 'SELECT * FROM Summary WHERE ObsHistID == {}'.format(args.visit) 
    df = pd.read_sql_query(sql_query, engine)
    recs = df.to_records()
    obsMetaDataResults = obs_gen.ObservationMetaDataFromPointingArray(recs)
    obs_metaData = obsMetaDataResults[0]
    sn_sed_file_dir = os.path.join(args.seddir, 'spectra_files')
    
    availConns = None
    
    generateSinglePointing(obs_metaData,
                           availableConns=availConns,
                           sntable='TwinkSN',
                           fname=args.outfile,
                           sn_sed_file_dir=sn_sed_file_dir)
