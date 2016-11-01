import numpy as np
import os
import sqlite3

def createDummyFatboy(file_name):
    ra=53.0091385
    dec=-27.4389488
    rng = np.random.RandomState(112)
    radius = 0.31
    n_stars = 10000
    star_seds = ['km20_5750.fits_g40_5790', 'm2.0Full.dat', 'bergeron_6500_85.dat_6700']
    if os.path.exists(file_name):
        raise RuntimeError("Cannot create %s; it already exists" % file_name)

    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE StarAllForceSeek
                 (simobjid int, ra real, decl real, magNorm real, mura real, mudecl real,
                  parallax real, ebv real, vrad real, varParamStr text, sedfilename text, gmag real)''')

    rr = rng.random_sample(n_stars)*radius
    theta = rng.random_sample(n_stars)*np.pi*2.0
    ra_list = ra + rr*np.cos(theta)
    dec_list = dec + rr*np.sin(theta)
    mag_norm_list = rng.random_sample(n_stars)*7.0 + 15.0
    mura_list = rng.random_sample(n_stars)*30.0
    mudecl_list = rng.random_sample(n_stars)*30.0
    px_list = rng.random_sample(n_stars)*10.0
    ebv_list = rng.random_sample(n_stars)*7.0
    vrad_list = rng.random_sample(n_stars)*100.0
    sed_dex_list = rng.randint(0,3,n_stars)
    for ix, (ra, dec, norm, mura, mudecl, px, ebv, vrad, sed) in \
    enumerate(zip(ra_list, dec_list, mag_norm_list, mura_list, mudecl_list, px_list, ebv_list,
                  vrad_list, sed_dex_list)):

        cmd = '''INSERT INTO StarAllForceSeek VALUES(
                 %d, %f, %f, %f, %f, %f, %f, %f, %f, 'None', '%s', 15.0)''' % \
                 (ix, ra, dec, norm, mura, mudecl, px, ebv, vrad, star_seds[sed])
        c.execute(cmd)
    conn.commit()
    conn.close()

