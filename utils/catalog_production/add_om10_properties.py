import numpy as np
import urllib
import os
from sklearn.cross_validation import train_test_split
from astroML.plotting import setup_text_plots
import empiriciSN
from MatchingLensGalaxies_utilities import *
from astropy.io import fits
import GCRCatalogs
import pandas as pd
from GCR import GCRQuery
sys.path.append('/global/homes/b/brycek/DC2/sims_GCRCatSimInterface/workspace/sed_cache/')
from SedFitter import sed_from_galacticus_mags
from lsst.sims.photUtils import Sed, Bandpass, BandpassDict


def get_sl2s_data():
    filename = '../../data/SonnenfeldEtal2013_Table3.csv'
    ! wc -l $filename

    z = np.array([])
    z_err = np.array([])
    v_disp = np.array([])
    v_disp_err = np.array([])
    r_eff = np.array([])
    r_eff_err = np.array([])
    log_m = np.array([])
    log_m_err = np.array([])
    
    infile = open(filename, 'r')
    inlines = infile.readlines()
    
    for line1 in inlines:
        if line1[0] == '#': continue
        line = line1.split(',')
        
        #Params
        z = np.append(z, float(line[1]))
        v_disp = np.append(v_disp, float(line[2]))
        r_eff = np.append(r_eff, float(line[3]))
        log_m = np.append(log_m, float(line[4]))
        
        #Errors
        z_err = np.append(z_err, float(line[5]))
        v_disp_err = np.append(v_disp_err, float(line[6]))
        r_eff_err = np.append(r_eff_err, float(line[7]))
        log_m_err = np.append(log_m_err, float(line[8]))
    
    #Build final arrays
    X = np.vstack([z, v_disp, r_eff, log_m]).T
    Xerr = np.zeros(X.shape + X.shape[-1:])
    diag = np.arange(X.shape[-1])
    
    Xerr[:, diag, diag] = np.vstack([z_err**2, v_disp_err**2,
                                    r_eff_err**2, log_m_err**2]).T
    
    return X, Xerr


#Write new conditioning function
def get_log_m(cond_indices, m_index, X, model_file, Xerr=None):
    
    """
        Uses a subset of parameters in the given data to condition the
        model and return a sample value for log(M/M_sun).

        Parameters
        ----------
        cond_indices: array_like
            Array of indices indicating which parameters to use to
            condition the model. 
        m_index: int
            Index of log(M/M_sun) in the list of parameters that were used
            to fit the model.
        X: array_like, shape = (n < n_features,)
            Input data.
        Xerr: array_like, shape = (X.shape,) (optional)
            Error on input data. If none, no error used to condition.

        Returns
        -------
        log_m: float
            Sample value of log(M/M_sun) taken from the conditioned model.

        Notes
        -----
        The fit_params array specifies a list of indices to use to
        condition the model. The model will be conditioned and then
        a mass will be drawn from the conditioned model.

        This is so that the mass can be used to find cosmoDC2 galaxies
        to act as hosts for OM10 systems.

        This does not make assumptions about what parameters are being
        used in the model, but does assume that the model has been
        fit already.
    """

    if m_index in cond_indices:
        raise ValueError("Cannot condition model on log(M/M_sun).")

    cond_data = np.array([])
    if Xerr is not None: cond_err = np.array([])
    m_cond_idx = m_index
    n_features = empiricist.XDGMM.mu.shape[1]
    j = 0

    for i in range(n_features):
        if i in cond_indices:
            cond_data = np.append(cond_data,X[j])
            if Xerr is not None: cond_err = np.append(cond_err, Xerr[j])
            j += 1
            if i < m_index: m_cond_idx -= 1
        else:
            cond_data = np.append(cond_data,np.nan)
            if Xerr is not None: cond_err = np.append(cond_err, 0.0)

    if Xerr is not None:
        cond_XDGMM = empiricist.XDGMM.condition(cond_data, cond_err)
    else: cond_XDGMM = empiricist.XDGMM.condition(cond_data)

    sample = cond_XDGMM.sample()
    log_m = sample[0][m_cond_idx]
    return log_m


