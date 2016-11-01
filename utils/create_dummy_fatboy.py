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
    cur = conn.cursor()
    cur.execute('''CREATE TABLE StarAllForceSeek
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
                 %d, %.12g, %.12g, %.12g, %.12g, %.12g, %.12g, %.12g, %.12g, 'None', '%s', 15.0)''' % \
                 (ix, ra, dec, norm, mura, mudecl, px, ebv, vrad, star_seds[sed])
        cur.execute(cmd)
    conn.commit()


    cur.execute('''CREATE TABLE TwinkSN_run3
                 (snra real, sndec real, t0 real, x0 real, x1 real, c real, redshift real,
                  galtileid int, id int)''')

    n_sn = 100
    rr = rng.random_sample(n_sn)*radius
    theta = rng.random_sample(n_sn)*2.0*np.pi
    snra_list = ra + rr*np.cos(theta)
    sndec_list = dec + rr*np.sin(theta)
    t0_list = rng.random_sample(n_sn)
    x0_list = rng.random_sample(n_sn)*1.0e-5+1.0e-6
    x1_list = rng.random_sample(n_sn)*5.0
    c_list = rng.random_sample(n_sn)*5.0
    redshift_list = rng.random_sample(n_sn)*1.1 + 0.1
    for ix, (snra, sndec, t0, x0, x1, c, redshift) in \
    enumerate(zip(snra_list, sndec_list, t0_list, x0_list, x1_list, c_list, redshift_list)):
        cmd = '''INSERT INTO TwinkSN_run3
                 VALUES (%.12g, %.12g, %.12g, %12.g, %.12g, %.12g, %.12g, %d,%d)''' % \
                 (snra, sndec, t0, x0, x1, c, redshift, ix, ix)
        cur.execute(cmd)
    conn.commit()
    conn.close()
