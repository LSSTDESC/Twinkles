import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import numpy as np
import pandas

import sys
import time

from desc.twinkles import getPredictedCentroids

t_start = time.time()
catalog_name = sys.argv[2]
centroid_name = sys.argv[1]

catsim_data = getPredictedCentroids(catalog_name)

print 'got catsim dataframe after ',time.time()-t_start

phosim_dtype = np.dtype([('id', long), ('nphot', int),
                         ('x', float), ('y', float)])

print 'loading centroid ',centroid_name
_phosim_data = np.genfromtxt(centroid_name, dtype=phosim_dtype, skip_header=1)

phosim_data = pandas.DataFrame({'id': _phosim_data['id'],
                                'nphot': _phosim_data['nphot'],
                                'x': _phosim_data['x'],
                                'y':_phosim_data['y']})

# make sure that any sources whicha appear in the PhoSim centroid file, but
# not in the CatSim-predicted centroid file have id==0
just_phosim = phosim_data[np.logical_not(phosim_data.id.isin(catsim_data.id.values).values)]

print 'got all dataframes after ',time.time()-t_start

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

plt.figsize=(30,30)
for i_fig, limit in enumerate(((-50, 50), (-200,200), (-4000, 4000))):
    plt.subplot(2,2,i_fig+1)
    plt.scatter(bright_sources.dx,bright_sources.dy,c=bright_sources.nphot,
                s=10,edgecolor='',cmap=plt.cm.gist_ncar,norm=LogNorm())

    ticks = np.arange(limit[0],limit[1],(limit[1]-limit[0])/5)
    tick_labels = ['%.2e' % vv if ix%2==0 else '' for ix, vv in enumerate(ticks)]

    plt.xlim(limit)
    plt.ylim(limit)
    plt.xticks(ticks, tick_labels, fontsize=10)
    plt.yticks(ticks, tick_labels, fontsize=10)
    plt.minorticks_on()
    plt.tick_params(axis='both', length=10)

    if i_fig==0:
        cb = plt.colorbar()
        cb.set_label('counts in source')
        plt.xlabel('dx (pixels)')
        plt.ylabel('dy (pixels)')

plt.tight_layout()
plt.savefig('dx_dy_scatter.png')
plt.close()

print 'first figure after ',time.time()-t_start

nphot_sum = bright_sources.nphot.sum()
weighted_dx = (bright_sources.dx*bright_sources.nphot).sum()/nphot_sum
weighted_dy = (bright_sources.dy*bright_sources.nphot).sum()/nphot_sum

print 'weighted dx/dy: ',weighted_dx, weighted_dy
print 'mean dx/dy: ',bright_sources.dx.mean(),bright_sources.dy.mean()
print 'median dx/dy: ',bright_sources.dx.median(),bright_sources.dy.median()

nphot_unique = np.unique(bright_sources.nphot)
sorted_dex = np.argsort(-1.0*nphot_unique)
nphot_unique = nphot_unique[sorted_dex]

dx_of_nphot = np.array([np.abs(bright_sources.query('nphot>=%e' % nn).dx).max() for nn in nphot_unique[1:]])
dy_of_nphot = np.array([np.abs(bright_sources.query('nphot>=%e' % nn).dy).max() for nn in nphot_unique[1:]])

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
plt.savefig('max_displacement.png')

print 'that took ',time.time()-t_start
