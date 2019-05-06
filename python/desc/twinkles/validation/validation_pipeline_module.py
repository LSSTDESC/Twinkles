import os
import sys
import argparse
import numpy as np
from .validate_ic import validate_ic

__all__ = ["validation_pipeline"]

def validation_pipeline(cat_folder, visit_num, sne_SED_path):
    """
    Parameters
    ----------
    cat_folder is a string; the path to the directory containing the
    phosim_NNNNN.txt catalog

    visit_num is an int; the obsHistID of the pointing

    sne_SED_path is a string; the path to the parent directory of
    the Dynamic/ dir containing SNe SEDs
    """

    filter_list = ['u', 'g', 'r', 'i', 'z', 'y']

    print("Loading visit info")
    with open(os.path.join(cat_folder, 'phosim_cat_%i.txt' % visit_num)) as f:
        for line in f:
            line_info = line.split(' ')
            if line_info[0] == 'mjd':
                visit_mjd = float(line_info[1])
            elif line_info[0] == 'filter':
                visit_band = filter_list[int(line_info[1])]
            elif line_info[0] == 'vistime':
                delta_t = float(line_info[1])/2.

    # This converts the way phosim wants the time to opsim time
    visit_mjd -= delta_t/86400.0

    sne_SED_file_dir = 'Dynamic'

    twinkles_data_dir = os.path.join(os.environ['TWINKLES_DIR'], 'data')
    agn_cache_file_name = os.path.join(twinkles_data_dir,
                                       'cosmoDC2_v1.1.4_agn_cache.csv')
    sne_cache_file_name = os.path.join(twinkles_data_dir,
                                       'cosmoDC2_v1.1.4_sne_cache.csv')
    sprinkled_agn_data_name = os.path.join(twinkles_data_dir,
                                           'cosmoDC2_v1.1.4_matched_AGN.fits')
    sprinkled_sne_data_name = os.path.join(twinkles_data_dir,
                                           'cosmoDC2_v1.1.4_sne_cat.csv')

    print("Running tests")
    val_cat = validate_ic(agn_cache_file=agn_cache_file_name,
                          sne_cache_file=sne_cache_file_name,
                          sprinkled_agn_data=sprinkled_agn_data_name,
                          sprinkled_sne_data=sprinkled_sne_data_name)
    
    df_gal, df_pt_src = val_cat.load_cat(cat_folder, visit_num)

    # Verify that the InstanceCatalog pipline ignored
    # the Sersic components of rows corresponding to
    # duplicate images of AGN (those rows would have
    # galaxy_id == (galaxy_id+1.5e10)*100000 as per
    # the uniqueId mangling scheme in the sprinkler)
    df_gal_galaxy_id = df_gal['uniqueId'].values//1024
    large_galaxy_id = df_gal_galaxy_id>1.0e11
    if large_galaxy_id.any():
        raise RuntimeError("Some galaxies that should have been "
                           "replaced by the sprinkler were not.")

    # Make sure that none of the point sources have magNorm
    # placeholders (999 or None) by the time they reach the
    # InstanceCatalog
    pt_src_magnorm = df_pt_src['phosimMagNorm'].values
    invalid_magnorm = (pt_src_magnorm>900.0) | np.isnan(pt_src_magnorm)

    if invalid_magnorm.any():
        raise RuntimeError("Some point sources have invalid magNorms")

    spr_agn = val_cat.process_sprinkled_agn(df_pt_src)

    agn_lens_gals = val_cat.process_agn_lenses(spr_agn, df_gal)
    
    agn_location_test = val_cat.compare_agn_location(spr_agn, agn_lens_gals)

    spr_sne = val_cat.process_sprinkled_sne(df_pt_src, sne_SED_file_dir)

    sne_lens_gals = val_cat.process_sne_lenses(df_gal)

    sne_location_test = val_cat.compare_sne_location(spr_sne, sne_lens_gals)

    test_agn_inputs = val_cat.compare_agn_inputs(spr_agn, agn_lens_gals)

    test_sne_lens_inputs = val_cat.compare_sne_lens_inputs(sne_lens_gals)

    test_sne_image_inputs = val_cat.compare_sne_image_inputs(spr_sne,
                                                             sne_lens_gals,
                                                             visit_mjd,
                                                             sne_SED_file_dir,
                                                             sne_SED_path)

    test_agn_lens_mags = val_cat.compare_agn_lens_mags(spr_agn, agn_lens_gals,
                                                       visit_band)

    test_sne_lens_mags = val_cat.compare_sne_lens_mags(sne_lens_gals,
                                                       visit_band)

    test_agn_image_mags = val_cat.compare_agn_image_mags(spr_agn, agn_lens_gals,
                                                         visit_mjd, visit_band)

    test_sne_image_mags = val_cat.compare_sne_image_mags(spr_sne, sne_lens_gals,
                                                         visit_mjd, visit_band)
