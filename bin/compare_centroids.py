from __future__ import with_statement

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import numpy as np
import pandas

import os

from desc.twinkles import getPredictedCentroids

import argparse
import warnings

def tex_opening_boilerplate(file_handle):
    file_handle.write('\documentclass[preprint]{aastex}\n')
    file_handle.write('\\topmargin 0.0cm\n\\textheight 8.5in\n')
    file_handle.write('\\begin{document}\n\n')


def tex_closing_boilerplate(file_handle):
    file_handle.write('\n\end{document}\n')


def tex_figure(file_handle, fig_name, caption):
    file_handle.write('\n\\begin{figure}\n')
    file_handle.write('\includegraphics[scale=0.9]{%s}\n' % fig_name)
    file_handle.write('\caption{\n')
    file_handle.write('%s\n' % caption)
    file_handle.write('}\n')
    file_handle.write('\end{figure}\n\n')

def tex_scalar(file_handle, value, caption):
    file_handle.write('\n\n%s: $%.12e$\n\n' % (caption, value))

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Read in an InstanceCatalog and a centroid file. "
                                     "Use CatSim to calculate the pixel positions of "
                                     "objects in the InstanceCatalog.  Compare this "
                                     "to the pixel positions as reported in the "
                                     "centroid file.\n\nexample:\n\n"
                                     "python compare_centroids.py --cat myInstanceCatalog.txt "
                                     "--cent myCentroidFile.txt --out_dir my/output/director/")

    parser.add_argument("--cat", type=str, help="path to the InstanceCatalog", default=None)
    parser.add_argument("--cent", type=str, help="path to the centroid file", default=None)
    parser.add_argument("--clean", type=bool, help="delete old files, if names conflict",
                        default=False)
    parser.add_argument("--out_dir", type=str, help="directory where we will put output files",
                        default=".")

    _x_center = 2000.0
    _y_center = 2036.0  # central pixel on chip

    args = parser.parse_args()

    if args.cat is None or args.cent is None:
        raise RuntimeError("Must specify an InstanceCatalog and a centroid file.\n"
                           "You specified %s and %s" % (args.cat, args.cent))

    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)

    catsim_data = getPredictedCentroids(args.cat)

    phosim_dtype = np.dtype([('id', long), ('nphot', int),
                             ('x', float), ('y', float)])

    _phosim_data = np.genfromtxt(args.cent, dtype=phosim_dtype, skip_header=1)

    phosim_data = pandas.DataFrame({'id': _phosim_data['id'],
                                    'nphot': _phosim_data['nphot'],
                                    'x': _phosim_data['x'],
                                    'y':_phosim_data['y']})

    # make sure that any sources whicha appear in the PhoSim centroid file, but
    # not in the CatSim-predicted centroid file have id==0
    just_phosim = phosim_data[np.logical_not(phosim_data.id.isin(catsim_data.id.values).values)]

    try:
        assert just_phosim.id.max() == 0
    except:
        print 'a source with non-zero ID appears in PhoSim centroid file, but not CatSim centroid file'
        raise

    # find all of the CatSim sources that appeared in PhoSim
    catsim_phosim = catsim_data.merge(phosim_data, left_on='id', right_on='id',
                                      how='left', suffixes=('_catsim', '_phosim'))

    catsim_phosim['dx'] = pandas.Series(catsim_phosim['x_catsim']-catsim_phosim['x_phosim'], index=catsim_phosim.index)
    catsim_phosim['dy'] = pandas.Series(catsim_phosim['y_catsim']-catsim_phosim['y_phosim'], index=catsim_phosim.index)

    # select points that actually showed up on the PhoSim image
    overlap = np.logical_not(np.logical_or(catsim_phosim['x_phosim'].isnull(), catsim_phosim['y_phosim'].isnull()))

    overlap = catsim_phosim[overlap]

    bright_sources = overlap.query('nphot>0')
    bright_sources = bright_sources.sort_values(by='nphot')

    scatter_fig_name = os.path.join(args.out_dir, 'dx_dy_scatter.png')
    radial_fig_name = os.path.join(args.out_dir, 'dx_dy_radius.png')
    displacement_fig_name = os.path.join(args.out_dir, 'max_displacement.png')
    tex_name = os.path.join(args.out_dir, args.cent.replace('.txt','_validation.tex'))

    if os.path.exists(tex_name) and args.clean:
        os.unlink(tex_name)

    if os.path.exists(scatter_fig_name) and args.clean:
        os.unlink(scatter_fig_name)

    if os.path.exists(displacement_fig_name) and args.clean:
        os.unlink(displacement_fig_name)

    if os.path.exists(radial_fig_name) and args.clean:
        os.unlink(radial_fig_name)

    if os.path.exists(scatter_fig_name) or os.path.exists(displacement_fig_name) \
    or os.path.exists(tex_name) or os.path.exists(radial_fig_name):

        scatter_root = scatter_fig_name.replace('.png', '')
        displacement_root = displacement_fig_name.replace('.png', '')
        tex_root = tex_name.replace('.tex', '')
        radial_root = radial_fig_name.replace('.png', '')

        ix = 1
        while os.path.exists(scatter_fig_name) or os.path.exists(displacement_fig_name) \
        or os.path.exists(tex_name):

            scatter_fig_name = scatter_root+'_%d.png' % ix
            displacement_fig_name = displacement_root+'_%d.png' % ix
            tex_name = tex_root+'_%d.tex' % ix
            radial_fig_name = radial_root+'_%d.tex' % ix
            ix += 1

        warnings.warn('Needed to rename figures to %s, %s, %s, %s to avoid overwriting older files' %
                      (scatter_fig_name, displacement_fig_name, radial_fig_name, tex_name))

    just_catsim = catsim_data[np.logical_not(catsim_data.id.isin(phosim_data.id.values).values)]
    min_d_just_catsim = np.sqrt(np.power(just_catsim.x-_x_center,2) + np.power(just_catsim.y-_y_center,2)).min()
    print 'minimum distance of just_catsim: ',min_d_just_catsim

    nphot_sum = bright_sources.nphot.sum()
    weighted_dx = (bright_sources.dx*bright_sources.nphot).sum()/nphot_sum
    weighted_dy = (bright_sources.dy*bright_sources.nphot).sum()/nphot_sum
    mean_dx = bright_sources.dx.mean()
    mean_dy = bright_sources.dy.mean()
    median_dx = bright_sources.dx.median()
    median_dy = bright_sources.dy.median()

    print 'weighted dx/dy: ',weighted_dx, weighted_dy
    print 'mean dx/dy: ',mean_dx, mean_dy
    print 'median dx/dy: ',median_dx, median_dy

    if os.path.exists(scatter_fig_name):
        raise RuntimeError('%s already exists; not going to overwrite it' % scatter_fig_name)

    _dx = bright_sources.dx.max()-bright_sources.dx.min()
    _dy = bright_sources.dy.max()-bright_sources.dy.min()

    plt.figsize=(30,30)
    for i_fig, limit in enumerate([((-20+weighted_dx, 20+weighted_dx),(-20+weighted_dy, 20+weighted_dy)),
                                   ((-50+weighted_dx, 50+weighted_dx),(-50+weighted_dy, 50+weighted_dy)),
                                   ((-200+weighted_dx,200+weighted_dx),(-200+weighted_dy,200+weighted_dy)),
                                   ((bright_sources.dx.min()-0.01*_dx, bright_sources.dx.max()+0.01*_dx),
                                    (bright_sources.dy.min()-0.01*_dy, bright_sources.dy.max()+0.01*_dy))]):
        plt.subplot(2,2,i_fig+1)
        plt.scatter(bright_sources.dx,bright_sources.dy,c=bright_sources.nphot,
                    s=10,edgecolor='',cmap=plt.cm.gist_ncar,norm=LogNorm())


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
    plt.savefig(scatter_fig_name)
    plt.close()

    if os.path.exists(radial_fig_name):
        raise RuntimeError("%s exists; not willing to overwrite it" % radial_fig_name)

    d_rr = np.sqrt(np.power(bright_sources.dx, 2) + np.power(bright_sources.dy, 2))
    center_dist = np.sqrt(np.power(bright_sources.x_phosim-_x_center,2) +
                          np.power(bright_sources.y_phosim-_y_center,2))

    plt.figsize = (30, 30)
    fig = plt.figure()
    ax = plt.gca()
    ax.scatter(center_dist, d_rr)
    plt.xlabel('distance from center in PhoSim (pixels)')
    plt.ylabel('displacement between PhoSim and CatSim (pixels)')
    ax.set_yscale('log')
    ax.set_xscale('log')
    plt.savefig(radial_fig_name)

    nphot_unique = np.unique(bright_sources.nphot)
    sorted_dex = np.argsort(-1.0*nphot_unique)
    nphot_unique = nphot_unique[sorted_dex]

    dx_of_nphot = np.array([np.abs(bright_sources.query('nphot>=%e' % nn).dx).max() for nn in nphot_unique[1:]])
    dy_of_nphot = np.array([np.abs(bright_sources.query('nphot>=%e' % nn).dy).max() for nn in nphot_unique[1:]])

    if os.path.exists(displacement_fig_name):
        raise RuntimeError('%s already exists; will not overwrite it' % displacement_fig_name)

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
    plt.savefig(displacement_fig_name)

    if os.path.exists(tex_name):
        raise RuntimeError('%s already exists; not going to overwrite it\n' % tex_name)

    with open(tex_name, 'w') as tex_file:
        tex_opening_boilerplate(tex_file)
        tex_figure(tex_file, scatter_fig_name.split('/')[-1],
                   'The displacement between CatSim and PhoSim in pixel coordinates for each source. '
                   'Color bar indicates number of photons in the source.')
        tex_figure(tex_file, displacement_fig_name.split('/')[-1],
                   'Maximum displacement in pixel coordinates as a function of number of '
                   'photons in the source')
        tex_figure(tex_file, radial_fig_name.split('/')[-1],
                   'Displacement between PhoSim and CatSim as a function of distance from '
                   'chip center (in PhoSim)')
        tex_scalar(tex_file, weighted_dx, 'Weighted (by nphoton) mean displacement in x')
        tex_scalar(tex_file, weighted_dy, 'Weighted (by nphoton) mean displacement in y')
        tex_scalar(tex_file, mean_dx, 'Mean displacement in x')
        tex_scalar(tex_file, mean_dy, 'Mean displacement in y')
        tex_scalar(tex_file, median_dx, 'Median displacement in x')
        tex_scalar(tex_file, median_dy, 'Median displacement in y')
        tex_scalar(tex_file, min_d_just_catsim,
                   'Minimum distance (in pixels) from the center of the chip '
                   'of objects that appear in CatSim but not PhoSim')
        tex_closing_boilerplate(tex_file)

    print 'created file: %s\ncompile it with pdflatex' % tex_name
