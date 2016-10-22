#!/usr/bin/env python
"""
Command line tool to extract obsHistIDs (visit numbers) from an OpSim db
file given a fieldID.
"""
from __future__ import absolute_import
import os
import argparse
import pandas as pd
from desc.twinkles import get_twinkles_visits
from desc.twinkles import OpSimOrdering
from lsst.utils import getPackageDir

parser = argparse.ArgumentParser(description="Write an ascii file of visits derived from an OpSim db file given a fieldID")
parser.add_argument('opsimDB', help='OpSim database sqlite file')
parser.add_argument('--fieldID', type=int, default=1427,
                    help='ID number of the desired field')
parser.add_argument('--outfile', type=str, default=None, help='output file')
parser.add_argument('--orderObsHistIDsByDesign', type=bool, default=True,
                    help='order obsHistIDs as decided for Twinkles 3')
parser.add_argument('--randomForestPickleFileName', type=str, default='RF_pickle.p',
                    help='filename for a pickle of a RandomForest Predictor of PhoSim Run times')
parser.add_argument('--randomForestPickleFileDir', type=str, default=None,
                    help='absolute path to the directory holding the RandomForest Predictor of PhoSim Run times. The default `None` expects the file at `TWINKLES_DIR/data/`')
parser.add_argument('--maxPredictedTime', type=float, default=100.0,
                    help='max predicted phosim run time for the opsim record'
                    ' in hours beyond which the record index obsHistID will '
                    'not be included') 
args = parser.parse_args()

# output filename is common
if args.outfile is None :
    args.outfile = 'twinkles_visits_fieldID_%i.txt' % args.fieldID

# Random Forest Generator Pickle:
if args.randomForestPickleFileDir is None:
    twinklesDir = getPackageDir('Twinkles')
    randomForestPickleFileDir = os.path.join(twinklesDir, 'data') 
else:
    randomForestPickleFileDir = args.randomForestPickleFileDir
randomForestPickle = os.path.join(randomForestPickleFileDir, args.randomForestPickleFileName)
if args.orderObsHistIDsByDesign:
    ops = OpSimOrdering(opSimDBPath=args.opsimDB,
                        randomForestPickle=randomForestPickle,
                        timeMax=args.maxPredictedTime)
    df = pd.concat([ops.Twinkles_3p1, ops.Twinkles_3p2, ops.Twinkles_3p3])
    df.obsHistID.to_csv(args.outfile, index=False)
else:
    obsHistIDs = get_twinkles_visits(args.opsimDB)

    with open(args.outfile, 'w') as output:
        for obsHistID in obsHistIDs:
            output.write('%s\n' % obsHistID)
