import numpy as np
import pandas as pd
import os
import sys
import argparse
import GCRCatalogs
import pandas as pd
from GCR import GCRQuery
from lsst.sims.photUtils import Sed, Bandpass, BandpassDict
sys.path.append('/global/homes/b/brycek/DC2/sims_GCRCatSimInterface/workspace/sed_cache/')
from SedFitter import sed_from_galacticus_mags

def load_limited_cat(dc2_df_system, catalog):

    z_cat_min = np.power(10, np.log10(np.min(dc2_df_system['zl'])) - .1)
    z_cat_max = np.power(10, np.log10(np.max(dc2_df_system['zl'])) + .1)

    i_gal_dim = np.max(-2.5*np.log10(np.power(10, -0.4*dc2_df_system['lensgal_mi'])*.9))
    i_gal_bright = np.min(-2.5*np.log10(np.power(10, -0.4*dc2_df_system['lensgal_mi'])*1.1))

    print(z_cat_min, z_cat_max, i_gal_dim, i_gal_bright)

    data = catalog.get_quantities(['galaxy_id', 'redshift_true', 'ellipticity_true', 'mag_true_i_lsst',
                                   'size_minor_bulge_true', 'size_bulge_true'],
                                  filters=['mag_true_i_lsst > %f' % i_gal_bright,
                                           'mag_true_i_lsst < %f' % i_gal_dim,
                                           'redshift_true > %f' % z_cat_min,
                                           'redshift_true < %f' % z_cat_max,
                                           'stellar_mass_bulge/stellar_mass > 0.99'])

    data['glsne_ellipticity'] = (1-(data['size_minor_bulge_true']/data['size_bulge_true']))


    data_df = pd.DataFrame(data)
    data_df.to_csv('sn_matching_checkpoint_1.csv', index=False)


def match_up_glsn(dc2_df_system, data_df):


    gcr_glsn_match = []
    err = 0
    np.random.seed(10)
    i = 0

    row_num = -1
    keep_rows = []
    num_match_total = []

    for zsrc, i_mag_star in zip(dc2_df_system['zl'].values,
                                dc2_df_system['lensgal_mi'].values):

        row_num += 1
        #print(zsrc, m_star, ellip)
        if row_num % 10000 == 0:
            print(row_num)
            
        z_min, z_max = np.power(10, np.log10(zsrc) - .1), np.power(10, np.log10(zsrc) + .1)
        i_mag_dim, i_mag_bright = -2.5*np.log10(np.power(10, -0.4*i_mag_star)*.9),\
                                  -2.5*np.log10(np.power(10, -0.4*i_mag_star)*1.1)
        #ellip_min, ellip_max = ellip*.9, ellip*1.1
        #r_major = r_eff / np.sqrt(1 - ellip)
        #r_major_max, r_major_min = r_major*1.1, r_major*.9
    
        #print(z_min, z_max, i_mag_min, i_mag_max, ellip_min, ellip_max)
    
        data_subset = data_df.query('redshift_true > %f and redshift_true < %f ' % (z_min, z_max)
                                    + 'and mag_true_i_lsst > %f and mag_true_i_lsst < %f ' % (i_mag_bright, i_mag_dim)
                                    #+ 'and glsne_ellipticity > %f and glsne_ellipticity < %f' % (ellip_min, ellip_max)
                                    #+ 'and size_bulge_true > %f and size_bulge_true < %f' % (r_major_min, r_major_max)
                                )
    
        num_matches = len(data_subset['redshift_true'])

        num_match_total.append(num_matches)
    
        if num_matches == 0:
            err += 1
            continue
        elif num_matches == 1:
            gcr_data = [data_subset['redshift_true'].values[0], 
                        data_subset['galaxy_id'].values[0]]
            gcr_glsn_match.append(gcr_data)
            keep_rows.append(row_num)
        elif num_matches > 1:
            use_idx = np.random.choice(num_matches)
            gcr_data = [data_subset['redshift_true'].values[use_idx],
                        data_subset['galaxy_id'].values[use_idx]]
            gcr_glsn_match.append(gcr_data)
            keep_rows.append(row_num)
            
    print("Total Match Failures: ", err, " Percentage Match Failures: ", np.float(err)/len(dc2_df_system))
    
    gcr_glsn_match = np.array(gcr_glsn_match)
    np.savetxt('gcr_glsn_match.txt', gcr_glsn_match)
    keep_rows = np.array(keep_rows)
    np.savetxt('keep_rows_sn.txt', keep_rows)

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
                                  filters=['mag_true_i_lsst > %f' % i_gal_bright,
                                           'mag_true_i_lsst < %f' % i_gal_dim,
                                           'redshift_true > %f' % z_cat_min,
                                           'redshift_true < %f' % z_cat_max,
                                           'stellar_mass_bulge/stellar_mass > 0.99'])
    data_df = pd.DataFrame(data)
    data_df.to_csv('sn_matching_checkpoint_2.csv', index=False)


