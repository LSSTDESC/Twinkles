import os
import om10
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gzip
import shutil
from lsst.utils import getPackageDir
from lsst.sims.photUtils import Bandpass, BandpassDict, Sed

from lsst.sims.catUtils.mixins.VariabilityMixin import ExtraGalacticVariabilityModels as egvar


__all__ = ['validate_ic']


class validate_ic(object):

    def __init__(self):

        return

    def load_cat(self, ic_file, sn_file_prefix):

        i=0
        not_star_rows = []
        not_galaxy_rows = []
        not_agn_rows = []
        not_sne_rows = []

        if ic_file.endswith('.gz'):
            reader_func = gzip.open
        else:
            reader_func = open

        with reader_func(ic_file, 'rb') as f:
            for line in f:

                new_str = line.decode('utf8').split(' ')

                # Skip through the header
                if len(new_str) < 4:
                    not_star_rows.append(i)
                    not_galaxy_rows.append(i)
                    not_agn_rows.append(i)
                    not_sne_rows.append(i)
                    i += 1
                    continue

                if new_str[5].startswith('starSED'):
                    not_galaxy_rows.append(i)
                    not_agn_rows.append(i)
                    not_sne_rows.append(i)
                elif new_str[5].startswith('galaxySED'):
                    not_star_rows.append(i)
                    not_agn_rows.append(i)
                    not_sne_rows.append(i)
                elif new_str[5].startswith('agnSED'):
                    not_star_rows.append(i)
                    not_galaxy_rows.append(i)
                    not_sne_rows.append(i)
                elif new_str[5].startswith(sn_file_prefix):
                    not_star_rows.append(i)
                    not_galaxy_rows.append(i)
                    not_agn_rows.append(i)
                i += 1

        base_columns = ['prefix', 'uniqueId', 'raPhoSim', 'decPhoSim',
                        'phosimMagNorm', 'sedFilepath', 'redshift',
                        'shear1', 'shear2', 'kappa', 'raOffset', 'decOffset',
                        'spatialmodel']

        df_galaxy = pd.read_csv(ic_file, delimiter=' ', header=None,
                                names=base_columns+['majorAxis', 'minorAxis',
                                                    'positionAngle', 'sindex',
                                                    'internalExtinctionModel',
                                                    'internalAv', 'internalRv',
                                                    'galacticExtinctionModel',
                                                    'galacticAv', 'galacticRv'],
                                skiprows=not_galaxy_rows)

        df_agn = pd.read_csv(ic_file, delimiter=' ', header=None,
                             names=base_columns+['internalExtinctionModel',
                                                 'galacticExtinctionModel',
                                                 'galacticAv', 'galacticRv'],
                             skiprows=not_agn_rows)

        df_sne = pd.read_csv(ic_file, delimiter=' ', header=None,
                             names=base_columns+['internalExtinctionModel',
                                                 'galacticExtinctionModel',
                                                 'galacticAv', 'galacticRv'],
                             skiprows=not_sne_rows)

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

    def process_lenses(self, sprinkled_df, df_galaxy):

        lens_gal_locs = []
        for idx in sprinkled_df['lens_galaxy_uID'].values:
            matches = np.where(df_galaxy['uniqueId'] == idx)[0]
            for match in matches:
                lens_gal_locs.append(match)

        lens_gals = df_galaxy.iloc[np.unique(lens_gal_locs)]
        lens_gals = lens_gals.reset_index(drop=True)

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
        for sne_id in df_sne['uniqueId']:
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
                                                    np.array(twinkles_im_num, dtype=np.int), 10) + 97, dtype=np.int)
        sprinkled_sne['host_galaxy_disk_uID'] = np.array(np.left_shift(galtileids*10000
                                                    + np.array(twinkles_system, dtype=np.int)*4 +
                                                    np.array(twinkles_im_num, dtype=np.int), 10) + 107, dtype=np.int)

            
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

    
    def overlay_ic_system(self, spr_agn_df, spr_agn_lens_df):

        db = om10.DB(catalog=os.path.join(os.environ['TWINKLES_DIR'], 'data', 
                                          'twinkles_lenses_v2.fits'))
        use_lens = db.lenses['LENSID'][np.where(db.lenses['twinklesId'] == 
                                                spr_agn_df['twinkles_system'].iloc[0])[0]]
        lens = db.get_lens(use_lens[0])

        print(lens['XIMG'], lens['YIMG'])
        
        om10.plot_lens(lens)
        
        # Calculate the offsets from the lens galaxy position
        offset_x1, offset_y1 = self.offset_on_sky(spr_agn_df['raPhoSim'].iloc[0], 
                                                  spr_agn_df['decPhoSim'].iloc[0],
                                                  spr_agn_lens_df['raPhoSim'],
                                                  spr_agn_lens_df['decPhoSim'])
        offset_x2, offset_y2 = self.offset_on_sky(spr_agn_df['raPhoSim'].iloc[1], 
                                                  spr_agn_df['decPhoSim'].iloc[1],
                                                  spr_agn_lens_df['raPhoSim'],
                                                  spr_agn_lens_df['decPhoSim'])
        # offset_x3, offset_y3 = self.offset_on_sky(spr_agn_df['raPhoSim'].iloc[2], 
        #                                           spr_agn_df['decPhoSim'].iloc[2],
        #                                           spr_agn_lens_df['raPhoSim'],
        #                                           spr_agn_lens_df['decPhoSim'])
        # offset_x4, offset_y4 = self.offset_on_sky(spr_agn_df['raPhoSim'].iloc[3], 
        #                                           spr_agn_df['decPhoSim'].iloc[3],
        #                                           spr_agn_lens_df['raPhoSim'],
        #                                           spr_agn_lens_df['decPhoSim'])
        # offset_lens_ra, offset_lens_dec = self.offset_on_sky

        
        plt.scatter(offset_x1, offset_y1, c='r', marker='o', s=188, alpha=0.4, label='Catalog Image 1')
        plt.scatter(offset_x2, offset_y2, c='r', marker='o', s=188, alpha=0.4, label='Catalog Image 2')
        # plt.scatter(offset_x3, offset_y3, c='r', marker='o', s=188, alpha=0.4, label='Catalog Image 3')
        # plt.scatter(offset_x4, offset_y4, c='r', marker='o', s=188, alpha=0.4, label='Catalog Image 4')
                
        return 

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


        # print(np.histogram(x_offsets))
        # print(np.histogram(y_offsets))
        # print(np.histogram(total_offsets))
        # max_x_err = np.max(np.abs(x_offsets))
        # max_y_err = np.max(np.abs(y_offsets))
        max_total_err = np.max(total_offsets)

        print('------------')
        print('AGN Location Test Results:')

        if max_total_err < 0.01:
            print('Pass: Max image offset error less than 1 percent')
        else:
            print('Fail: Max image offset error greater than 1 percent. ' + 
                  'Max total offset error is: %.4f percent.' % max_total_err)

        print('------------')

        return

    def compare_sne_location(self, spr_sne_df, spr_sne_lens_df):
        
        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

        x_offsets = []
        y_offsets = []
        total_offsets = []

        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_sne_df.query('lens_galaxy_uID == %i' % u_id)
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

        # print(np.histogram(x_offsets))
        # print(np.histogram(y_offsets))
        # print(np.histogram(total_offsets))
        # max_x_err = np.max(np.abs(x_offsets))
        # max_y_err = np.max(np.abs(y_offsets))
        max_total_err = np.max(total_offsets)

        print('------------')
        print('SNE Location Test Results:')

        if max_total_err < 0.01:
            print('Pass: Max image offset error less than 1 percent')
        else:
            print('Fail: Max image offset error greater than 1 percent. ' + 
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

            if (lens_gal_df['sedFilepath'] != 'galaxySED/%s.gz' % lens['lens_sed'][0]):
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
            print('Fail:')
            print(errors_string)

        print('------------')

        return


    def compare_sne_inputs(self, spr_sne_df, spr_sne_lens_df):

        """
        This test compares the things that get swapped in directly from the input catalog.
        """

        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

        errors_present = False
        phi_error = False
        z_lens_error = False
        z_src_error = False
        lens_major_axis_error = False
        lens_minor_axis_error = False
        lens_sed_error = False
        errors_string = "Errors in: "


        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_sne_df.query('lens_galaxy_uID == %i' % u_id)
            lens = df.query('twinkles_sysno == %i' % spr_sys_df['twinkles_system'].iloc[0])

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

            if np.max(lens['zs'] - spr_sys_df['redshift'].values) > 0.005:
                if z_src_error is False:
                    errors_string = errors_string + "\nSource Redshifts. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    z_src_error = True

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

            if (len(np.unique(lens['lens_sed'].values) == 1) and 
                (lens_gal_df['sedFilepath'] != 'galaxySED/%s.gz' % lens['lens_sed'].values[0])):
                if lens_sed_error is False:
                    errors_string = errors_string + "\nSED Filename. First error found in lens_gal_id: %i " % u_id
                    errors_present = True
                    lens_sed_error = True                    

        
        print('------------')
        print('SNE direct catalog input Results:')

        if errors_present is False:
            print('Pass: All instance catalog values within 0.005 of lensed system inputs. ' +
                  'All SED Filenames match.')
        else:
            print('Fail:')
            print(errors_string)

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
        print('AGN Magnitude Test Results:')

        if max_lens_mag_error < 0.01:
            print('Pass: Max lens phosim MagNorm error less than 0.01 mags.')
        else:
            print('Fail: Max lens phosim MagNorm error is greater than 0.01 mags. ' + 
                  'Max error is: %.4f mags.' % max_lens_mag_error)

        print('------------')

        return

    def compare_sne_lens_mags(self, spr_sne_df, spr_sne_lens_df):

        """
        This test compares the things that get swapped in directly from the input catalog.
        """

        df = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
                                      'dc2_sne_cat.csv'))

        lens_mag_error = []

        for lens_gal_row in spr_sne_lens_df.iterrows():
            lens_idx, lens_gal_df = lens_gal_row
            u_id = lens_gal_df['uniqueId']

            spr_sys_df = spr_sne_df.query('lens_galaxy_uID == %i' % u_id)
            lens = df.query('twinkles_sysno == %i' % spr_sys_df['twinkles_system'].iloc[0])
            # SNe systems might not have all images appearing in an instance catalog unlike AGN
            img_vals = spr_sys_df['image_number'].values

            for img_idx in range(len(img_vals)):

                lens_mag_error.append(lens['bulge_magnorm'].iloc[img_vals[img_idx]] -
                                      lens_gal_df['phosimMagNorm'])

        max_lens_mag_error = np.max(np.abs(lens_mag_error))

        print('------------')
        print('SNE Magnitude Test Results:')

        if max_lens_mag_error < 0.01:
            print('Pass: Max lens phosim MagNorm error less than 0.01 mags.')
        else:
            print('Fail: Max lens phosim MagNorm error is greater than 0.01 mags. ' + 
                  'Max error is: %.4f mags.' % max_lens_mag_error)

        print('------------')

        return

    def compare_agn_image_mags(self, spr_agn_df, spr_agn_lens_df, visit_mjd,
                               visit_band):

        """
        This test compares the image magnitudes.
        """
        
        db = om10.DB(catalog=os.path.join(os.environ['TWINKLES_DIR'], 'data', 
                                          'twinkles_lenses_v2.fits'), vb=False)

        lens_mag_error = []

        agnSpecDir = 'agnSED'
        agnDir = str(getPackageDir('sims_sed_library') + '/' + agnSpecDir)
        bandpassDict = BandpassDict.loadTotalBandpassesFromFiles(bandpassNames=[visit_band])
        norm_bp = Bandpass()
        norm_bp.imsimBandpass()

        agn_var_params = self.load_agn_var_params()

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
                print(np.abs(mag)[i], lensed_mags.values[i], d_mags[visit_band])
                
                corrected_mags.append(test_mag_3)

            print(corrected_mags)
            
            
        #     lens_mag_error.append(test_mag - lens_gal_df['phosimMagNorm'])


        # max_lens_mag_error = np.max(np.abs(lens_mag_error))

        # print('------------')
        # print('AGN Magnitude Test Results:')

        # if max_lens_mag_error < 0.01:
        #     print('Pass: Max lens phosim MagNorm error less than 0.01 mags.')
        # else:
        #     print('Fail: Max lens phosim MagNorm error is greater than 0.01 mags. ' + 
        #           'Max error is: %.4f mags.' % max_lens_mag_error)

        # print('------------')

        return

    def get_agn_variability_mags(self, var_param_dict, time_delay, mjd, redshift):

        def return_num_obj(params):
            return 1

        eg_test = egvar()
        eg_test.num_variable_obj = return_num_obj

        print(time_delay)

        var_mags = eg_test.applyAgn([[0]], var_param_dict, 
                                    mjd+time_delay,
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
                line_redshift = line.split(',')[4]
                
                var_param_dict = {x.split(':')[0][2:-1]:np.array([np.float(x.split(':')[1])]) 
                                  for x in line.split('{')[2][:-3].split(',')}

                # Some munging from the way we made the dict
                var_param_dict['seed'] = np.array(var_param_dict['eed'], dtype=int)
                del var_param_dict['eed']

                agn_var_params[str(line_id)] = var_param_dict

        return agn_var_params