def estimate_stellar_masses_om10():

    # Instantiate an empiriciSN worker object:
    empiricist = empiriciSN.Empiricist()
    X, Xerr = get_sl2s_data()

    # Load in cached om10 catalog
    hdulist = fits.open('../../data/om10_qso_mock.fits')
    twinkles_lenses = hdulist[1].data

    # Predict a mass for each galaxy:
    np.random.seed(0)
    cond_indices = np.array([0,1])
    twinkles_log_m_1comp = np.array([])

    model_file='demo_model.fit'
    empiricist.fit_model(X, Xerr, filename = 'demo_model.fit', n_components=1)
    twinkles_data = np.array([twinkles_lenses['ZLENS'], twinkles_lenses['VELDISP']]).T
    
    for x in twinkles_data:
        log_m = get_log_m(cond_indices, 2, x[cond_indices], model_file)
        twinkles_log_m_1comp = np.append(twinkles_log_m_1comp,log_m)
    
    return twinkles_lenses, log_m, twinkles_log_m_1comp


def get_catalog(catalog, twinkles_lenses, twinkles_log_m_1comp):

    gcr_om10_match = []
    err = 0
    np.random.seed(10)
    i = 0

    z_cat_min = np.power(10, np.log10(np.min(twinkles_lenses['ZLENS'])) - .1)
    z_cat_max = np.power(10, np.log10(np.max(twinkles_lenses['ZLENS'])) + .1)
    
    stellar_mass_cat_min = np.min(np.power(10, twinkles_log_m_1comp))*0.9
    stellar_mass_cat_max = np.max(np.power(10, twinkles_log_m_1comp))*1.1

    data = catalog.get_quantities(['galaxy_id', 'redshift_true', 'stellar_mass', 'ellipticity_true', 'size_true', 'size_minor_true', 
                                   'stellar_mass_bulge', 'stellar_mass_disk', 'size_bulge_true', 'size_minor_bulge_true'],
                                  filters=['stellar_mass > %f' % stellar_mass_cat_min, 'stellar_mass < %f' % stellar_mass_cat_max,
                                           'redshift_true > %f' % z_cat_min, 'redshift_true < %f' % z_cat_max,
                                           'stellar_mass_bulge/stellar_mass > 0.99'])

    #### Important Note
    # Twinkles issue #310 (https://github.com/LSSTDESC/Twinkles/issues/310) says OM10 defines ellipticity as 1 - b/a but
    # gcr_catalogs defines ellipticity as (1-b/a)/(1+b/a) (https://github.com/LSSTDESC/gcr-catalogs/blob/master/GCRCatalogs/SCHEMA.md)

    data['om10_ellipticity'] = (1-(data['size_minor_bulge_true']/data['size_bulge_true']))

    data_df = pd.DataFrame(data)
    data_df.to_csv('om10_matching_checkpoint_1.csv', index=False)


