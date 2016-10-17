"""
This script  queries fatboy for all of the galaxies in the Twinkles
field of view and writes them to the file

$TWINKLES_DIR/data/twinkles_galaxy_cache.txt
"""

from __future__ import with_statement
from lsst.utils import getPackageDir
from lsst.sims.catUtils.baseCatalogModels import GalaxyTileObj
from lsst.sims.utils import ObservationMetaData
from desc.twinkles import _galaxy_cache_dtype

import numpy as np
import os

class GalaxyTileObjDegrees(GalaxyTileObj):
    """
    We needed to sub-class GalaxyTileObj so that we can replace
    _final_pass, which requires you to query for
    (raJ2000, decJ2000), rather than (ra, dec)
    """
    def _final_pass(self, results):
        return results

obs = ObservationMetaData(pointingRA=53.0091385,
                          pointingDec=-27.4389488,
                          boundType='circle',
                          boundLength=0.31)

db = GalaxyTileObjDegrees()

col_names = list(_galaxy_cache_dtype.names)

result_iterator = db.query_columns(colnames=col_names, chunk_size=100000,
                                   obs_metadata=obs)

file_name = os.path.join(getPackageDir('twinkles'),
                         'data', 'twinkles_galaxy_cache.txt')

with open(file_name, 'w') as output_file:
    output_file.write('# galtileid ')
    for name in col_names:
        output_file.write('%s ' % name)
    output_file.write('\n')
    for chunk in result_iterator:
        for line in chunk:
            output_file.write(('%ld;%.17g;%.17g;%s;%.17g;%s;%.17g;%s;%.17g;%s;%.17g;%.17g;'
                               % (line[0], line[1], line[2],
                                  line[3], line[4], line[5],
                                  line[6], line[7], line[8],
                                  line[9], line[10], line[11])).replace('nan', 'NULL').replace('None', 'NULL')
                               + ('%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g;%.17g'
                                  % (line[12], line[13], line[14],
                                     line[15], line[16], line[17],
                                     line[18], line[19], line[20],
                                     line[21], line[22], line[23])).replace('nan', 'NULL').replace('None', 'NULL')
                               + '\n')

