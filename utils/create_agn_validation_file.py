import os
import numpy as np

from lsst.sims.catalogs.definitions import InstanceCatalog
from desc.sims.GCRCatSimInterface import agnDESCQAObject_protoDC2
from lsst.sims.utils import ObservationMetaData

class VarParCat(InstanceCatalog):

    """
    Quick test catalog to get AGN variability parameters
    out of the catalog.
    """

    column_outputs = ['galaxy_id', 'raJ2000', 'decJ2000',
                      'magNorm', 'redshift', 'varParamStr']

    cannot_be_null = ['magNorm']

    transformations = {'raJ2000': np.degrees,
                       'decJ2000': np.degrees}

if __name__ == "__main__":

    """
    This script can just be run from the command line as:
      python create_agn_validation_file.py
    after a version of the DESC stack with Twinkles is
    setup. 

    The goal of this script is to create a quick catalog
    of the uDDF field with the AGN variability parameters
    of the objects in the uDDF field. This is then used
    to test that the sprinkled instance catalogs are using
    the correct variability in AGN magnitudes.
    """

    field_ra = 55.064
    field_dec = -29.783
    pointing_ra = 53.125
    pointing_dec = -28.100

    db = agnDESCQAObject_protoDC2(yaml_file_name='proto-dc2_v3.0')

    agn_db_name = os.path.join(os.environ['SCRATCH'], 'proto_dc2_agn',
                               'test_agn.db')

    assert os.path.exists(agn_db_name)

    db.agn_params_db = agn_db_name
    db.field_ra = field_ra
    db.field_dec = field_dec

    obs = ObservationMetaData(pointingRA=pointing_ra,
                              pointingDec=pointing_dec,
                              boundType='circle',
                              boundLength=1.0)

    cat = VarParCat(db, obs_metadata=obs)
    validation_filename = os.path.join(os.environ['TWINKLES_DIR'],
                                       'data', 'agn_validation_params.txt')
    with open(validation_filename, 'w') as f:
        f.write('#galaxy_id, raJ2000, decJ2000, magNorm, redshift, varParamStr\n')
        for line in cat.iter_catalog():
            for i in line:
                f.write(str(str(i) + ';'))
            f.write('\n')
            