def match_to_cat(twinkles_lenses, twinkles_log_m_1comp, data_df):

    row_num = -1
    keep_rows = []

    for zsrc, m_star, ellip in zip(twinkles_lenses['ZLENS'], np.power(10, twinkles_log_m_1comp), twinkles_lenses['ELLIP']):

        row_num += 1
        #print(zsrc, m_star, ellip)
        if row_num % 1000 == 0:
            print(row_num)

        z_min, z_max = np.power(10, np.log10(zsrc) - .1), np.power(10, np.log10(zsrc) + .1)
        m_star_min, m_star_max = m_star*.9, m_star*1.1
        ellip_min, ellip_max = ellip*.9, ellip*1.1
    
        data_subset = data_df.query('redshift_true > %f and redshift_true < %f and stellar_mass > %f and stellar_mass < %f and om10_ellipticity > %f and om10_ellipticity < %f' %
                                    (z_min, z_max, m_star_min, m_star_max, ellip_min, ellip_max))
    
        #data = catalog.get_quantities(['redshift_true', 'stellar_mass', 'ellipticity_true'])
        #data_subset = (query).filter(data)
        #print(data_subset)
        num_matches = len(data_subset['redshift_true'])
        
        if num_matches == 0:
            err += 1
            continue
        elif num_matches == 1:
            gcr_data = [data_subset['redshift_true'].values[0], 
                        data_subset['stellar_mass_bulge'].values[0],
                        data_subset['om10_ellipticity'].values[0],
                        data_subset['size_bulge_true'].values[0],
                        data_subset['size_minor_bulge_true'].values[0],
                        data_subset['galaxy_id'].values[0]]
            gcr_om10_match.append(gcr_data)
            keep_rows.append(row_num)
        elif num_matches > 1:
            use_idx = np.random.choice(num_matches)
            gcr_data = [data_subset['redshift_true'].values[use_idx], 
                        data_subset['stellar_mass_bulge'].values[use_idx],
                        data_subset['om10_ellipticity'].values[use_idx],
                        data_subset['size_bulge_true'].values[use_idx],
                        data_subset['size_minor_bulge_true'].values[use_idx],
                        data_subset['galaxy_id'].values[use_idx]]
            gcr_om10_match.append(gcr_data)
            keep_rows.append(row_num)
        
    print("Total Match Failures: ", err, " Percentage Match Failures: ", np.float(err)/len(twinkles_log_m_1comp))

    np.savetxt('gcr_om10_match.dat', gcr_om10_match)

def get_catalog_mags(catalog):

    H0 = catalog.cosmology.H0.value
    Om0 = catalog.cosmology.Om0

    sed_label = []
    sed_min_wave = []
    sed_wave_width = []
    for quant_label in sorted(catalog.list_all_quantities()):
        if (quant_label.startswith('sed') and quant_label.endswith('bulge')):
            sed_label.append(quant_label)
            label_split = quant_label.split('_')
            sed_min_wave.append(int(label_split[1])/10)
            sed_wave_width.append(int(label_split[2])/10)
    bin_order = np.argsort(sed_min_wave)
    sed_label = np.array(sed_label)[bin_order]
    sed_min_wave = np.array(sed_min_wave)[bin_order]
    sed_wave_width = np.array(sed_wave_width)[bin_order]

    for i in zip(sed_label, sed_min_wave, sed_wave_width):
        print(i)

    columns = ['galaxy_id', 'redshift_true', 'mag_u_lsst', 'mag_g_lsst', 'mag_r_lsst',
               'mag_i_lsst', 'mag_z_lsst', 'mag_y_lsst']
    for sed_bin in sed_label:
        columns.append(sed_bin)
    data = catalog.get_quantities(columns,
                                  filters=['stellar_mass > %f' % stellar_mass_cat_min, 'stellar_mass < %f' % stellar_mass_cat_max,
                                           'redshift_true > %f' % z_cat_min, 'redshift_true < %f' % z_cat_max,
                                           'stellar_mass_bulge/stellar_mass > 0.99'])
    data_df = pd.DataFrame(data)

    data_df.to_csv('om10_matching_checkpoint_2.csv', index=False)


