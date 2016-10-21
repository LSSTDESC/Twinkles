#!/usr/bin/env python
"""
Command line tool to extract obsHistIDs (visit numbers) from an OpSim db
file given a fieldID.
"""
from __future__ import absolute_import
import argparse
from desc.twinkles import get_twinkles_visits

parser = argparse.ArgumentParser(description="Write an ascii file of visits derived from an OpSim db file given a fieldID")
parser.add_argument('opsimDB', help='OpSim database sqlite file')
parser.add_argument('--fieldID', type=int, default=1427,
                    help='ID number of the desired field')
parser.add_argument('--outfile', type=str, default=None, help='output file')
args = parser.parse_args()

obsHistIDs = get_twinkles_visits(args.opsimDB)
if args.outfile is None:
    args.outfile = 'twinkles_visits_fieldID_%i.txt' % args.fieldID

with open(args.outfile, 'w') as output:
    for obsHistID in obsHistIDs:
        output.write('%s\n' % obsHistID)
