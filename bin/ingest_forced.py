#!/usr/bin/env python
"""
Ingest into a MySQL database the forced source catalogs from a Level 2
analysis.
"""
from __future__ import print_function, absolute_import
from builtins import dict
import os
import argparse
import desc.twinkles
import desc.twinkles.db_table_access as db_table_access

description = """Ingest forced source catalogs into ForcedSource
database tables."""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('data_repo',
                    help='Output repository from Level 2 processing')
parser.add_argument('database', help='MySQL database name')
parser.add_argument('--conn_info', type=str, help='MySQL connection info file',
                    default='~/.my.cnf')

args = parser.parse_args()
db_info = dict(db=args.database, read_default_file=args.conn_info)

forced_src_table = db_table_access.ForcedSourceTable(**db_info)
visits = desc.twinkles.get_visits(args.data_repo)
for band, visit_list in visits.items():
    print("Processing band ", band, " for ", len(visit_list), " visits.")
    for ccdVisitId in visit_list:
        visit_name = 'v%i-f%s' % (ccdVisitId, band)
        #
        # @todo: Generalize this for arbitrary rafts and sensors.  This
        # will need the data butler subset method to be fixed first.
        #
        catalog = os.path.join(args.data_repo, 'forced', '0',
                               visit_name, 'R22', 'S11.fits')
        print("Processing ", visit_name)
        forced_src_table.ingestSourceCatalog(catalog, ccdVisitId)