def get_30_band_mags(gcr_om10_match, data_df, catalog):

    H0 = catalog.cosmology.H0.value
    Om0 = catalog.cosmology.Om0

    sed_name_list = []
    magNorm_list = []
    i = 0
    lsst_mags = []
    mag_30_list = []
    redshift_list = []

    sed_label = []
    sed_min_wave = []
    sed_wave_width = []
    for quant_label in sorted(catalog.list_all_quantities()):
        if (quant_label.startswith('sed') and quant_label.endswith('bulge')):
            sed_label.append(quant_label)
            label_split = quant_label.split('_')
            sed_min_wave.append(int(label_split[1])/10)
            sed_wave_width.append(int(label_split[2])/10)
    bin_order = np.argsort(sed_min_wave)
    sed_label = np.array(sed_label)[bin_order]
    sed_min_wave = np.array(sed_min_wave)[bin_order]
    sed_wave_width = np.array(sed_wave_width)[bin_order]

    lsst_mags = []
    mag_30_list = []
    redshift_list = []
    i = 0
    # Using 1-component model results
    for gal_id, gal_z in zip(gcr_gal_id_1comp, gcr_z_1comp):
        
        if i % 1000 == 0:
            print(i)
        i+=1
    
        data_subset = data_df.query(str('galaxy_id == %i' % gal_id)) ## Galaxy Ids are not unique in cosmoDC2_v0.1
        mag_array = []
        lsst_mag_array = [data_subset['mag_%s_lsst' % band_name].values[0] for band_name in ['u', 'g', 'r', 'i', 'z', 'y']]
        for sed_bin in sed_label:
            mag_array.append(-2.5*np.log10(data_subset[sed_bin].values[0]))
        mag_array = np.array(mag_array)
        lsst_mag_array = np.array(lsst_mag_array)
        lsst_mags.append(lsst_mag_array)
        mag_30_list.append(mag_array)
        redshift_list.append(gal_z)

    mag_30_list = np.array(mag_30_list).T
    lsst_mags = np.array(lsst_mags).T
    redshift_list = np.array(redshift_list)

    sed_name, magNorm, av, rv = sed_from_galacticus_mags(mag_30_list, redshift_list,
                                                         H0, Om0, sed_min_wave, sed_wave_width, lsst_mags)

    return np.array(sed_name), np.array(magNorm), np.array(av), np.array(rv)

if __name__ == "__main__":

    sys.argv[1] = catalog_version


    twinkles_lenses, log_m, twinkles_log_m_1comp = estimate_stellar_masses_om10()

    # Use _image for DC2
    catalog = GCRCatalogs.load_catalog(str(catalog_version + '_small'))

    data_df = pd.read_csv('om10_matching_checkpoint_1.csv')
    
    match_to_cat(twinkles_lenses, twinkles_log_m_1comp, data_df)
    gcr_om10_match = np.genfromtxt('gcr_om10_match.dat')

    gcr_z = []
    gcr_m_star = []
    gcr_r_eff = []
    gcr_gal_id = []
    for row in gcr_om10_match:
        gcr_z.append(row[0])
        gcr_m_star.append(row[1])
        gcr_r_eff.append(np.sqrt(row[3]*row[4]))
        gcr_gal_id.append(row[5])


    get_catalog_mags(catalog)

    data_df = pd.read_csv('om10_matching_checkpoint_2.csv')

    sed_name, magNorm, av, rv = get_30_band_mags(gcr_gal_id, gcr_z, data_df, catalog)

    test_bandpassDict = BandpassDict.loadTotalBandpassesFromFiles()
    imsimband = Bandpass()
    imsimband.imsimBandpass()

    mag_norm_om10 = []
    for i, idx in list(enumerate(keep_rows)):
        if i % 10000 == 0:
            print(i, idx)
        test_sed = Sed()
        test_sed.readSED_flambda(os.path.join(str(os.environ['SIMS_SED_LIBRARY_DIR']), sed_name_array[i]))
        fnorm = test_sed.calcFluxNorm(twinkles_lenses['APMAG_I'][idx], test_bandpassDict['i'])
        test_sed.multiplyFluxNorm(fnorm)
        magNorm_diff = magNorm_array[3, i] - test_sed.calcMag(imsimband)
        mag_norm_om10.append(magNorm_array[:,i] - magNorm_diff)

    col_list = []
    for col in twinkles_lenses.columns:
        if col.name != 'REFF':
            col_list.append(fits.Column(name=col.name, format=col.format, array=twinkles_lenses[col.name][keep_rows]))
        else:
            col_list.append(fits.Column(name=col.name, format=col.format, array=gcr_r_eff_1comp))
    col_list.append(fits.Column(name='lens_sed', format='40A', array=sed_name_array))
    col_list.append(fits.Column(name='sed_magNorm', format='6D', array=mag_norm_om10))

    cols = fits.ColDefs(col_list)
    tbhdu = fits.BinTableHDU.from_columns(cols)
    tbhdu.writeto('../../data/twinkles_lenses_%s.fits' % catalog_version)
