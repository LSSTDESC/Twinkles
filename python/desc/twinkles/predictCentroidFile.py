from __future__ import with_statement
import numpy as np
import pandas

from lsst.sims.utils import ObservationMetaData
from lsst.sims.coordUtils import pixelCoordsFromRaDec
from lsst.obs.lsstSim import LsstSimMapper
from desc.twinkles import icrsFromPhoSim

def getPredictedCentroids(cat_name):
    """
    Read in an InstanceCatalog.  Use CatSim to calculate the expected
    pixel positions of all of the sources in that InstanceCatalog.
    Return a pandas dataframe containing each source's id, xpix, and ypix
    coordinates.

    Parameters
    ----------
    cat_name is the path to the InstanceCatalog

    Returns
    -------
    a pandas dataframe with columns 'id', 'x', and 'y'
    """

    target_chip = 'R:2,2 S:1,1'

    camera = LsstSimMapper().camera

    with open(cat_name, 'r') as input_catalog:
        input_lines = input_catalog.readlines()

    ra = None
    dec = None
    mjd = None
    rotSkyPos = None
    while ra is None or dec is None or mjd is None or rotSkyPos is None:
        for line in input_lines:
            line = line.split()
            if line[0] == 'rightascension':
                ra = float(line[1])
            if line[0] == 'declination':
                dec = float(line[1])
            if line[0] == 'mjd':
                mjd = float(line[1])
            if line[0] == 'rotskypos':
                rotSkyPos = float(line[1])

    try:
        assert ra is not None
        assert dec is not None
        assert mjd is not None
        assert rotSkyPos is not None
    except:
        print 'ra: ',ra
        print 'dec: ',dec
        print 'mjd: ',mjd
        print 'rotSkyPos: ',rotSkyPos

    obs = ObservationMetaData(pointingRA=ra,
                              pointingDec=dec,
                              mjd=mjd,
                              rotSkyPos=rotSkyPos)

    id_list = []
    ra_list = []
    dec_list = []
    for line in input_lines:
        line = line.split()
        if len(line) > 2:
            id_list.append(int(line[1]))
            ra_list.append(float(line[2]))
            dec_list.append(float(line[3]))

    id_list = np.array(id_list)
    ra_list = np.array(ra_list)
    dec_list = np.array(dec_list)

    ra_icrs, dec_icrs = icrsFromPhoSim(ra_list, dec_list, obs)

    x_pix, y_pix = pixelCoordsFromRaDec(ra_icrs, dec_icrs,
                                        chipName=[target_chip]*len(id_list),
                                        #chipName=chip_name_list,
                                        obs_metadata=obs,
                                        camera=camera)

    return pandas.DataFrame({'id': id_list,
                             'x': y_pix,
                             'y': x_pix})  # need to reverse pixel order because
                                           # DM and PhoSim have different
                                           # conventions
