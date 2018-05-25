import os
import om10
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gzip
import shutil

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

        sprinkled_agn = df_agn.iloc[np.array(keep_idx)]
        sprinkled_agn = sprinkled_agn.reset_index(drop=True)
        sprinkled_agn['galaxy_id'] = galtileids
        sprinkled_agn['twinkles_system'] = twinkles_system
        sprinkled_agn['image_number'] = twinkles_im_num
        sprinkled_agn['lens_galaxy_uID'] = np.left_shift(np.array(galtileids, dtype=np.int), 10) + 97
            
        return sprinkled_agn

    def process_agn_lenses(self, sprinkled_agn_df, df_galaxy):

        lens_gal_locs = []
        for idx in sprinkled_agn_df['lens_galaxy_uID'].values:
            matches = np.where(df_galaxy['uniqueId'] == idx)[0]
            for match in matches:
                lens_gal_locs.append(match)

        lens_gals = df_galaxy.iloc[np.unique(lens_gal_locs)]
        lens_gals = lens_gals.reset_index(drop=True)

        return lens_gals

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
        lens = db.get_lens(use_lens)

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

        # print(np.histogram(x_offsets))
        # print(np.histogram(y_offsets))
        max_x_err = np.max(np.abs(x_offsets))
        max_y_err = np.max(np.abs(y_offsets))

        if (max_x_err < 0.01) and (max_y_err < 0.01):
            print('Pass: Max image offset error less than 0.01 arcsec')
        else:
            print('Fail: Max image offset error greater than 0.01 arcsec.' + 
                  'Max x error is: %.4f arcsec. Max y error is: %.4f arcsec.' % (max_x_err, max_y_err))

        return
