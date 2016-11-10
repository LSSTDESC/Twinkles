from __future__ import with_statement
import sys
import numpy as np

from lsst.sims.utils import ObservationMetaData
from lsst.sims.coordUtils import chipNameFromRaDec, pixelCoordsFromRaDec
from lsst.obs.lsstSim import LsstSimMapper
from desc.twinkles import icrsFromPhoSim
import time

if __name__ == "__main__":

    t_start = time.time()
    cat_name = sys.argv[1]
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
    #chip_name_list = chipNameFromRaDec(ra_icrs, dec_icrs,
    #                                   obs_metadata=obs, camera=camera).astype(str)

    #on_chip_dexes = np.where(np.char.rfind(chip_name_list, target_chip)==0)
    #print len(chip_name_list)
    #print len(on_chip_dexes[0])

    #ra_icrs = ra_icrs[on_chip_dexes]
    #dec_icrs = dec_icrs[on_chip_dexes]
    #chip_name_list = chip_name_list[on_chip_dexes]
    #id_list = id_list[on_chip_dexes]
    x_pix, y_pix = pixelCoordsFromRaDec(ra_icrs, dec_icrs,
                                        chipName=[target_chip]*len(id_list),
                                        #chipName=chip_name_list,
                                        obs_metadata=obs,
                                        camera=camera)

    with open('test_centroid.txt', 'w') as output_file:
        for ii, xx, yy in zip(id_list, x_pix, y_pix):
            output_file.write('%ld %.12g %.12g\n' % (ii, yy, xx))  # reverse order of x,y
                                                                   # because DM and PhoSim
                                                                   # conventions don't agree

    print 'that took ',time.time()-t_start