def get_30_band_mags(gcr_glsn_match, data_df, catalog):

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

    for gal_id, gal_z in zip(gcr_glsn_match[:, 1], 
                             gcr_glsn_match[:, 0]):
        
        if i % 100 == 0:
            print(i)
        i+=1
        #print(np.int(gal_id), type(data_df['galaxy_id'].iloc[0]))
        #print(gal_z, type(gal_z), data_df['redshift_true'].iloc[0])
        #print(int(gal_id))
        data_subset = data_df.query(str('galaxy_id == %i' % np.int(gal_id)))# + ' and ' + 'redshift_true == {}'.format(gal_z))) ## Galaxy Ids are not unique in cosmoDC2_v0.1
        #print(data_subset)
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

    print('Getting SEDs')

    sed_name, magNorm, av, rv = sed_from_galacticus_mags(mag_30_list, redshift_list,
                                                         H0, Om0, sed_min_wave, sed_wave_width, lsst_mags)

    return sed_name, magNorm, av, rv


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("cat_version", type=str,
                        help="CosmoDC2 catalog name from gcr-catalogs.")
    parser.add_argument("glsn_cat", type=str,
                        help="Location of graviationally lensed SNe catalog.")
    args = parser.parse_args()
    catalog_version = args.cat_version
    glsn_cat = args.glsn_cat

    dc2_df_system = pd.read_hdf(glsn_cat, key='system')
    dc2_df_image = pd.read_hdf(glsn_cat, key='image')

    catalog = GCRCatalogs.load_catalog('%s_small' % catalog_version)

    load_limited_cat(dc2_df_system, catalog)
    data_df = pd.read_csv('sn_matching_checkpoint_1.csv')
    print('Saved Checkpoint 1.')
    match_up_glsn(dc2_df_system, data_df)
    get_catalog_mags(catalog)
    print('Saved Checkpoint 2.')

    data_df = pd.read_csv('sn_matching_checkpoint_2.csv')
    gcr_glsn_match = np.genfromtxt('gcr_glsn_match.txt')
    keep_rows = np.genfromtxt('keep_rows_sn.txt')

    sed_name, magNorm, av, rv = get_30_band_mags(gcr_glsn_match, data_df, catalog)

    sed_name_array = np.array(sed_name)
    magNorm_array = np.array(magNorm)
    av_array = np.array(av)
    rv_array = np.array(rv)

    np.savetxt('sed_name_list_sn.txt', sed_name_array, fmt='%s')
    np.savetxt('magNorm_list_sn.txt', magNorm_array)
    np.savetxt('av_list_sn.txt', av_array)
    np.savetxt('rv_list_sn.txt', rv_array)

    test_bandpassDict = BandpassDict.loadTotalBandpassesFromFiles()
    imsimband = Bandpass()
    imsimband.imsimBandpass()

    mag_norm_glsne = []
    for i, idx in list(enumerate(keep_rows)):
        if i % 10000 == 0:
            print(i, idx)
        test_sed = Sed()
        test_sed.readSED_flambda(os.path.join(str(os.environ['SIMS_SED_LIBRARY_DIR']), sed_name_array[i]))
        fnorm = test_sed.calcFluxNorm(dc2_df_system['lensgal_mi'].iloc[idx], test_bandpassDict['i'])
        test_sed.multiplyFluxNorm(fnorm)
        magNorm_diff = magNorm_array[3, i] - test_sed.calcMag(imsimband)
        mag_norm_glsne.append(magNorm_array[:,i] - magNorm_diff)

    mag_norm_glsne = np.array(mag_norm_glsne)

    results_dict = {}
    print(len(keep_rows), len(gcr_glsn_match[:, 0]))
    for keep_idx in range(len(keep_rows)):
        results_dict[str(dc2_df_system['sysno'].iloc[keep_rows[keep_idx]])] = {'z':gcr_glsn_match[:, 0][keep_idx],
                                                                               'sed_name':sed_name_array[keep_idx],
                                                                               'magNorm':mag_norm_glsne[keep_idx],
                                                                               'lens_av':av_array[keep_idx],
                                                                               'lens_rv':rv_array[keep_idx]}
    keep_systems = dc2_df_system['sysno'].iloc[keep_rows].values

    final_df_z = []
    final_df_lens_sed = []
    final_df_magNorm_u = []
    final_df_magNorm_g = []
    final_df_magNorm_r = []
    final_df_magNorm_i = []
    final_df_magNorm_z = []
    final_df_magNorm_y = []
    final_df_lens_av = []
    final_df_lens_rv = []
    
    keep_in_df = []
    
    for idx, twinkles_sys in enumerate(dc2_df_system['sysno']):
        if twinkles_sys in keep_systems:
            keep_in_df.append(idx)
            final_df_z.append(results_dict[str(twinkles_sys)]['z'])
            final_df_lens_sed.append(results_dict[str(twinkles_sys)]['sed_name'])
            final_df_magNorm_u.append(results_dict[str(twinkles_sys)]['magNorm'][0])
            final_df_magNorm_g.append(results_dict[str(twinkles_sys)]['magNorm'][1])
            final_df_magNorm_r.append(results_dict[str(twinkles_sys)]['magNorm'][2])
            final_df_magNorm_i.append(results_dict[str(twinkles_sys)]['magNorm'][3])
            final_df_magNorm_z.append(results_dict[str(twinkles_sys)]['magNorm'][4])
            final_df_magNorm_y.append(results_dict[str(twinkles_sys)]['magNorm'][5])
            final_df_lens_av.append(results_dict[str(twinkles_sys)]['lens_av'])
            final_df_lens_rv.append(results_dict[str(twinkles_sys)]['lens_rv'])

    final_df = dc2_df_system.iloc[keep_in_df]
    final_df = final_df.reset_index(drop=True)

    final_df['lensgal_magnorm_u'] = final_df_magNorm_u
    final_df['lensgal_magnorm_g'] = final_df_magNorm_g
    final_df['lensgal_magnorm_r'] = final_df_magNorm_r
    final_df['lensgal_magnorm_i'] = final_df_magNorm_i
    final_df['lensgal_magnorm_z'] = final_df_magNorm_z
    final_df['lensgal_magnorm_y'] = final_df_magNorm_y
    final_df['lensgal_sed'] = final_df_lens_sed
    final_df['lens_av'] = final_df_lens_av
    final_df['lens_rv'] = final_df_lens_rv

    final_df.to_hdf('/global/cscratch1/sd/brycek/glsne_%s.h5' % catalog_version, key='system', format='table')
    dc2_df_image.to_hdf('/global/cscratch1/sd/brycek/glsne_%s.h5' % catalog_version, mode='a', key='image', format='table')
