import GCRCatalogs
import astropy.io.fits as fits
import lsst.sims.photUtils as sims_photUtils
import numpy as np
import os

data_dir = os.path.join(os.environ['TWINKLES_DIR'], 'data')
assert os.path.isdir(data_dir)

# load the mapping between galaxy_id and twinklesId
# (really, I just want a list of all of the galaxies that
# are getting replaced, so that I can get their redshifts from
# the GCR)
gal_to_twink_file = os.path.join(data_dir, 'cosmoDC2_v1.1.4_agn_cache.csv')
assert os.path.isfile(gal_to_twink_file)
gal_to_twink_dtype = np.dtype([('galaxy_id', int), ('twinkles_id', int)])
gal_to_twink = np.genfromtxt(gal_to_twink_file,
                             dtype=gal_to_twink_dtype,
                             delimiter=',', skip_header=1)


gcr_cat = GCRCatalogs.load_catalog('cosmoDC2_v1.1.4_image')
gcr_cat_q = gcr_cat.get_quantities(['galaxy_id', 'redshift_true'])

overlap = np.where(np.in1d(gcr_cat_q['galaxy_id'], gal_to_twink['galaxy_id']))

galaxy_id = gcr_cat_q['galaxy_id'][overlap]
redshift = gcr_cat_q['redshift_true'][overlap]

fits_file_name = os.path.join(data_dir, 'cosmoDC2_v1.1.4_matched_AGN.fits')
assert os.path.isfile(fits_file_name)

twinkles_data = fits.open(fits_file_name)[1].data

sed_dir = os.environ['SIMS_SED_LIBRARY_DIR']
bp_dict = sims_photUtils.BandpassDict.loadTotalBandpassesFromFiles()

dust_wav = None
max_dmag = -1.0
with open('i_mag_validation.txt', 'w') as out_file:
    out_file.write('# g_id is shld d z\n')
    for idx in range(len(twinkles_data['twinklesId'])):
        t_id = twinkles_data['twinklesId'][idx]
        sed_name = twinkles_data['lens_sed'][idx]
        i_magnorm = twinkles_data['sed_magNorm'][idx][3]
        apmag_i = twinkles_data['APMAG_I'][idx]
        av = twinkles_data['lens_av'][idx]
        rv = twinkles_data['lens_rv'][idx]

        valid = np.where(gal_to_twink['twinkles_id']==t_id)[0]
        g_id = gal_to_twink['galaxy_id'][valid]
        valid = np.where(galaxy_id==g_id)[0]
        zz = redshift[valid]

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
        abs_d_mag = np.abs(i_mag-apmag_i)
        if abs_d_mag > max_dmag:
            print('d_mag %e: is %e shld %e' % (d_mag, i_mag, apmag_i))
            max_dmag = abs_d_mag
        out_file.write('%d %e %e %e %e\n' % (g_id, i_mag, apmag_i, d_mag, zz))
