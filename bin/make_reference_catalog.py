#!/usr/bin/env python
from __future__ import absolute_import
import argparse
import numpy
from lsst.sims.catalogs.measures.instance import InstanceCatalog
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from lsst.sims.catUtils.mixins import AstrometryStars, PhotometryStars

class TwinklesReference(InstanceCatalog, AstrometryStars, PhotometryStars):
    catalog_type = 'twinkles_ref_star'
    column_outputs = ['uniqueId', 'raJ2000', 'decJ2000', 'lsst_g',
                      'lsst_r', 'lsst_i', 'starnotgal',
                      'isvariable']
    default_columns = [('isresolved', 0, int), ('isvariable', 0, int)]
    default_formats = {'S': '%s', 'f': '%.8f', 'i': '%i'}
    transformations = {'raJ2000': numpy.degrees, 'decJ2000': numpy.degrees}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the reference catalog')
    parser.add_argument('opsimDB', help='OpSim database sqlite file')
    parser.add_argument('-o', '--outfile', type=str, default='twinkles_ref.txt',
                        help='Filename of output reference catalog')
    args = parser.parse_args()

    # you need to provide ObservationMetaDataGenerator with the connection
    # string to an OpSim output database.  This is the connection string
    # to a test database that comes when you install CatSim.
    generator = ObservationMetaDataGenerator(database=args.opsimDB,
                                             driver='sqlite')
    obsMetaDataResults = generator.getObservationMetaData(fieldRA=(53, 54), fieldDec=(-29, -27), boundLength=0.3)

    # First get the reference catalog
    stars = CatalogDBObject.from_objid('allstars')
    while True:
        try:
            ref_stars = TwinklesReference(stars, obs_metadata=obsMetaDataResults[0])
            break
        except RuntimeError:
            continue
    ref_stars.write_catalog(args.outfile, write_mode='w', write_header=True,
                            chunk_size=20000)
