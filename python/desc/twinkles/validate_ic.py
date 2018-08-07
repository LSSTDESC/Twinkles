import os
import om10
import pandas as pd
import numpy as np
import gzip
import shutil
import copy
from lsst.utils import getPackageDir
from lsst.sims.photUtils import Bandpass, BandpassDict, Sed
from lsst.sims.catUtils.supernovae import SNObject
from lsst.sims.catUtils.mixins.VariabilityMixin import ExtraGalacticVariabilityModels as egvar


__all__ = ['validate_ic']


class CatalogError(Exception):
    """Raised when Instance Catalog entries do not pass expected tests."""
    pass

class validate_ic(object):

    def __init__(self):

        return

    def load_cat(self, ic_folder, visit_num, sn_file_prefix):

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

        df_agn = pd.read_csv(os.path.join(ic_folder, 'agn%s' % ic_file),
                             delimiter=' ', header=None,
                             names=base_columns+['internalExtinctionModel',
                                                 'galacticExtinctionModel',
                                                 'galacticAv', 'galacticRv'])

        df_sne = pd.read_csv(os.path.join(ic_folder, 'agn%s' % ic_file),
                             delimiter=' ', header=None,
                             names=base_columns+['internalExtinctionModel',
                                                 'galacticExtinctionModel',
                                                 'galacticAv', 'galacticRv'])

        return df_galaxy, df_agn, df_sne

    def process_sprinkled_agn(self, df_agn):

        galtileids = []
        twinkles_system = []
        twinkles_im_num = []
        galtile_list = np.genfromtxt(os.path.join(os.environ['TWINKLES_DIR'],
                                                  'data', 'dc2_agn_cache.csv'),
                                     delimiter=',', names=True, dtype=np.int)
        
        i=0
        keep_idx = []
        for agn_id in df_agn['uniqueId']:
            twinkles_ids = np.right_shift(agn_id-117, 10)
            galtileid = int(twinkles_ids/10000)
            if galtileid in galtile_list['galtileid']:
                keep_idx.append(i)
                galtileids.append(galtileid)
                twinkles_num = np.int(str(twinkles_ids)[-4:])
                twinkles_system.append(twinkles_num // 4)
                twinkles_im_num.append(twinkles_num % 4)
                
            i+=1

        galtileids = np.array(galtileids, dtype=np.int)
        sprinkled_agn = df_agn.iloc[np.array(keep_idx)]
        sprinkled_agn = sprinkled_agn.reset_index(drop=True)
        sprinkled_agn['galaxy_id'] = galtileids
        sprinkled_agn['twinkles_system'] = twinkles_system
        sprinkled_agn['image_number'] = twinkles_im_num
        sprinkled_agn['lens_galaxy_uID'] = np.left_shift(galtileids, 10) + 97
        sprinkled_agn['host_galaxy_bulge_uID'] = np.array(np.left_shift(galtileids*10000
                                                    + np.array(twinkles_system, dtype=np.int)*4 +
                                                    np.array(twinkles_im_num, dtype=np.int), 10) + 97, dtype=np.int)
        sprinkled_agn['host_galaxy_disk_uID'] = np.array(np.left_shift(galtileids*10000
                                                    + np.array(twinkles_system, dtype=np.int)*4 +
                                                    np.array(twinkles_im_num, dtype=np.int), 10) + 107, dtype=np.int)
            
        return sprinkled_agn

    def process_hosts(self, sprinkled_df, df_galaxy):

        host_bulge_locs = []
        host_disk_locs = []
        for bulge_idx, disk_idx in zip(sprinkled_df['host_galaxy_bulge_uID'],
                                       sprinkled_df['host_galaxy_disk_uID']):
            bulge_matches = np.where(df_galaxy['uniqueId'] == bulge_idx)[0]
            disk_matches = np.where(df_galaxy['uniqueId'] == disk_idx)[0]
            for bulge_match, disk_match in zip(bulge_matches, disk_matches):
                host_bulge_locs.append(bulge_match)
                host_disk_locs.append(disk_match)

        host_bulges = df_galaxy.iloc[np.unique(host_bulge_locs)]
        host_bulges = host_bulges.reset_index(drop=True)
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
        These must be done differently since the lens galaxy for SNe
        will not have associated images in every instance catalog.
        """

        galtile_list = np.genfromtxt(os.path.join(os.environ['TWINKLES_DIR'],
                                                  'data', 'dc2_sne_cache.csv'),
                                     delimiter=',', names=True, dtype=np.int)

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
                

    def process_sprinkled_sne(self, df_sne):

        galtileids = []
        twinkles_system = []
        twinkles_im_num = []
        galtile_list = np.genfromtxt(os.path.join(os.environ['TWINKLES_DIR'],
                                                  'data', 'dc2_sne_cache.csv'),
                                     delimiter=',', names=True, dtype=np.int)
        
        i=0
        keep_idx = []
        for sne_idx, sne_row in df_sne.iterrows():
            if sne_row['sedFilepath'].startswith('Dynamic'):
                sne_id = sne_row['uniqueId']
                twinkles_ids = np.right_shift(sne_id-117, 10)
                galtileid = int(twinkles_ids/10000)
                if galtileid in galtile_list['galtileid']:
                    keep_idx.append(i)
                    galtileids.append(galtileid)
                    twinkles_num = np.int(str(twinkles_ids)[-4:])
                    twinkles_system.append(twinkles_num // 4)
                    twinkles_im_num.append(twinkles_num % 4)
                
            i+=1

        galtileids = np.array(galtileids, dtype=np.int)
        sprinkled_sne = df_sne.iloc[np.array(keep_idx)]
        sprinkled_sne = sprinkled_sne.reset_index(drop=True)
        sprinkled_sne['galaxy_id'] = galtileids
        sprinkled_sne['twinkles_system'] = twinkles_system
        sprinkled_sne['image_number'] = twinkles_im_num
        sprinkled_sne['lens_galaxy_uID'] = np.left_shift(np.array(galtileids, dtype=np.int), 10) + 97
        sprinkled_sne['host_galaxy_bulge_uID'] = np.array(np.left_shift(galtileids*10000
                                                    + np.array(twinkles_system, dtype=np.int)*4 +
                                                    np.array(twinkles_im_num, dtype=np.int), 10) + 97,
                                                    dtype=np.int)
        sprinkled_sne['host_galaxy_disk_uID'] = np.array(np.left_shift(galtileids*10000
                                                    + np.array(twinkles_system, dtype=np.int)*4 +
                                                    np.array(twinkles_im_num, dtype=np.int), 10) + 107,
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
        
        db = om10.DB(catalog=os.path.join(os.environ['TWINKLES_DIR'], 'data', 
                                          'twinkles_lenses_v2.fits'), vb=False)

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
        
        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

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

            # This is just to make sure there are at least some images when we expect
            # and the previous line is not just skipping everything.
            images_tested += 1

            lens = df.query('twinkles_sysno == %i' % spr_sys_df['twinkles_system'].iloc[0])
            # SNe systems might not have all images appearing in an instance catalog unlike AGN
            img_vals = spr_sys_df['image_number'].values
            
            for img_idx in range(len(img_vals)):
                # Calculate the offsets from the lens galaxy position
                offset_x1, offset_y1 = self.offset_on_sky(spr_sys_df['raPhoSim'].iloc[img_idx], 
                                                          spr_sys_df['decPhoSim'].iloc[img_idx],
                                                          lens_gal_df['raPhoSim'],
                                                          lens_gal_df['decPhoSim'])

                x_offsets.append(offset_x1-lens['x'].iloc[img_vals[img_idx]])
                y_offsets.append(offset_y1-lens['y'].iloc[img_vals[img_idx]])
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
        This test compares the things that get swapped in directly from the input catalog.
        """
        
        db = om10.DB(catalog=os.path.join(os.environ['TWINKLES_DIR'], 'data', 
                                          'twinkles_lenses_v2.fits'), vb=False)

        errors_present = False
        phi_error = False
        z_lens_error = False
        z_src_error = False
        lens_major_axis_error = False
        lens_minor_axis_error = False
        lens_sed_error = False
        errors_string = "Errors in: "

        for lens_gal_row in spr_agn_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_agn_df.query('lens_galaxy_uID == %i' % u_id)
            use_lens = db.lenses['LENSID'][np.where(db.lenses['twinklesId'] == 
                                                    spr_sys_df['twinkles_system'].iloc[0])[0]]
            lens = db.get_lens(use_lens)

            # These should just be different by a minus sign
            if lens['PHIE'] + lens_gal_df['positionAngle'] > 0.005:
                if phi_error is False:
                    errors_string = errors_string + "\nPosition Angles. First error found in lens_gal_id: %i" % u_id
                    errors_present = True
                    phi_error = True

            # Redshifts should be identical
            if lens['ZLENS'] - lens_gal_df['redshift'] > 0.005:
                if z_error is False:
                    errors_string = errors_string + "\nLens Redshifts. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    z_lens_error = True

            if np.max(lens['ZSRC'] - spr_sys_df['redshift'].values) > 0.005:
                if z_src_error is False:
                    errors_string = errors_string + "\nSource Redshifts. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    z_src_error = True

            if (lens_gal_df['majorAxis'] - lens['REFF']/np.sqrt(1-lens['ELLIP'])) > 0.005:
                if lens_major_axis_error is False:
                    errors_string = errors_string + "\nLens Major Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_major_axis_error = True

            if (lens_gal_df['minorAxis'] - lens['REFF']/np.sqrt(1+lens['ELLIP'])) > 0.005:
                if lens_minor_axis_error is False:
                    errors_string = errors_string + "\nLens Minor Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_minor_axis_error = True

            if (lens_gal_df['sedFilepath'] != lens['lens_sed'][0]):
                if lens_sed_error is False:
                    errors_string = errors_string + "\nSED Filename. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_sed_error = True                    
        
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
        This test compares the things that get swapped in directly from the input catalog.
        """

        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

        errors_present = False
        phi_error = False
        z_lens_error = False
        lens_major_axis_error = False
        lens_minor_axis_error = False
        lens_sed_error = False
        errors_string = "Errors in: "


        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            lens = df.query('twinkles_sysno == %i' % lens_gal_df['twinkles_system'])

            # These should just be different by a minus sign
            # Also making sure that this works for both entries in lens (should be the same anyway)
            if np.max(lens['theta_e'] + lens_gal_df['positionAngle']) > 0.005:
                if phi_error is False:
                    errors_string = errors_string + "\nPosition Angles. First error found in lens_gal_id: %i" % u_id
                    errors_present = True
                    phi_error = True

            # Redshifts should be identical
            if np.max(lens['zl'] - lens_gal_df['redshift']) > 0.005:
                if z_error is False:
                    errors_string = errors_string + "\nLens Redshifts. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    z_lens_error = True

            if np.max((lens_gal_df['majorAxis'] - lens['r_eff']/np.sqrt(1-lens['e']))) > 0.005:
                if lens_major_axis_error is False:
                    errors_string = errors_string + "\nLens Major Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_major_axis_error = True

            if np.max((lens_gal_df['minorAxis'] - lens['r_eff']/np.sqrt(1+lens['e']))) > 0.005:
                if lens_minor_axis_error is False:
                    errors_string = errors_string + "\nLens Minor Axis. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_minor_axis_error = True

            if (lens_gal_df['sedFilepath'] != lens['lens_sed'].values[0]):
                if lens_sed_error is False:
                    errors_string = errors_string + "\nSED Filename. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_sed_error = True
        
        print('------------')
        print('SNe Lenses direct catalog input Results:')

        if errors_present is False:
            print('Pass: All instance catalog values within 0.005 of lensed system inputs. ' +
                  'All SED Filenames match.')
        else:
            raise CatalogError('\nFail:\n%s' % errors_string)

        print('------------')

        return

    def compare_agn_lens_mags(self, spr_agn_df, spr_agn_lens_df):

        """
        This test compares the lens magnitudes.
        """
        
        db = om10.DB(catalog=os.path.join(os.environ['TWINKLES_DIR'], 'data', 
                                          'twinkles_lenses_v2.fits'), vb=False)

        lens_mag_error = []

        galSpecDir = 'galaxySED'
        galDir = str(getPackageDir('sims_sed_library') + '/' + galSpecDir)
        bandpassDict = BandpassDict.loadTotalBandpassesFromFiles(bandpassNames=['i'])
        norm_bp = Bandpass()
        norm_bp.imsimBandpass()

        for lens_gal_row in spr_agn_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_agn_df.query('lens_galaxy_uID == %i' % u_id)
            use_lens = db.lenses['LENSID'][np.where(db.lenses['twinklesId'] == 
                                                    spr_sys_df['twinkles_system'].iloc[0])[0]]
            lens = db.get_lens(use_lens)
            num_img = lens['NIMG']

            test_sed = Sed()
            test_sed.readSED_flambda('%s/%s' % (galDir, lens['lens_sed'][0]))
            test_sed.redshiftSED(lens['ZLENS'])
            test_f_norm = test_sed.calcFluxNorm(lens['APMAG_I'], bandpassDict['i'])
            test_sed.multiplyFluxNorm(test_f_norm)
            test_mag = test_sed.calcMag(norm_bp)
            lens_mag_error.append(test_mag - lens_gal_df['phosimMagNorm'])


        max_lens_mag_error = np.max(np.abs(lens_mag_error))

        print('------------')
        print('AGN Lens Magnitude Test Results:')

        if max_lens_mag_error < 0.01:
            print('Pass: Max lens phosim MagNorm error less than 0.01 mags.')
        else:
            raise CatalogError('\nFail: Max lens phosim MagNorm error is greater than 0.01 mags. ' + 
                               'Max error is: %.4f mags.' % max_lens_mag_error)

        print('------------')

        return

    def compare_sne_lens_mags(self, spr_sne_lens_df):

        """
        This test compares the things that get swapped in directly from the input catalog.
        """

        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

        lens_mag_error = []

        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            lens = df.query('twinkles_sysno == %i' % lens_gal_df['twinkles_system'])

            # Even though SNe images don't appear in every image the lens galaxy should always
            # be in the instance catalog
            
            lens_mag_error.append(lens['bulge_magnorm'].iloc[0] -
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
                                 sne_file_loc):

        """
        This test compares the image inputs from catalog.
        """

        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

        errors_present = False
        z_s_error = False
        sed_error = False
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
                
                if lens['zs'].iloc[image_on] - spr_sys_df['redshift'].iloc[idx] > 0.005:
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
                        errors_present = True
                        sed_error = True
        
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
        This test compares the image magnitudes.
        """
        
        db = om10.DB(catalog=os.path.join(os.environ['TWINKLES_DIR'], 'data', 
                                          'twinkles_lenses_v2.fits'), vb=False)

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
                test_f_norm = test_sed.calcFluxNorm(lensed_mags.values[i], norm_bp)
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

        agn_var_params = {}

        with open(os.path.join(os.environ['TWINKLES_DIR'], 'data', 
                                          'agn_validation_params.txt'), 'r') as f:
            for line in f:
                line_id = line.split(',')[0]
                line_magNorm = line.split(',')[3]
                
                var_param_dict = {x.split(':')[0][2:-1]:np.array([np.float(x.split(':')[1])]) 
                                  for x in line.split('{')[2][:-3].split(',')}

                # Some munging from the way we made the dict
                var_param_dict['seed'] = np.array(var_param_dict['eed'], dtype=int)
                var_param_dict['magNorm_static'] = np.float(line_magNorm)
                del var_param_dict['eed']

                agn_var_params[str(line_id)] = var_param_dict

        return agn_var_params

    def compare_sne_image_mags(self, spr_sne_df, spr_sne_lens_df, visit_mjd,
                               visit_band):

        """
        This test compares the image magnitudes.
        """
        
        sn_obj = SNObject(0., 0.)

        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

        bandpassDict = BandpassDict.loadTotalBandpassesFromFiles(bandpassNames=[visit_band])
        norm_bp = Bandpass()
        norm_bp.imsimBandpass()

        max_magNorm_err = 0.

        for lens_gal_row in spr_sne_lens_df.iterrows():

            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_sne_df.query('lens_galaxy_uID == %i' % u_id)

            # There may be no images present in the current instance catalog
            if len(spr_sys_df) == 0:
                continue

            lens = df.query('twinkles_sysno == %i' % spr_sys_df['twinkles_system'].iloc[0])
            img_vals = spr_sys_df['image_number'].values

            mag = lens['mu']
            lensed_mags = spr_sys_df['phosimMagNorm']
            corrected_mags = []

            for idx, image_on in list(enumerate(img_vals)):
            
                magnorm = self.get_sne_variability_mags(lens.iloc[image_on],
                                                        spr_sys_df['raPhoSim'].values[idx],
                                                        spr_sys_df['decPhoSim'].values[idx],
                                                        visit_mjd, sn_obj, norm_bp,
                                                        bandpassDict[visit_band])
                test_mag  = magnorm - 2.5*np.log10(np.abs(mag.iloc[image_on]))
                
                corrected_mags.append(test_mag)

            corrected_mags = np.array(corrected_mags)
            max_error = np.max(np.abs(corrected_mags - 
                                      lensed_mags))

            if max_error > max_magNorm_err:
                max_magNorm_err = max_error

        print('------------')
        print('SNe Image Magnitude Test Results:')

        if max_magNorm_err < 0.001:
            print('Pass: Image MagNorms are within 0.001 of correct values.')
        else:
            raise CatalogError('\nFail: Max image phosim MagNorm error is greater than 0.001 mags. ' + 
                               'Max error is: %.4f mags.' % max_magNorm_err)

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
