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
parser.add_argument('--orderObsHistID', type=bool, default=True,
                    help='order obsHistIDs as decided for Twinkles 3')
parser.add_argument('--RF_pickle_file', type=str, default=None,
                    help='absolute path for a pickle of a RandomForest Predictor of PhoSim Run times, defaults to None which effectively sets the variable to Twinkles/data/RF_pickle.p')
parser.add_argument('--maxPredTime', type=float, default=100.0,
                    help='max predicted phosim run time for the opsim record'
                    ' in hours beyond which the record index obsHistID will '
                    'not be included')
args = parser.parse_args()

# output filename is common
if args.outfile is None:
    args.outfile = 'twinkles_visits_fieldID_%i.txt' % args.fieldID

# Random Forest Generator Pickle:
if args.RF_pickle_file is None:
    twinklesDir = getPackageDir('Twinkles')
    randomForestPickle = os.path.join(twinklesDir, 'data', 'RF_pickle.p')
else:
    randomForestPickle = args.RF_pickle_file

if args.orderObsHistID:
    ops = OpSimOrdering(opSimDBPath=args.opsimDB,
                        randomForestPickle=randomForestPickle,
                        timeMax=args.maxPredTime)
    with open(args.outfile, 'w') as output:
        output.write('# Begin Section Twinkles 3.1\n')
    ops.Twinkles_3p1.obsHistID.to_csv(args.outfile, index=False, mode='a')
    with open(args.outfile, 'a') as output:
        output.write('# Begin Section Twinkles 3.2\n')
    ops.Twinkles_3p2.obsHistID.to_csv(args.outfile, index=False, mode='a')
    with open(args.outfile, 'a') as output:
        output.write('# Begin Section Twinkles 3.3\n')
    ops.Twinkles_3p3.obsHistID.to_csv(args.outfile, index=False, mode='a')
    print("Left out {0} visits due to"
          "the time limit of {1}".format(len(ops.obsHistIDsPredictedToTakeTooLong),
                                         args.maxPredTime))
else:
    obsHistIDs = get_twinkles_visits(args.opsimDB)

    with open(args.outfile, 'w') as output:
        for obsHistID in obsHistIDs:
            output.write('%s\n' % obsHistID)
