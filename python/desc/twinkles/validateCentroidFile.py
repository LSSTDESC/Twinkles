from __future__ import with_statement

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import numpy as np
import pandas
import os
import warnings

from lsst.sims.utils import ObservationMetaData
from lsst.sims.coordUtils import pixelCoordsFromRaDec
from lsst.obs.lsstSim import LsstSimMapper
from desc.twinkles import icrsFromPhoSim

__all__ = ["getPredictedCentroids", "CentroidValidator"]

def getPredictedCentroids(cat_name):
    """
    Read in an InstanceCatalog.  Use CatSim to calculate the expected
    pixel positions of all of the sources in that InstanceCatalog.
    Return a pandas dataframe containing each source's id, xpix, and ypix
    coordinates.

    Parameters
    ----------
    cat_name is the path to the InstanceCatalog

    Returns
    -------
    a pandas dataframe with columns 'id', 'x', and 'y'
    """

    target_chip = 'R:2,2 S:1,1'

    camera = LsstSimMapper().camera

    with open(cat_name, 'r') as input_catalog:
        input_lines = input_catalog.readlines()

    ra = None
    dec = None
    mjd = None
    rotSkyPos = None
    while ra is None or dec is None or mjd is None or rotSkyPos is None:
        for line in input_lines:
            line = line.split()
            if line[0] == 'rightascension':
                ra = float(line[1])
            if line[0] == 'declination':
                dec = float(line[1])
            if line[0] == 'mjd':
                mjd = float(line[1])
            if line[0] == 'rotskypos':
                rotSkyPos = float(line[1])

    try:
        assert ra is not None
        assert dec is not None
        assert mjd is not None
        assert rotSkyPos is not None
    except:
        print 'ra: ',ra
        print 'dec: ',dec
        print 'mjd: ',mjd
        print 'rotSkyPos: ',rotSkyPos

    obs = ObservationMetaData(pointingRA=ra,
                              pointingDec=dec,
                              mjd=mjd,
                              rotSkyPos=rotSkyPos)

    id_list = []
    ra_list = []
    dec_list = []
    for line in input_lines:
        line = line.split()
        if len(line) > 2:
            id_list.append(int(line[1]))
            ra_list.append(float(line[2]))
            dec_list.append(float(line[3]))

    id_list = np.array(id_list)
    ra_list = np.array(ra_list)
    dec_list = np.array(dec_list)

    ra_icrs, dec_icrs = icrsFromPhoSim(ra_list, dec_list, obs)

    x_pix, y_pix = pixelCoordsFromRaDec(ra_icrs, dec_icrs,
                                        chipName=[target_chip]*len(id_list),
                                        #chipName=chip_name_list,
                                        obs_metadata=obs,
                                        camera=camera)

    return pandas.DataFrame({'id': id_list,
                             'x': y_pix,
                             'y': x_pix})  # need to reverse pixel order because
                                           # DM and PhoSim have different
                                           # conventions


