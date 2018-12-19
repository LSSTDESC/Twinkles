from desc.sims.GCRCatSimInterface import InstanceCatalogWriter

catalog_version = 'cosmoDC2_v1.1.4'
agnDB = '/global/projecta/projectdirs/lsst/groups/SSim/DC2/cosmoDC2_v1.1.4/agn_db_mbh7_mi30_sf4.db'
sneDB = '/global/projecta/projectdirs/lsst/groups/SSim/DC2/cosmoDC2_v1.1.4/sne_cosmoDC2_v1.1.4_MS_DDF.db'
sed_lookup_dir = '/global/projecta/projectdirs/lsst/groups/SSim/DC2/cosmoDC2_v1.1.4/sedLookup'

# First we need to create a catalog without sprinkling
opsimDB = '/global/projecta/projectdirs/lsst/groups/SSim/DC2/minion_1016_desc_dithered_v4.db'
starDB = '/global/projecta/projectdirs/lsst/groups/SSim/DC2/dc2_stellar_db.db'

if __name__ == "__main__":

    t_sky = InstanceCatalogWriter(opsimDB, '%s_image_addon_knots' % catalog_version, min_mag=30, protoDC2_ra=0,
                              protoDC2_dec=0, sprinkler=False,
                              agn_db_name=agnDB, star_db_name=starDB,
                              sed_lookup_dir=sed_lookup_dir)

    uddf_visit = 197356 # Use a visit we know covers the uDDF field
    t_sky.write_catalog(uddf_visit, out_dir='../../examples/notebooks', fov=2.1)
