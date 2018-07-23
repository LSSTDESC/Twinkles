import sys
import matplotlib as mpl
mpl.rcParams['text.usetex'] = False
import matplotlib.pyplot as plt
from desc.twinkles import validate_ic
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator

if __name__ == "__main__":

    cat_name = sys.argv[1]

    # opsim_db = sys.argv[2]

    # visit_num = sys.argv[3]

    val_cat = validate_ic()
    
    df_gal, df_agn, df_sne = val_cat.load_cat(cat_name, 'Dynamic')

    spr_agn = val_cat.process_sprinkled_agn(df_agn)

    agn_lens_gals = val_cat.process_lenses(spr_agn, df_gal)
    
    agn_location_test = val_cat.compare_agn_location(spr_agn, agn_lens_gals)

    #spr_sne = val_cat.process_sprinkled_sne(df_sne)

    #sne_lens_gals = val_cat.process_lenses(spr_sne, df_gal)

    #sne_location_test = val_cat.compare_sne_location(spr_sne, sne_lens_gals)

    test_agn_inputs = val_cat.compare_agn_inputs(spr_agn, agn_lens_gals)

    #test_sne_inputs = val_cat.compare_sne_inputs(spr_sne, sne_lens_gals)

    test_agn_lens_mags = val_cat.compare_agn_lens_mags(spr_agn, agn_lens_gals)

    #test_sne_lens_mags = val_cat.compare_sne_lens_mags(spr_sne, sne_lens_gals)

    test_agn_image_mags = val_cat.compare_agn_image_mags(spr_agn, agn_lens_gals,
                                                         59844.22, 'r')
