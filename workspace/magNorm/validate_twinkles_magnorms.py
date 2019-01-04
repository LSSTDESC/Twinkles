import astropy.io.fits as fits
import lsst.sims.photUtils as sims_photUtils
import numpy as np
import os

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--fits_file', type=str)
args = parser.parse_args()

assert os.path.isfile(args.fits_file)

twinkles_data = fits.open(args.fits_file)[1].data

sed_dir = os.environ['SIMS_SED_LIBRARY_DIR']
bp_dict = sims_photUtils.BandpassDict.loadTotalBandpassesFromFiles()

dust_wav = None
max_dmag = -1.0
with open('i_mag_validation.txt', 'w') as out_file:
    out_file.write('# g_id is shld d z\n')
    for idx in range(len(twinkles_data['lens_sed'])):
        sed_name = twinkles_data['lens_sed'][idx]
        i_magnorm = twinkles_data['sed_magNorm'][idx][3]
        apmag_i = twinkles_data['APMAG_I'][idx]
        av = twinkles_data['lens_av'][idx]
        rv = twinkles_data['lens_rv'][idx]

        zz = twinkles_data['ZLENS'][idx]

        spec = sims_photUtils.Sed()
        full_file_name = os.path.join(sed_dir, sed_name)
        spec.readSED_flambda(full_file_name)
        fnorm = sims_photUtils.getImsimFluxNorm(spec, i_magnorm)
        spec.multiplyFluxNorm(fnorm)
        if dust_wav is None or not np.array_equal(spec.wavelen, dust_wav):
            dust_wav = np.copy(spec.wavelen)
            a_x, b_x = spec.setupCCM_ab()
        spec.addDust(a_x, b_x, A_v=av, R_v=rv)
        spec.redshiftSED(zz, dimming=True)
        i_mag = spec.calcMag(bp_dict['i'])
        d_mag = i_mag-apmag_i
        if twinkles_data['LENSID'][idx] == 180815:
            print(i_mag,apmag_i,d_mag)
        abs_d_mag = np.abs(i_mag-apmag_i)
        if abs_d_mag > max_dmag:
            print('d_mag %e: is %e shld %e' % (d_mag, i_mag, apmag_i))
            max_dmag = abs_d_mag
        out_file.write('%e %e %e %e\n' % (i_mag, apmag_i, d_mag, zz))
