import os
import sqlite3
import om10
import pandas as pd
import numpy as np
import gzip
import shutil
import copy
import json
from lsst.utils import getPackageDir
import lsst.sims.utils.htmModule as htm
from lsst.sims.photUtils import Bandpass, BandpassDict, Sed, getImsimFluxNorm
from lsst.sims.photUtils import calcSNR_m5, PhotometricParameters
from lsst.sims.catUtils.supernovae import SNObject
from lsst.sims.catUtils.mixins.VariabilityMixin import ExtraGalacticVariabilityModels as egvar


__all__ = ['validate_ic']


class CatalogError(Exception):
    """Raised when Instance Catalog entries do not pass expected tests."""
    pass

class validate_ic(object):

    def __init__(self, agn_cache_file=None, sne_cache_file=None,
                 sprinkled_agn_data=None, sprinkled_sne_data=None):

        """
        Initiate with the location of the input AGN and SNe lensed
        systems information. Also initiate with the location of the
        cached sprinkled AGN and SNe galaxy IDs.

        Parameters
        ----------
        agn_cache_file: str or None, default=None
            The location of the file with the cached galaxy IDs that
            are replaced when sprinkling in the lensed AGN systems. If None
            then it uses the latest DESC cache in the Twinkles/data
            directory.

        sne_cache_file: str or None, default=None
            The location of the file with the cached galaxy IDs that
            are replaced when sprinkling in the lensed SNe systems. If None
            then it uses the latest DESC cache in the Twinkles/data
            directory.

        sprinkled_agn_data: str or None, default=None
            The location of the file with the set of sprinkled AGN
            systems. If None then it will use information from the
            Twinkles/data directory.

        sprinkled_sne_data: str or None, default=None
            The location of the file with the set of sprinkled SNe
            systems. If None then it will use information from the
            Twinkles/data directory.
        """

        self.lsst_bp_dict = BandpassDict.loadTotalBandpassesFromFiles()
        self.phot_params = PhotometricParameters(exptime=30.0, nexp=1)
        self.sn_gamma_dict = {}
        for bp in 'ugrizy':
            self.sn_gamma_dict[bp] = None

        if agn_cache_file is None:
            self.agn_cache_file = os.path.join(os.environ['TWINKLES_DIR'],
                                               'data', 'dc2_agn_cache.csv')
        else:
            self.agn_cache_file = agn_cache_file

        if sne_cache_file is None:
            self.sne_cache_file = os.path.join(os.environ['TWINKLES_DIR'],
                                               'data', 'dc2_sne_cache.csv')
        else:
            self.sne_cache_file = sne_cache_file

        if sprinkled_agn_data is None:
            self.sprinkled_agn_data = os.path.join(os.environ['TWINKLES_DIR'],
                                                   'data',
                                                   'twinkles_lenses_v2.fits')
        else:
            self.sprinkled_agn_data = sprinkled_agn_data

        if sprinkled_sne_data is None:
            self.sprinkled_sne_data = os.path.join(os.environ['TWINKLES_DIR'],
                                                   'data',
                                                   'dc2_sne_cat.csv')
        else:
            self.sprinkled_sne_data = sprinkled_sne_data

        return

    def load_cat(self, ic_folder, visit_num):

        """
        This method takes a visit number and a folder with instance
        catalogs separated as those from sims_GCRCatSimInterface
        and loads the needed instance catalogs and parses them
        into separate pandas dataframes for the galaxy bulges where
        the lens galaxies can be found and for extragalactic point
        sources where the sprinkled AGN and SNe can be found.

        Parameters
        ----------
        ic_folder: str
            The folder where the instance catalogs are stored.

        visit_num: int
            The visit number of the instance catalogs you want to test

        Returns
        -------
        df_galaxy: pandas dataframe
            A pandas dataframe with the instance catalog information from
            the bulge components of galaxies where the lens galaxies are
            found.

        df_pt_src: pandas dataframe
            A pandas dataframe with the instance catalog information
            for the sprinkled extragalactic point sources including the
            sprinkled AGN and SNe.
        """

        ic_file = '_gal_cat_%i.txt.gz' % visit_num

        i=0
        not_star_rows = []
        not_galaxy_rows = []
        not_agn_rows = []
        not_sne_rows = []

        base_columns = ['prefix', 'uniqueId', 'raPhoSim', 'decPhoSim',
                        'phosimMagNorm', 'sedFilepath', 'redshift',
                        'shear1', 'shear2', 'kappa', 'raOffset', 'decOffset',
                        'spatialmodel']

        df_galaxy = pd.read_csv(os.path.join(ic_folder, 'bulge%s' % ic_file),
                                delimiter=' ', header=None,
                                names=base_columns+['majorAxis', 'minorAxis',
                                                    'positionAngle', 'sindex',
                                                    'internalExtinctionModel',
                                                    'internalAv', 'internalRv',
                                                    'galacticExtinctionModel',
                                                    'galacticAv', 'galacticRv'])

        df_pt_srcs = pd.read_csv(os.path.join(ic_folder, 'agn%s' % ic_file),
                                 delimiter=' ', header=None,
                                 names=base_columns+['internalExtinctionModel',
                                                     'galacticExtinctionModel',
                                                     'galacticAv', 'galacticRv'])

        return df_galaxy, df_pt_srcs

    def process_sprinkled_agn(self, df_agn):

        """
        The method parses the extragalactic point source dataframe for the
        sprinkled AGN.

        Parameters
        ----------
        df_agn: pandas dataframe
            The point source dataframe from load_cat

        Returns
        -------
        sprinkled_agn: pandas dataframe
            A pandas dataframe with only the sprinkled AGN found in the
            Instance Catalog with additional information on the lens
            system and lens galaxy associated with each AGN.
        """

        galtileids = []
        twinkles_system = []
        twinkles_im_num = []
        galtile_list = np.genfromtxt(self.agn_cache_file, delimiter=',',
                                     names=True, dtype=np.int)

        id_offset = int(1.5e10)
        keep_idx = []
        for i, agn_id in enumerate(df_agn['uniqueId']):
            twinkles_ids = np.right_shift(agn_id, 10)
            galtileid = int(twinkles_ids)//100000-id_offset
            if galtileid in galtile_list['galtileid']:
                keep_idx.append(i)
                galtileids.append(galtileid)
                twinkles_num = twinkles_ids % 100000
                twinkles_system.append(twinkles_num // 8)
                twinkles_im_num.append(twinkles_num % 8)

        galtileids = np.array(galtileids, dtype=np.int)
        sprinkled_agn = df_agn.iloc[np.array(keep_idx)]
        sprinkled_agn = sprinkled_agn.reset_index(drop=True)
        sprinkled_agn['galaxy_id'] = galtileids
        sprinkled_agn['twinkles_system'] = twinkles_system
        sprinkled_agn['image_number'] = twinkles_im_num
        sprinkled_agn['lens_galaxy_uID'] = np.left_shift(galtileids, 10) + 97
        twinkles_system = np.array(twinkles_system, dtype=np.int)
        twinkles_im_num = np.array(twinkles_im_num, dtype=np.int)
        sprinkled_agn['host_galaxy_bulge_uID'] = np.array(np.left_shift(galtileids*100000
                                                                        + twinkles_system*8 +
                                                                        twinkles_im_num, 10) + 97,
                                                          dtype=np.int)
        sprinkled_agn['host_galaxy_disk_uID'] = np.array(np.left_shift(galtileids*100000
                                                                       + twinkles_system*8 +
                                                                       twinkles_im_num, 10) + 107,
                                                         dtype=np.int)

        return sprinkled_agn

    def process_hosts(self, sprinkled_df, df_galaxy):

        """
        This will take the galaxy and sprinkled point source dataframes and create
        a new dataframe with the sprinkled hosts of the point sources.

        ***Not yet ready since the final format of how hosts will be printed
        out in sims_GCRCatSimInterface is not yet complete.***
        """

        host_bulge_locs = []
        host_disk_locs = []
        for bulge_idx, disk_idx in zip(sprinkled_df['host_galaxy_bulge_uID'],
                                       sprinkled_df['host_galaxy_disk_uID']):
            bulge_matches = np.where(df_galaxy['uniqueId'] == bulge_idx)[0]
            disk_matches = np.where(df_galaxy['uniqueId'] == disk_idx)[0]
            assert len(bulge_matches) == len(disk_matches)
            for bulge_match, disk_match in zip(bulge_matches, disk_matches):
                host_bulge_locs.append(bulge_match)
                host_disk_locs.append(disk_match)

        host_bulges = df_galaxy.iloc[np.unique(host_bulge_locs)]
        host_bulges = host_bulges.reset_index(drop=True)
        assert len(host_bulges) == len(sprinkled_df)
        host_bulges['galaxy_id'] = sprinkled_df['galaxy_id']
        host_bulges['twinkles_system'] = sprinkled_df['twinkles_system']
        host_bulges['image_number'] = sprinkled_df['image_number']
        host_disks = df_galaxy.iloc[np.unique(host_disk_locs)]
        host_disks = host_disks.reset_index(drop=True)
        host_disks['galaxy_id'] = sprinkled_df['galaxy_id']
        host_disks['twinkles_system'] = sprinkled_df['twinkles_system']
        host_disks['image_number'] = sprinkled_df['image_number']

        return host_bulges, host_disks

    def process_agn_lenses(self, sprinkled_df, df_galaxy):

        """
        Takes the sprinkled AGN dataframe and the full Instance Catalog
        bulge dataframe and parses the latter to find the lens galaxies
        for the lensed AGN systems.

        Parameters
        ----------
        sprinkled_df: pandas dataframe
            The dataframe from process_sprinkled_agn that contains the
            sprinkled AGN in the Instance Catalog

        df_galaxy: pandas dataframe
            The dataframe from load_cat that contains the bulge information
            from the Instance Catalog

        Returns
        -------
        lens_gals: pandas dataframe
            Dataframe with the lens galaxies for the sprinkled systems
            present in the Instance Catalog
        """

        if len(sprinkled_df) == 0:
            return []

        lens_gal_locs = []
        for idx in sprinkled_df['lens_galaxy_uID'].values:
            matches = np.where(df_galaxy['uniqueId'] == idx)[0]
            for match in matches:
                lens_gal_locs.append(match)

        lens_gals = df_galaxy.iloc[np.unique(lens_gal_locs)]
        lens_gals = lens_gals.reset_index(drop=True)

        return lens_gals

    def process_sne_lenses(self, df_galaxy):

        """
        Takes the full Instance Catalog bulge dataframe and
        parses it to find the lens galaxies for the lensed SNe systems.
        Unlike the process_agn_lenses we cannot just use the lensed AGN
        to know which lens galaxies should be present because the lensed
        SNe do not always show up in the Instance Catalog like the lensed AGN.
        Since the images of the SNe will only appear based upon the mjd of the
        Instance Catalog they may not be in the Instance Catalog but the lens
        galaxy for the lensed SNe system should always be present. Therefore,
        we must use a cache file with the galaxy ids that were sprinkled.

        Parameters
        ----------
        df_galaxy: pandas dataframe
            The dataframe from load_cat that contains the bulge information
            from the Instance Catalog

        Returns
        -------
        lens_gals: pandas dataframe
            Dataframe with the lens galaxies for the sprinkled systems
            present in the Instance Catalog
        """

        galtile_list = np.genfromtxt(self.sne_cache_file, delimiter=',',
                                     names=True, dtype=np.int)

        lens_gal_locs = []
        twinkles_sys = []
        for gal_row in galtile_list:
            bulge_id = np.left_shift(gal_row['galtileid'], 10) + 97
            match = np.where(df_galaxy['uniqueId'] == bulge_id)[0]
            if len(match) > 1:
                raise ValueError('Multiple galaxies with same id.')
            elif len(match) == 1:
                lens_gal_locs.append(match[0])
                twinkles_sys.append(gal_row['twinkles_system'])

        lens_gals = df_galaxy.iloc[lens_gal_locs]
        lens_gals = lens_gals.reset_index(drop=True)
        lens_gals['twinkles_system'] = twinkles_sys

        return lens_gals


    def process_sprinkled_sne(self, df_sne, sn_file_path):

        """
        The method parses the extragalactic point source dataframe for the
        sprinkled SNe. This will only have the sprinkled SNe that show
        up in a given Instance Catalog, not the entire set of sprinkled SNe
        that may show up in the field across all times.

        Parameters
        ----------
        df_sne: pandas dataframe
            The point source dataframe from load_cat

        sne_file_path: string
            The folder where the dynamically generated SNe SEDs are found

        Returns
        -------
        sprinkled_sne: pandas dataframe
            A pandas dataframe with only the sprinkled SNe found in the
            Instance Catalog with additional information on the lens
            system and lens galaxy associated with each SNe.
        """

        galtileids = []
        twinkles_system = []
        twinkles_im_num = []
        galtile_list = np.genfromtxt(self.sne_cache_file, delimiter=',',
                                     names=True, dtype=np.int)

        i=0
        keep_idx = []
        id_offset = int(1.5e10)
        for sne_idx, sne_row in df_sne.iterrows():
            if sne_row['sedFilepath'].startswith(sn_file_path):
                sne_id = sne_row['uniqueId']
                twinkles_ids = np.right_shift(sne_id, 10)
                galtileid = int(twinkles_ids)//100000 - id_offset
                if galtileid in galtile_list['galtileid']:
                    keep_idx.append(i)
                    galtileids.append(galtileid)
                    twinkles_num = twinkles_ids % 100000
                    twinkles_system.append(twinkles_num // 8)
                    twinkles_im_num.append(twinkles_num % 8)

            i+=1

        galtileids = np.array(galtileids, dtype=np.int)
        sprinkled_sne = df_sne.iloc[np.array(keep_idx)]
        sprinkled_sne = sprinkled_sne.reset_index(drop=True)
        sprinkled_sne['galaxy_id'] = galtileids
        sprinkled_sne['twinkles_system'] = twinkles_system
        sprinkled_sne['image_number'] = twinkles_im_num
        sprinkled_sne['lens_galaxy_uID'] = np.left_shift(np.array(galtileids, dtype=np.int), 10) + 97
        twinkles_system = np.array(twinkles_system, dtype=np.int)
        twinkles_im_num = np.array(twinkles_im_num, dtype=np.int)
        sprinkled_sne['host_galaxy_bulge_uID'] = np.array(np.left_shift(galtileids*100000
                                                                        + twinkles_system*8 +
                                                                        twinkles_im_num, 10) + 97,
                                                          dtype=np.int)
        sprinkled_sne['host_galaxy_disk_uID'] = np.array(np.left_shift(galtileids*100000
                                                                       + twinkles_system*8 +
                                                                       twinkles_im_num, 10) + 107,
                                                         dtype=np.int)


        return sprinkled_sne

    def offset_on_sky(self, ra, dec, ra0, dec0, units='degrees'):

        """
        Subtract off a reference sky position and convert to simple cartesians in arcsec:

        Parameters
        ----------
        ra, dec : float, float
            Feature positions (degrees)
        ra0, dec0 : float, float
            Reference position (degrees)
        units : string
            'degrees' or 'radians'

        Returns
        -------
        x, y : float, float
            Offset position in righthanded cartesians, and units of arcsec
        """

        if units == 'radians':
            ra, dec = np.degrees(ra), np.degrees(dec)

        y = 3600.0 * (dec - dec0)
        x = 3600.0 * (ra - ra0) * np.cos(np.radians(dec0))

        return x, y

    def compare_agn_location(self, spr_agn_df, spr_agn_lens_df):

        """
        This test makes sure that the AGN images are offset from the lenses by the
        correct amounts given by the input catalog. The test will raise an error
        if offsets are incorrect.

        Parameters
        ----------
        spr_agn_df: pandas dataframe
            Dataframe with the sprinkled AGN images from the Instance Catalog.
            This is the output dataframe from process_sprinkled_agn.

        spr_agn_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled AGN
            systems. This is the output dataframe from process_agn_lenses.
        """

        if len(spr_agn_df)==0 or len(spr_agn_lens_df)==0:
            if len(spr_agn_df) != len(spr_agn_lens_df):
                msg = "\nlen(spr_agn_df): %d\n" % len(spr_agn_df)
                msg += "len(spr_agn_lens_df): %d\n" % len(spr_agn_lens_df)
                raise RuntimeError(msg)
            return
        db = om10.DB(catalog=self.sprinkled_agn_data, vb=False)

        x_offsets = []
        y_offsets = []
        total_offsets = []

        for lens_gal_row in spr_agn_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_agn_df.query('lens_galaxy_uID == %i' % u_id)
            use_lens = db.lenses['LENSID'][np.where(db.lenses['twinklesId'] ==
                                                    spr_sys_df['twinkles_system'].iloc[0])[0]]
            lens = db.get_lens(use_lens)
            num_img = lens['NIMG']

            for img_idx in range(num_img[0]):
                # Calculate the offsets from the lens galaxy position
                offset_x1, offset_y1 = self.offset_on_sky(spr_sys_df['raPhoSim'].iloc[img_idx],
                                                          spr_sys_df['decPhoSim'].iloc[img_idx],
                                                          lens_gal_df['raPhoSim'],
                                                          lens_gal_df['decPhoSim'])

                x_offsets.append(offset_x1-lens['XIMG'][0][img_idx])
                y_offsets.append(offset_y1-lens['YIMG'][0][img_idx])
                total_offsets.append((np.sqrt(x_offsets[-1]**2. + y_offsets[-1]**2.)/
                                      np.sqrt(lens['XIMG'][0][img_idx]**2. +
                                              lens['YIMG'][0][img_idx]**2.)))

        max_total_err = np.max(total_offsets)

        print('------------')
        print('AGN Location Test Results:')

        if max_total_err < 0.01:
            print('Pass: Max image offset error less than 1 percent')
        else:
            raise CatalogError('\nFail: Max image offset error greater than 1 percent. ' +
                               'Max total offset error is: %.4f percent.' % max_total_err)

        print('------------')

        return

    def compare_sne_location(self, spr_sne_df, spr_sne_lens_df):

        """
        This test makes sure that the SNe images are offset from the lenses by the
        correct amounts given by the input catalog. The test will raise an error
        if offsets are incorrect.

        Parameters
        ----------
        spr_sne_df: pandas dataframe
            Dataframe with the sprinkled SNe images from the Instance Catalog.
            This is the output dataframe from process_sprinkled_sne.

        spr_sne_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled SNe
            systems. This is the output dataframe from process_sne_lenses.
        """
        if len(spr_sne_lens_df)==0:
            # spr_sne_df could have len 0 b/c SNe transience
            if len(spr_sn_df)!=len(spr_sne_lens_df):
                msg = "\nlen(spr_sn_df) %d\n" % len(spr_sn_df)
                msg += "len(spr_sne_lens_df) %d\n" % len(spr_sne_lens_df)
                raise RuntimeError(msg)
            return

        df = pd.read_csv(self.sprinkled_sne_data)

        x_offsets = []
        y_offsets = []
        total_offsets = []
        images_tested = 0

        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_sne_df.query('lens_galaxy_uID == %i' % u_id)

            # There may be no images present in the current instance catalog
            if len(spr_sys_df) == 0:
                continue

            twinkles_system = spr_sys_df['twinkles_system'].iloc[0]

            lens = df.query('twinkles_sysno == %i' % spr_sys_df['twinkles_system'].iloc[0])
            #print(lens.columns)
            #exit()

            # SNe systems might not have all images appearing in an instance catalog unlike AGN
            img_vals = spr_sys_df['image_number'].values

            for img_idx in range(len(img_vals)):

                # This is just to make sure there are at least some images when we expect
                # and the test is not just skipping everything.
                images_tested += 1

               # Calculate the offsets from the lens galaxy position
                offset_x1, offset_y1 = self.offset_on_sky(spr_sys_df['raPhoSim'].iloc[img_idx],
                                                          spr_sys_df['decPhoSim'].iloc[img_idx],
                                                          lens_gal_df['raPhoSim'],
                                                          lens_gal_df['decPhoSim'])

                x_offsets.append(offset_x1-lens['x'].iloc[img_vals[img_idx]])
                y_offsets.append(offset_y1-lens['y'].iloc[img_vals[img_idx]])

                gross_cos_dec = np.cos(np.radians(spr_sys_df['decPhoSim']))
                dra_shld = lens['lensgal_x'].iloc[img_vals[img_idx]] - lens['x'].iloc[img_vals[img_idx]]
                ddec_shld = lens['lensgal_y'].iloc[img_vals[img_idx]] - lens['y'].iloc[img_vals[img_idx]]

                total_offsets.append((np.sqrt(x_offsets[-1]**2. + y_offsets[-1]**2.)/
                                      np.sqrt(lens['x'].iloc[img_vals[img_idx]]**2. +
                                              lens['y'].iloc[img_vals[img_idx]]**2.)))

        max_total_err = np.max(total_offsets)

        print('------------')
        print('SNe Location Test Results:')

        print('Tested %i systems with images.' % images_tested)

        if max_total_err < 0.01:
            print('Pass: Max image offset error less than 1 percent')
        else:
            raise CatalogError('\nFail: Max image offset error greater than 1 percent. ' +
                               'Max total offset error is: %.4f percent.' % max_total_err)

        print('------------')

        return

    def compare_agn_inputs(self, spr_agn_df, spr_agn_lens_df):

        """
        This test makes sure that the AGN system properties that are replaced
        in Instance Catalogs by the sprinkler get inserted correctly. It will raise an
        error if the differences are outside a reasonable amount.

        Parameters
        ----------
        spr_agn_df: pandas dataframe
            Dataframe with the sprinkled AGN images from the Instance Catalog.
            This is the output dataframe from process_sprinkled_agn.

        spr_agn_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled AGN
            systems. This is the output dataframe from process_agn_lenses.
        """

        if len(spr_agn_df)==0 or len(spr_agn_lens_df)==0:
            if len(spr_agn_df) != len(spr_agn_lens_df):
                msg = "\nlen(spr_agn_df): %d\n" % len(spr_agn_df)
                msg += "len(spr_agn_lens_df): %d\n" % len(spr_agn_lens_df)
                raise RuntimeError(msg)
            return

        db = om10.DB(catalog=self.sprinkled_agn_data, vb=False)

        errors_present = False
        phi_error = False
        z_lens_error = False
        z_src_error = False
        lens_major_axis_error = False
        lens_minor_axis_error = False
        lens_sed_error = False
        lens_sed_filepath_error = False
        errors_string = "Errors in: "

        for lens_gal_row in spr_agn_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_agn_df.query('lens_galaxy_uID == %i' % u_id)
            use_lens = db.lenses['LENSID'][np.where(db.lenses['twinklesId'] ==
                                                    spr_sys_df['twinkles_system'].iloc[0])[0]]
            lens = db.get_lens(use_lens)

            # These should just be different by a minus sign
            if np.abs(lens['PHIE'] + lens_gal_df['positionAngle']) > 0.005:
                if phi_error is False:
                    errors_string = errors_string + "\nPosition Angles. First error found in lens_gal_id: %i" % u_id
                    errors_present = True
                    phi_error = True

            # Redshifts should be identical
            if np.abs(lens['ZLENS'] - lens_gal_df['redshift']) > 0.005:
                if z_error is False:
                    errors_string = errors_string + "\nLens Redshifts. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    z_lens_error = True

            if np.max(np.abs(lens['ZSRC'] - spr_sys_df['redshift'].values)) > 0.005:
                if z_src_error is False:
                    errors_string = errors_string + "\nSource Redshifts. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    z_src_error = True

            if np.abs(lens_gal_df['majorAxis'] - lens['REFF']/np.sqrt(1-lens['ELLIP'])) > 0.005:
                if lens_major_axis_error is False:
                    errors_string = errors_string + "\nLens Major Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_major_axis_error = True

            if np.abs(lens_gal_df['minorAxis'] - lens['REFF']*np.sqrt(1-lens['ELLIP'])) > 0.005:
                if lens_minor_axis_error is False:
                    errors_string = errors_string + "\nLens Minor Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_minor_axis_error = True

            if (lens_gal_df['sedFilepath'] != lens['lens_sed'][0]):
                if lens_sed_error is False:
                    errors_string = errors_string + "\nSED Filename. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_sed_error = True

            sed_exists = os.path.isfile(os.path.join(getPackageDir('sims_sed_library'),
                                                     lens_gal_df['sedFilepath']))
            if sed_exists is False:
                if lens_sed_filepath_error is False:
                    errors_string = str(errors_string +
                                        "\nAGN lens galaxy SED does not exist. First error found in gal_id: %i" % u_id)
                    lens_sed_filepath_error = True
                    errors_present = True

        print('------------')
        print('AGN direct catalog input Results:')

        if errors_present is False:
            print('Pass: All instance catalog values within 0.005 of lensed system inputs. ' +
                  'All SED Filenames match.')
        else:
            raise CatalogError('\nFail:\n%s' % errors_string)

        print('------------')

        return


    def compare_sne_lens_inputs(self, spr_sne_lens_df):

        """
        This test makes sure that the SNe system lens galaxy properties that are replaced
        in Instance Catalogs by the sprinkler get inserted correctly. It will raise an
        error if the differences are outside a reasonable amount. The lens tests and
        the image tests for the SNe are separated out unlike the AGN since only the
        lens galaxies for sure show up in every Instance Catalog and extra work is
        required to keep track of the images in compare_sne_image_inputs below.

        Parameters
        ----------
        spr_sne_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled SNe
            systems. This is the output dataframe from process_sne_lenses.
        """

        if len(spr_sne_lens_df) == 0:
            return

        df = pd.read_csv(self.sprinkled_sne_data)

        errors_present = False
        phi_error = False
        z_lens_error = False
        lens_major_axis_error = False
        lens_minor_axis_error = False
        lens_sed_error = False
        lens_sed_filepath_error = False
        errors_string = "Errors in: "


        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            lens = df.query('twinkles_sysno == %i' % lens_gal_df['twinkles_system'])

            # These should just be different by a minus sign
            # Also making sure that this works for both entries in lens (should be the same anyway)
            if np.max(np.abs(lens['theta_e'] + lens_gal_df['positionAngle'])) > 0.005:
                if phi_error is False:
                    errors_string = errors_string + "\nPosition Angles. First error found in lens_gal_id: %i" % u_id
                    errors_present = True
                    phi_error = True

            # Redshifts should be identical
            if np.max(np.abs(lens['zl'] - lens_gal_df['redshift'])) > 0.005:
                if z_lens_error is False:
                    errors_string = errors_string + "\nLens Redshifts. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    z_lens_error = True

            d_a = np.max(np.abs(lens_gal_df['majorAxis'] - lens['lensgal_reff']/np.sqrt(1-lens['e'])))
            if d_a > 0.005:
                if lens_major_axis_error is False:
                    errors_string = errors_string + "\nLens Major Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_major_axis_error = True

            d_b = np.max(np.abs(lens_gal_df['minorAxis'] - lens['lensgal_reff']*np.sqrt(1-lens['e'])))
            if d_b > 0.005:
                if lens_minor_axis_error is False:
                    errors_string = errors_string + "\nLens Minor Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_minor_axis_error = True

            if (lens_gal_df['sedFilepath'] != lens['lensgal_sed'].values[0]):
                if lens_sed_error is False:
                    errors_string = errors_string + "\nSED Filename. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_sed_error = True


            sed_exists = os.path.isfile(os.path.join(getPackageDir('sims_sed_library'),
                                                     lens_gal_df['sedFilepath']))
            if sed_exists is False:
                if lens_sed_filepath_error is False:
                    errors_string = str(errors_string +
                                        "\nSNe lens galaxy SED does not exist. First error found in gal_id: %i" % u_id)
                    lens_sed_filepath_error = True
                    errors_present = True


        print('------------')
        print('SNe Lenses direct catalog input Results:')

        if errors_present is False:
            print('Pass: All instance catalog values within 0.005 of lensed system inputs. ' +
                  'All SED Filenames match.')
        else:
            raise CatalogError('\nFail:\n%s' % errors_string)

        print('------------')

        return

    def compare_agn_lens_mags(self, spr_agn_df, spr_agn_lens_df, bandpass_name):

        """
        This test makes sure that the AGN lens magnitudes replaced
        in Instance Catalogs by the sprinkler get inserted correctly.
        It will raise an error if the differences are outside a
        reasonable amount.

        Parameters
        ----------
        spr_agn_df: pandas dataframe
            Dataframe with the sprinkled AGN images from the Instance Catalog.
            This is the output dataframe from process_sprinkled_agn.

        spr_agn_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled AGN
            systems. This is the output dataframe from process_agn_lenses.

        bandpass_name: str
            one of 'ugrizy' (whatever the InstanceCatalog being validated
            corresponds to)
        """
        if len(spr_agn_df)==0 or len(spr_agn_lens_df)==0:
            if len(spr_agn_df)!=len(spr_agn_lens_df):
                msg = "\nlen(spr_agn_df): %d\n" % len(spr_agn_df)
                msg += "len(spr_agn_lens_df): %d\n" % len(spr_agn_lens_df)
                raise RuntimeError(msg)
            return

        db = om10.DB(catalog=self.sprinkled_agn_data, vb=False)

        lens_mag_error = []

        galDir = str(getPackageDir('sims_sed_library'))
        bandpassDict = BandpassDict.loadTotalBandpassesFromFiles(bandpassNames=['i'])
        norm_bp = Bandpass()
        norm_bp.imsimBandpass()

        dust_wavelen = None

        for lens_gal_row in spr_agn_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_agn_df.query('lens_galaxy_uID == %i' % u_id)
            use_lens = db.lenses['LENSID'][np.where(db.lenses['twinklesId'] ==
                                                    spr_sys_df['twinkles_system'].iloc[0])[0]]
            lens = db.get_lens(use_lens)
            num_img = lens['NIMG']

            # Because we allow magNorm to change between
            # bandpasses, we can only compare directly to
            # OM10's APMAG_I if this InstanceCatalog is actually
            # in the i-band.  If we are not in the i-band, we will
            # just have to compare magnorms
            if bandpass_name != 'i':
                bandpass_int = {'u':0, 'g':1, 'r':2,
                                'i':3, 'z':4, 'y':5}[bandpass_name]
                magnorm_shld = lens['sed_magNorm'][0][bandpass_int]
                dmag = lens_gal_df['phosimMagNorm'] - magnorm_shld
            elif bandpass_name == 'i':
                test_sed = Sed()
                test_sed.readSED_flambda(os.path.join(galDir,
                                                      lens_gal_df['sedFilepath']))

                fnorm = getImsimFluxNorm(test_sed, lens_gal_df['phosimMagNorm'])
                test_sed.multiplyFluxNorm(fnorm)

                if (dust_wavelen is None or
                    not np.array_equal(test_sed.wavelen, dust_wavelen)):

                    dust_wavelen = np.copy(test_sed.wavelen)
                    a_x, b_x = test_sed.setupCCM_ab()

                test_sed.addDust(a_x, b_x,
                                 A_v=lens_gal_df['internalAv'],
                                 R_v=lens_gal_df['internalRv'])

                test_sed.redshiftSED(lens_gal_df['redshift'], dimming=True)
                test_i_mag = test_sed.calcMag(bandpassDict['i'])
                dmag = test_i_mag-lens['APMAG_I']

            lens_mag_error.append(dmag)

        lens_mag_error = np.array(lens_mag_error)
        max_lens_mag_error = np.max(np.abs(lens_mag_error))

        print('------------')
        print('AGN Lens Magnitude Test Results (%d systems):' %
              len(lens_mag_error))

        if max_lens_mag_error < 0.01:
            print('Pass: Max lens phosim MagNorm error less than 0.01 mags.')
        else:
            raise CatalogError('\nFail: Max lens phosim MagNorm error is greater than 0.01 mags. ' +
                               'Max error is: %.4f mags.' % max_lens_mag_error)

        print('------------')

        return

    def compare_sne_lens_mags(self, spr_sne_lens_df, bandpass_name):

        """
        This test makes sure that the SNe system lens galaxy magnitudes that are replaced
        in Instance Catalogs by the sprinkler get inserted correctly. It will raise an
        error if the differences are outside a reasonable amount.

        Parameters
        ----------
        spr_sne_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled SNe
            systems. This is the output dataframe from process_sne_lenses.

        bandpass_name: str
            one of 'ugrizy'
        """

        if len(spr_sne_lens_df)==0:
            return

        df = pd.read_csv(self.sprinkled_sne_data)

        lens_mag_error = []

        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            lens = df.query('twinkles_sysno == %i' % lens_gal_df['twinkles_system'])

            # Even though SNe images don't appear in every image the lens galaxy should always
            # be in the instance catalog

            magnorm_name = 'lensgal_magnorm_%s' % bandpass_name
            lens_mag_error.append(lens[magnorm_name].iloc[0] -
                                  lens_gal_df['phosimMagNorm'])

        max_lens_mag_error = np.max(np.abs(lens_mag_error))

        print('------------')
        print('SNe Lens Magnitude Test Results:')

        if max_lens_mag_error < 0.01:
            print('Pass: Max lens phosim MagNorm error less than 0.01 mags.')
        else:
            raise CatalogError('\nFail: Max lens phosim MagNorm error is greater than 0.01 mags. ' +
                               'Max error is: %.4f mags.' % max_lens_mag_error)

        print('------------')

        return

    def compare_sne_image_inputs(self, spr_sne_df, spr_sne_lens_df, visit_mjd,
                                 sne_file_loc, sne_SED_path):

        """
        This test makes sure that the lensed SNe properties that are added
        to Instance Catalogs by the sprinkler get inserted correctly. It will raise an
        error if the differences are outside a reasonable amount. The lens tests and
        the image tests for the SNe are separated out unlike the AGN since only the
        lens galaxies for sure show up in every Instance Catalog and extra work is
        required to keep track of the images.

        Parameters
        ----------
        spr_sne_df: pandas dataframe
            Dataframe with the sprinkled SNe images from the Instance Catalog.
            This is the output dataframe from process_sprinkled_sne.

        spr_sne_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled SNe
            systems. This is the output dataframe from process_sne_lenses.

        visit_mjd: float
            The MJD of the Instance Catalog visit

        sne_file_loc: string
            The folder where the dynamically generated SNe SEDs are found

        sne_SED_path: string
            The path to the folder that contains the sne_file_loc folder.
        """
        if len(spr_sne_lens_df)==0:
            # spr_sne_df could have len 0 b/c SNe transience
            if len(spr_sn_df)!=len(spr_sne_lens_df):
                msg = "\nlen(spr_sn_df) %d\n" % len(spr_sn_df)
                msg += "len(spr_sne_lens_df) %d\n" % len(spr_sne_lens_df)
                raise RuntimeError(msg)
            return

        df = pd.read_csv(self.sprinkled_sne_data)

        errors_present = False
        z_s_error = False
        sed_error = False
        sed_filepath_error = False
        errors_string = 'Errors in:'

        for lens_gal_row in spr_sne_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_sne_df.query('lens_galaxy_uID == %i' % u_id)

            # There may be no images present in the current instance catalog
            if len(spr_sys_df) == 0:
                continue

            lens = df.query('twinkles_sysno == %i' % spr_sys_df['twinkles_system'].iloc[0])
            img_vals = spr_sys_df['image_number'].values

            for idx, image_on in list(enumerate(img_vals)):

                if np.abs(lens['zs'].iloc[image_on] -
                          spr_sys_df['redshift'].iloc[idx]) > 0.005:
                    if z_s_error is False:
                        errors_string = errors_string + "\nSNe Image Redshifts. First error found in gal_id: %i " % u_id
                        errors_present = True
                        z_lens_error = True

                sed_name = '%s/specFileGLSN_%i_%i_%.4f.txt.gz' % (sne_file_loc,
                                                                  spr_sys_df['twinkles_system'].iloc[0],
                                                                  image_on, visit_mjd)

                if (spr_sys_df['sedFilepath'].iloc[idx] != sed_name):
                    if sed_error is False:
                        errors_string = errors_string + "\nSNe Image SED Filename. First error found in gal_id: %i " % u_id
                        errors_string += '\n%s\nis not\n%s\n' % (spr_sys_df['sedFilepath'].iloc[idx], sed_name)
                        errors_present = True
                        sed_error = True

                sed_full_path = os.path.join(sne_SED_path, sed_name)
                sed_exists = os.path.isfile(sed_full_path)

            if sed_exists is False:
                if sed_filepath_error is False:
                    errors_string = str(errors_string +
                                        "\nSNe image SED does not exist. First error found in gal_id: %i" % u_id)
                    errors_string += "\n%s\ndoes not exist" % sed_full_path
                    sed_filepath_error = True
                    errors_present = True

        print('------------')
        print('SNe Images direct catalog input Results:')

        if errors_present is False:
            print('Pass: All instance catalog values within 0.005 of lensed system inputs. ' +
                  'All SED Filenames match.')
        else:
            raise CatalogError('\nFail:\n%s' % errors_string)

        print('------------')

        return

    def compare_agn_image_mags(self, spr_agn_df, spr_agn_lens_df, visit_mjd,
                               visit_band):

        """
        This test makes sure that the lensed AGN image magntiudes are correct
        for the MJD of the visit. This involves propagating the CatSim variability
        methods forward to the give MJD. It will raise an error if the differences
        are outside a reasonable amount.

        Parameters
        ----------
        spr_agn_df: pandas dataframe
            Dataframe with the sprinkled AGN images from the Instance Catalog.
            This is the output dataframe from process_sprinkled_sne.

        spr_agn_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled AGN
            systems. This is the output dataframe from process_agn_lenses.

        visit_mjd: float
            The MJD of the Instance Catalog visit

        visit_band: str
            The bandpass used for the Instance Catalog
        """
        if len(spr_agn_df)==0 or len(spr_agn_lens_df)==0:
            if len(spr_agn_df) != len(spr_agn_lens_df):
                msg = "\nlen(spr_agn_df): %d\n" % len(spr_agn_df)
                msg += "len(spr_agn_lens_df): %d\n" % len(spr_agn_lens_df)
                raise RuntimeError(msg)
            return

        db = om10.DB(catalog=self.sprinkled_agn_data, vb=False)

        agnSpecDir = 'agnSED'
        agnDir = str(getPackageDir('sims_sed_library') + '/' + agnSpecDir)
        bandpassDict = BandpassDict.loadTotalBandpassesFromFiles(bandpassNames=[visit_band])
        norm_bp = Bandpass()
        norm_bp.imsimBandpass()

        agn_var_params = self.load_agn_var_params()

        max_magNorm_err = 0.

        for lens_gal_row in spr_agn_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_agn_df.query('lens_galaxy_uID == %i' % u_id)
            agn_id = spr_sys_df['galaxy_id']
            use_lens = db.lenses['LENSID'][np.where(db.lenses['twinklesId'] ==
                                                    spr_sys_df['twinkles_system'].iloc[0])[0]]
            lens = db.get_lens(use_lens)
            num_img = lens['NIMG']

            mag = lens['MAG'].data[0]
            lensed_mags = spr_sys_df['phosimMagNorm']
            corrected_mags = []

            for i in range(num_img.data[0]):

                d_mags = self.get_agn_variability_mags(agn_var_params[str(agn_id.values[0])],
                                                       lens['DELAY'].data[0][i], visit_mjd,
                                                       spr_sys_df['redshift'].values[0])


                test_sed = Sed()
                test_sed.readSED_flambda('%s/%s' % (agnDir, 'agn.spec.gz'))
                test_sed.redshiftSED(lens['ZSRC'])
                test_f_norm = getImsimFluxNorm(test_sed, lensed_mags.values[i])
                test_sed.multiplyFluxNorm(test_f_norm)
                test_mag = test_sed.calcMag(bandpassDict[visit_band])
                test_f_norm_2 = test_sed.calcFluxNorm(test_mag - d_mags[visit_band],
                                                      bandpassDict[visit_band])
                test_sed.multiplyFluxNorm(test_f_norm_2)
                test_mag_2 = test_sed.calcMag(norm_bp)
                test_mag_3 = test_mag_2 + 2.5*np.log10(np.abs(mag)[i])

                corrected_mags.append(test_mag_3)

            corrected_mags = np.array(corrected_mags)
            max_error = np.max(np.abs(corrected_mags -
                                      agn_var_params[str(agn_id.values[0])]
                                      ['magNorm_static']))

            if max_error > max_magNorm_err:
                max_magNorm_err = max_error

        print('------------')
        print('AGN Image Magnitude Test Results:')

        if max_magNorm_err < 0.001:
            print('Pass: Image MagNorms are within 0.001 of correct values.')
        else:
            raise CatalogError('\nFail: Max image phosim MagNorm error is greater than 0.001 mags. ' +
                               'Max error is: %.4f mags.' % max_magNorm_err)

        print('------------')

        return

    def get_agn_variability_mags(self, var_param_dict, time_delay, mjd, redshift):

        """
        Use CatSim variability methods to get the variability offset from the baseline
        magnitude for AGN at the given MJD also taking into account the time delay.

        Parameters
        ----------
        var_param_dict: dictionary
            The AGN variability parameters from the input AGN database

        time_delay: float
            The time delay for the given image in the lensed system

        mjd: float
            The MJD for the Instance Catalog visit

        redshift: float
            The redshift of the AGN
        """

        def return_num_obj(params):
            return 1

        eg_test = egvar()
        eg_test.num_variable_obj = return_num_obj

        var_mags = eg_test.applyAgn([[0]], var_param_dict,
                                    mjd-time_delay,
                                    redshift=np.array([redshift]))

        filters = ['u', 'g', 'r', 'i', 'z', 'y']
        var_mag_dict = {x:y for x,y in zip(filters, var_mags)}

        return var_mag_dict


    def load_agn_var_params(self):
        """
        Load parameters for AGN in the DDF.  Currently, the method
        loads from a hard-coded sqlite database; in the future, we will
        make the database name a user-defined parameter.
        """

        db_file = '/global/projecta/projectdirs/lsst'
        db_file = os.path.join(db_file, 'groups', 'SSim', 'DC2')
        db_file = os.path.join(db_file, 'cosmoDC2_v1.1.4')
        db_file = os.path.join(db_file, 'agn_db_mbh7_mi30_sf4.db')

        if not os.path.isfile(db_file):
            raise RuntimeError("\n%s\n\nis not a file\n" % db_file)

        agn_param_query = 'SELECT galaxy_id, magNorm, varParamStr '
        agn_param_query += 'FROM agn_params'

        # only select those AGN that are in the DDF
        ddf_halfspace = htm.halfSpaceFromRaDec(53.125, -28.100, 0.6)
        htm_8_bounds = ddf_halfspace.findAllTrixels(8)

        agn_param_query += ' WHERE ('
        for i_bound, bound in enumerate(htm_8_bounds):
            if i_bound>0:
                agn_param_query += ' OR '
            if bound[0] == bound[1]:
                agn_param_query += 'htmid_8==%d' % bound[0]
            else:
                agn_param_query += '(htmid_8>=%d AND htmid_i<=%d)' % (bound[0],
                                                                       bound[1])
        agn_param_query += ')'

        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            results = c.execute(agn_param_query).fetchall()

        agn_var_params = {}

        for line in results:
            line_id = int(line[0])
            line_magNorm = float(line[1])
            var_dict = json.loads(line[2])['p']
            new_var_dict = {key:np.array([val])
                            for key, val in var_dict.items()}
            new_var_dict['magNorm_static'] = np.float(line_magNorm)
            agn_var_params[str(line_id)] = new_var_dict

        return agn_var_params

    def compare_sne_image_mags(self, spr_sne_df, spr_sne_lens_df, visit_mjd,
                               visit_band):

        """
        This test makes sure that the lensed SNe image magntiudes are correct
        for the MJD of the visit. This involves propagating the CatSim variability
        methods forward to the give MJD. It will raise an error if the differences
        are outside a reasonable amount.

        Parameters
        ----------
        spr_sne_df: pandas dataframe
            Dataframe with the sprinkled SNe images from the Instance Catalog.
            This is the output dataframe from process_sprinkled_sne.

        spr_sne_lens_df: pandas dataframe
            Dataframe with the sprinkled lens galaxies for the sprinkled SNe
            systems. This is the output dataframe from process_sne_lenses.

        visit_mjd: float
            The MJD of the Instance Catalog visit

        visit_band: str
            The bandpass used for the Instance Catalog
        """
        if len(spr_sne_lens_df)==0:
            # spr_sne_df could have len==0 b/c SNe transience
            if len(spr_sne_lens_df) != len(spr_sne_df):
                msg = "\nlen(spr_sne_df): %d\n" % len(spr_sne_df)
                msg += "len(spr_sne_lens_df): %d\n" % len(spr_sne_lens_df)
                raise RuntimeError(msg)
            return

        sn_obj = SNObject(0., 0.)

        df = pd.read_csv(self.sprinkled_sne_data)

        bandpassDict = BandpassDict.loadTotalBandpassesFromFiles(bandpassNames=[visit_band])
        norm_bp = Bandpass()
        norm_bp.imsimBandpass()

        max_flux_err = 0.

        print('------------')
        print('SNe Image Magnitude Test Results:')

        for lens_gal_row in spr_sne_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_sne_df.query('lens_galaxy_uID == %i' % u_id)

            # There may be no images present in the current instance catalog
            if len(spr_sys_df) == 0:
                continue

            lens = df.query('twinkles_sysno == %i' % spr_sys_df['twinkles_system'].iloc[0])
            img_vals = spr_sys_df['image_number'].values

            magnification = lens['mu']
            lensed_mags = spr_sys_df['phosimMagNorm'].values
            corrected_mags = []

            for idx, image_on in list(enumerate(img_vals)):

                magnorm = self.get_sne_variability_mags(lens.iloc[image_on],
                                                        spr_sys_df['raPhoSim'].values[idx],
                                                        spr_sys_df['decPhoSim'].values[idx],
                                                        visit_mjd, sn_obj, norm_bp,
                                                        bandpassDict[visit_band])
                test_mag  = magnorm - 2.5*np.log10(np.abs(magnification.iloc[image_on]))

                corrected_mags.append(test_mag)

            corrected_mags = np.array(corrected_mags)
            d_mag = np.abs(corrected_mags-lensed_mags)

            dummy_sed = Sed()
            flux_truth = dummy_sed.fluxFromMag(lensed_mags)
            flux_instcat = dummy_sed.fluxFromMag(corrected_mags)
            dflux = np.abs(flux_truth-flux_instcat)

            # these are the "single image depth designed" from
            # table 1 of the LSST overview paper (with an extra
            # magnitude added on)
            fiducial_m5 = {'u':24.9, 'g':26.0, 'r':25.7,
                           'i':25.0, 'z':24.3, 'y':23.1}[visit_band]

            (snr,
             gamma) = calcSNR_m5(lensed_mags, self.lsst_bp_dict[visit_band],
                                 fiducial_m5, self.phot_params,
                                 gamma=self.sn_gamma_dict[visit_band])

            self.sn_gamma_dict[visit_band] = gamma
            noise = flux_truth/snr
            dflux_over_noise = dflux/noise

            bright_mask = lensed_mags<fiducial_m5

            # more lax criterion for dim SNe
            dim_dmag = d_mag[~bright_mask]
            if len(dim_dmag) > 0:
                dim_dmag_max = dim_dmag.max()
                if dim_dmag_max > 0.01:
                    raise CatalogError("Among dim SNe, max dmag is %e" %
                                       (dim_dmag_max))

            max_error = dflux_over_noise.max()
            if max_error > max_flux_err:
                max_flux_err = max_error
                max_dex = np.argmax(dflux_over_noise)
                offending_mag = lensed_mags[max_dex]
                offending_dmag = lensed_mags[max_dex]-corrected_mags[max_dex]
                print('err %e mag %e dmag %e (fiducial_m5 %e)' %
                      (max_error, offending_mag, offending_dmag, fiducial_m5))

        if max_flux_err < 0.1:
            print('Pass: Image MagNorms are within 0.001 of correct values.')
        else:
            raise CatalogError('\nFail: Max discrepancy in flux ' +
                               'is greater than 0.1 * noise. ' +
                               'Max dflux/noise is: %.4f .' % (max_flux_err))

        print('------------')

        return

    def get_sne_variability_mags(self, system_df, sn_ra, sn_dec, visit_mjd, sn_obj,
                                 norm_bp, visit_bp):

        sn_param_dict = copy.deepcopy(sn_obj.SNstate)
        sn_param_dict['_ra'] = np.radians(sn_ra)
        sn_param_dict['_dec'] = np.radians(sn_dec)
        sn_param_dict['z'] = system_df['zs']
        sn_param_dict['c'] = system_df['c']
        sn_param_dict['x0'] = system_df['x0']
        sn_param_dict['x1'] = system_df['x1']
        sn_param_dict['t0'] = system_df['t_start']

        current_sn_obj = sn_obj.fromSNState(sn_param_dict)
        current_sn_obj.mwEBVfromMaps()
        sn_magnorm = current_sn_obj.catsimBandMag(norm_bp, visit_mjd)

        return sn_magnorm
