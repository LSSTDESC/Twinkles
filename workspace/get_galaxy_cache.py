from __future__ import with_statement
from lsst.sims.catUtils.baseCatalogModels import GalaxyTileObj
from lsst.sims.utils import ObservationMetaData

import numpy as np

class GalaxyTileObjDegrees(GalaxyTileObj):

    def _final_pass(self, results):
        return results

obs = ObservationMetaData(pointingRA=53.0091385,
                          pointingDec=-27.4389488,
                          boundType='circle',
                          boundLength=0.1)

db = GalaxyTileObjDegrees()

col_names = ['galtileid', 'ra', 'dec', 'sedname_disk', 'magnorm_disk',
             'sedname_bulge', 'magnorm_bulge', 'sedname_agn', 'magnorm_agn',
             'varParamStr', 'redshift', 'g_ab']

result_iterator = db.query_columns(colnames=col_names, chunk_size=100000,
                                   obs_metadata=obs)

with open('twinkles_galaxy_cache.txt', 'w') as output_file:
    output_file.write('# ')
    for name in col_names:
        output_file.write('%s ' % name)
    output_file.write('\n')
    for chunk in result_iterator:
        for line in chunk:
            output_file.write(('%ld %.9f %.9f %s %.9f %s %.9f %s %.9f %s %.9f %.9f\n'
                               % (line[0], line[1], line[2],
                                  line[3], line[4], line[5],
                                  line[6], line[7], line[8],
                                  line[9], line[10], line[11])).replace('nan', 'NULL').replace('None', 'NULL'))

