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
args = parser.parse_args()

df = OpSimOrdering.fullOpSimDF(opsimdbpath=args.opsimDB)

df['year'] = df.night // 365
df['year'] = df.year.astype(np.int)

print(' Will write out obsHistIDs\n')
for year in np.sort(df.year.unique()):
    release_name = os.path.join(args.outputDir, 
                                'year_{}_Release.csv'.format(year + 1))
    coadd_name  = os.path.join(args.outputDir,
                               'year_{}_Coadds.csv'.format(year + 1 ))
    df.query('year == @year').obsHistID.to_csv(release_name, index=False)
    df.query('year <= @year').obsHistID.to_csv(coadd_name, index=False)
