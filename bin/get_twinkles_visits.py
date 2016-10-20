#!/usr/bin/env python
"""
Command line tool to extract obsHistIDs (visit numbers) from an OpSim db
file given a fieldID.
"""
from __future__ import absolute_import
import argparse
from desc.twinkles import get_twinkles_visits
from desc.twinkles import OpSimOrdering

parser = argparse.ArgumentParser(description="Write an ascii file of visits derived from an OpSim db file given a fieldID")
parser.add_argument('opsimDB', help='OpSim database sqlite file')
parser.add_argument('--fieldID', type=int, default=1427,
                    help='ID number of the desired field')
parser.add_argument('--outfile', type=str, default=None, help='output file')
parser.add_argument('--orderObsHistIDsByDesign', type=bool, default=True,
                    help='order obsHistIDs as decided for Twinkles 3')
parser.add_argument('--maxPredictedTime', type=float, default=120.0,
                    help='max predicted phosim run time for the opsim record'
                    ' in hours beyond which the record index obsHistID will '
                    'not be included') 
args = parser.parse_args()

# output filename is common
if args.outfile is None:
    args.outfile = 'twinkles_visits_fieldID_%i.txt' % args.fieldID

if args.orderObsHistIDsByDesign:
    ops = OpSimOrdering(args.opsimDB, timeMax=args.maxPredictedTime)
    df = pd.concat([ops.Twinkles_3p1, ops.Twinkles_3p2, ops.Twinkles_3p3])
    df.obsHistID.to_csv(args.outfile, index=False)
else:
    obsHistIDs = get_twinkles_visits(args.opsimDB)

    with open(args.outfile, 'w') as output:
        for obsHistID in obsHistIDs:
            output.write('%s\n' % obsHistID)