class CentroidValidator(object):

    def __init__(self, cat_name, centroid_name):
        self.cat_name = cat_name
        self.centroid_name = centroid_name
        self.catsim_data = getPredictedCentroids(self.cat_name)

        self._x_center = 2000.0
        self._y_center = 2036.0  # central pixel on chip

        phosim_dtype = np.dtype([('id', long), ('nphot', int),
                                 ('x', float), ('y', float)])

        _phosim_data = np.genfromtxt(self.centroid_name, dtype=phosim_dtype,
                                     skip_header=1)

        self.phosim_data = pandas.DataFrame({'id': _phosim_data['id'],
                                             'nphot': _phosim_data['nphot'],
                                             'x': _phosim_data['x'],
                                             'y':_phosim_data['y']})

        # make sure that any sources whicha appear in the PhoSim centroid file, but
        # not in the CatSim-predicted centroid file have id==0
        self.just_phosim = self.phosim_data[np.logical_not(self.phosim_data.id.isin(self.catsim_data.id.values).values)]

        try:
            assert self.just_phosim.id.max() == 0
        except:
            print 'a source with non-zero ID appears in PhoSim centroid file, but not CatSim centroid file'
            raise

        # find all of the CatSim sources that appeared in PhoSim
        self.catsim_phosim = self.catsim_data.merge(self.phosim_data, left_on='id', right_on='id',
                                                    how='left', suffixes=('_catsim', '_phosim'))

        self.catsim_phosim['dx'] = pandas.Series(self.catsim_phosim['x_catsim']-self.catsim_phosim['x_phosim'],
                                                 index=self.catsim_phosim.index)
        self.catsim_phosim['dy'] = pandas.Series(self.catsim_phosim['y_catsim']-self.catsim_phosim['y_phosim'],
                                                 index=self.catsim_phosim.index)

        # select points that actually showed up on the PhoSim image
        overlap_dexes = np.logical_not(np.logical_or(self.catsim_phosim['x_phosim'].isnull(),
                                                     self.catsim_phosim['y_phosim'].isnull()))

        overlap = self.catsim_phosim[overlap_dexes]

        self.bright_sources = overlap.query('nphot>0')
        self.bright_sources = self.bright_sources.sort_values(by='nphot')

        self.just_catsim = self.catsim_data[np.logical_not(self.catsim_data.id.isin(self.phosim_data.id.values).values)]
        self.min_d_just_catsim = np.sqrt(np.power(self.just_catsim.x-self._x_center,2) +
                                         np.power(self.just_catsim.y-self._y_center,2)).min()
        print 'minimum distance of just_catsim: ',self.min_d_just_catsim

        nphot_sum = self.bright_sources.nphot.sum()
        self.weighted_dx = (self.bright_sources.dx*self.bright_sources.nphot).sum()/nphot_sum
        self.weighted_dy = (self.bright_sources.dy*self.bright_sources.nphot).sum()/nphot_sum
        self.mean_dx = self.bright_sources.dx.mean()
        self.mean_dy = self.bright_sources.dy.mean()
        self.median_dx = self.bright_sources.dx.median()
        self.median_dy = self.bright_sources.dy.median()

        print 'weighted dx/dy: ',self.weighted_dx, self.weighted_dy
        print 'mean dx/dy: ',self.mean_dx, self.mean_dy
        print 'median dx/dy: ',self.median_dx, self.median_dy


    def create_tex_file(self, out_dir, clean=False):
        """
        out_dir is the directory where we should write the figures
        clean is a boolean which controls whether or not to overwrite existing files
        (True means overwrite)
        """

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        self.scatter_fig_name = os.path.join(out_dir, 'dx_dy_scatter.png')
        self.radial_fig_name = os.path.join(out_dir, 'dx_dy_radius.png')
        self.displacement_fig_name = os.path.join(out_dir, 'max_displacement.png')
        self.tex_name = os.path.join(out_dir, self.centroid_name.replace('.txt','_validation.tex'))

        if os.path.exists(self.tex_name) and clean:
            os.unlink(self.tex_name)

        if os.path.exists(self.scatter_fig_name) and clean:
            os.unlink(self.scatter_fig_name)

        if os.path.exists(self.displacement_fig_name) and clean:
            os.unlink(self.displacement_fig_name)

        if os.path.exists(self.radial_fig_name) and clean:
            os.unlink(self.radial_fig_name)

        if os.path.exists(self.scatter_fig_name) or os.path.exists(self.displacement_fig_name) \
        or os.path.exists(self.tex_name) or os.path.exists(self.radial_fig_name):

            scatter_root = self.scatter_fig_name.replace('.png', '')
            displacement_root = self.displacement_fig_name.replace('.png', '')
            tex_root = self.tex_name.replace('.tex', '')
            radial_root = self.radial_fig_name.replace('.png', '')

            ix = 1
            while os.path.exists(self.scatter_fig_name) or os.path.exists(self.displacement_fig_name) \
            or os.path.exists(self.tex_name):

                self.scatter_fig_name = scatter_root+'_%d.png' % ix
                self.displacement_fig_name = displacement_root+'_%d.png' % ix
                self.tex_name = tex_root+'_%d.tex' % ix
                self.radial_fig_name = radial_root+'_%d.png' % ix
                ix += 1

            warnings.warn('Needed to rename figures to %s, %s, %s, %s to avoid overwriting older files' %
                          (self.scatter_fig_name, self.displacement_fig_name,
                           self.radial_fig_name, self.tex_name))

        self._create_figures(out_dir, clean)

        if os.path.exists(self.tex_name):
            raise RuntimeError('%s already exists; not going to overwrite it\n' % tex_name)

        with open(self.tex_name, 'w') as tex_file:
            self.tex_opening_boilerplate(tex_file)
            self.tex_figure(tex_file, self.scatter_fig_name.split('/')[-1],
                            'The displacement between CatSim and PhoSim in pixel coordinates for each source. '
                            'Color bar indicates number of photons in the source.')
            self.tex_figure(tex_file, self.displacement_fig_name.split('/')[-1],
                            'Maximum displacement in pixel coordinates as a function of number of '
                            'photons in the source')
            self.tex_figure(tex_file, self.radial_fig_name.split('/')[-1],
                            'Displacement between PhoSim and CatSim as a function of distance from '
                            'chip center (in PhoSim)')
            self.tex_scalar(tex_file, self.weighted_dx, 'Weighted (by nphoton) mean displacement in x')
            self.tex_scalar(tex_file, self.weighted_dy, 'Weighted (by nphoton) mean displacement in y')
            self.tex_scalar(tex_file, self.mean_dx, 'Mean displacement in x')
            self.tex_scalar(tex_file, self.mean_dy, 'Mean displacement in y')
            self.tex_scalar(tex_file, self.median_dx, 'Median displacement in x')
            self.tex_scalar(tex_file, self.median_dy, 'Median displacement in y')
            self.tex_scalar(tex_file, self.min_d_just_catsim,
                            'Minimum distance (in pixels) from the center of the chip '
                            'of objects that appear in CatSim but not PhoSim')
            self.tex_closing_boilerplate(tex_file)

        print 'created file: %s\ncompile it with pdflatex' % self.tex_name

    def _create_figures(self, out_dir, clean=False):
        """
        out_dir is the directory where we should write the figures
        clean is a boolean which controls whether or not to overwrite existing files
        (True means overwrite)
        """
        if os.path.exists(self.scatter_fig_name):
            raise RuntimeError('%s already exists; not going to overwrite it' % scatter_fig_name)

        _dx = self.bright_sources.dx.max()-self.bright_sources.dx.min()
        _dy = self.bright_sources.dy.max()-self.bright_sources.dy.min()

        plt.figsize=(30,30)
        for i_fig, limit in enumerate([((-20+self.weighted_dx, 20+self.weighted_dx),(-20+self.weighted_dy, 20+self.weighted_dy)),
                                       ((-50+self.weighted_dx, 50+self.weighted_dx),(-50+self.weighted_dy, 50+self.weighted_dy)),
                                       ((-200+self.weighted_dx,200+self.weighted_dx),(-200+self.weighted_dy,200+self.weighted_dy)),
                                       ((self.bright_sources.dx.min()-0.01*_dx, self.bright_sources.dx.max()+0.01*_dx),
                                        (self.bright_sources.dy.min()-0.01*_dy, self.bright_sources.dy.max()+0.01*_dy))]):
            plt.subplot(2,2,i_fig+1)
            plt.scatter(self.bright_sources.dx, self.bright_sources.dy, c=self.bright_sources.nphot,
                        s=10,edgecolor='',cmap=plt.cm.gist_ncar,norm=LogNorm())


            plt.plot([limit[0][0], limit[0][1]], [0.0, 0.0], color='k', linestyle='--')
            plt.plot([0.0, 0.0], [limit[1][0], limit[1][1]], color='k', linestyle='--')

            plt.xlim(limit[0])
            plt.ylim(limit[1])
            xticks = np.arange(limit[0][0],limit[0][1],(limit[0][1]-limit[0][0])/5)
            xtick_labels = ['%.2e' % vv if ix%2==0 else '' for ix, vv in enumerate(xticks)]

            yticks = np.arange(limit[1][0],limit[1][1],(limit[1][1]-limit[1][0])/5)
            ytick_labels = ['%.2e' % vv if ix%2==0 else '' for ix, vv in enumerate(yticks)]

            plt.xticks(xticks, xtick_labels, fontsize=10)
            plt.yticks(yticks, ytick_labels, fontsize=10)
            plt.minorticks_on()
            plt.tick_params(axis='both', length=10)

            if i_fig==0:
                cb = plt.colorbar()
                cb.set_label('photons in source')
                plt.xlabel('dx (pixels)')
                plt.ylabel('dy (pixels)')

        plt.tight_layout()
        plt.savefig(self.scatter_fig_name)
        plt.close()

        if os.path.exists(self.radial_fig_name):
            raise RuntimeError("%s exists; not willing to overwrite it" % self.radial_fig_name)

        d_rr = np.sqrt(np.power(self.bright_sources.dx, 2) + np.power(self.bright_sources.dy, 2))
        center_dist = np.sqrt(np.power(self.bright_sources.x_phosim-self._x_center,2) +
                              np.power(self.bright_sources.y_phosim-self._y_center,2))

        plt.figsize = (30, 30)
        fig = plt.figure()
        ax = plt.gca()
        ax.scatter(center_dist, d_rr)
        plt.xlabel('distance from center in PhoSim (pixels)')
        plt.ylabel('displacement between PhoSim and CatSim (pixels)')
        ax.set_yscale('log')
        ax.set_xscale('log')
        plt.savefig(self.radial_fig_name)

        nphot_unique = np.unique(self.bright_sources.nphot)
        sorted_dex = np.argsort(-1.0*nphot_unique)
        nphot_unique = nphot_unique[sorted_dex]

        dx_of_nphot = np.array([np.abs(self.bright_sources.query('nphot>=%e' % nn).dx).max() for nn in nphot_unique[1:]])
        dy_of_nphot = np.array([np.abs(self.bright_sources.query('nphot>=%e' % nn).dy).max() for nn in nphot_unique[1:]])

        if os.path.exists(self.displacement_fig_name):
            raise RuntimeError('%s already exists; will not overwrite it' % self.displacement_fig_name)

        plt.figsize = (30, 30)
        plt.subplot(2,2,1)
        plt.semilogx(nphot_unique[1:], dx_of_nphot, label='dx')
        plt.semilogx(nphot_unique[1:], dy_of_nphot, label='dy')
        plt.xlabel('minimum number of photons')
        plt.ylabel('max pixel displacement')
        plt.subplot(2,2,2)
        plt.semilogx(nphot_unique[1:], dx_of_nphot, label='dx')
        plt.semilogx(nphot_unique[1:], dy_of_nphot, label='dy')
        plt.ylim((0,200))
        plt.subplot(2,2,3)
        plt.semilogx(nphot_unique[1:], dx_of_nphot, label='dx')
        plt.semilogx(nphot_unique[1:], dy_of_nphot, label='dy')
        plt.ylim((0,100))
        plt.subplot(2,2,4)
        plt.semilogx(nphot_unique[1:], dx_of_nphot, label='dx')
        plt.semilogx(nphot_unique[1:], dy_of_nphot, label='dy')
        plt.ylim((0,50))
        plt.legend(loc=0)
        plt.tight_layout()
        plt.savefig(self.displacement_fig_name)


    def tex_opening_boilerplate(self, file_handle):
        file_handle.write('\documentclass[preprint]{aastex}\n')
        file_handle.write('\\topmargin 0.0cm\n\\textheight 8.5in\n')
        file_handle.write('\\begin{document}\n\n')


    def tex_closing_boilerplate(self, file_handle):
        file_handle.write('\n\end{document}\n')


    def tex_figure(self, file_handle, fig_name, caption):
        file_handle.write('\n\\begin{figure}\n')
        file_handle.write('\includegraphics[scale=0.9]{%s}\n' % fig_name)
        file_handle.write('\caption{\n')
        file_handle.write('%s\n' % caption)
        file_handle.write('}\n')
        file_handle.write('\end{figure}\n\n')

    def tex_scalar(self, file_handle, value, caption):
        file_handle.write('\n\n%s: $%.12e$\n\n' % (caption, value))
