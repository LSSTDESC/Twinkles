"""
Write out csv files with obsHistIDs corresponding to visits in yearly releases
and coadds. Check description of these releases and coadds in Issue #454  of
the Twinkles repository
"""
from __future__ import absolute_import, print_function
import argparse
import numpy as np
import os
from desc.twinkles import OpSimOrdering
from lsst.utils import getPackageDir
twinklesDir = getPackageDir('Twinkles')


parser = argparse.ArgumentParser(description="Write ascii files of visits in each of the Twinkles yearly data releases and coadds") 
parser.add_argument('opsimDB', help='absolute path to OpSim database sqlite file')
parser.add_argument('outputDir', help='output directory to write stuff out to, and the directory is assumed to exist')
parser.add_argument('--release_type', help='combination of visits which should be WFD or Combined', type=str, default='Combined')
args = parser.parse_args()

df = OpSimOrdering.fullOpSimDF(opsimdbpath=args.opsimDB)

# Do what is done in uniqueOpSimRecords
df.drop_duplicates(keep='first', subset='obsHistID', inplace=True)

df['year'] = df.night // 365
df['year'] = df.year.astype(np.int)

print(' Will write out obsHistIDs\n')
release_type = args.release_type
for year in np.sort(df.year.unique()):
    release_name = os.path.join(args.outputDir, 
                                'year_{0:02d}_Release_{1}.csv'.format(year + 1, release_type))
    coadd_name  = os.path.join(args.outputDir,
                               'year_{0:02d}_Coadds_{1}.csv'.format(year + 1, release_type ))
    templates_name  = os.path.join(args.outputDir,
                                  'year_{0:02d}_DIAvisits.csv'.format(year + 1 ))
    df.query('year == @year').obsHistID.to_csv(release_name, index=False)
    df.query('year <= @year').obsHistID.to_csv(coadd_name, index=False)
    df.query('year < @year').obsHistID.to_csv(templates_name, index=False)
