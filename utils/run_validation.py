import sys
import matplotlib as mpl
mpl.rcParams['text.usetex'] = False
import matplotlib.pyplot as plt
from desc.twinkles import validate_ic

if __name__ == "__main__":

    cat_name = sys.argv[1]

    val_cat = validate_ic()
    
    df_gal, df_agn, df_sne = val_cat.load_cat(cat_name, 'Dynamic')

    spr_agn = val_cat.process_sprinkled_agn(df_agn)

    agn_lens_gals = val_cat.process_agn_lenses(spr_agn, df_gal)
    
    res = val_cat.compare_agn_location(spr_agn, agn_lens_gals)
