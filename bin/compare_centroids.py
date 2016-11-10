import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import numpy as np
import pandas

import sys


catsim_name = sys.argv[2]
phosim_name = sys.argv[1]

print catsim_name,phosim_name

catsim_dtype = np.dtype([('id', long), ('x', float), ('y', float)])
phosim_dtype = np.dtype([('id', long), ('nphot', int),
                         ('x', float), ('y', float)])

_catsim_data = np.genfromtxt(catsim_name, dtype=catsim_dtype)
_phosim_data = np.genfromtxt(phosim_name, dtype=phosim_dtype, skip_header=1)

catsim_data = pandas.DataFrame({'id': _catsim_data['id'],
                                'x': _catsim_data['x'],
                                'y': _catsim_data['y']})

phosim_data = pandas.DataFrame({'id': _phosim_data['id'],
                                'nphot': _phosim_data['nphot'],
                                'x': _phosim_data['x'],
                                'y':_phosim_data['y']})

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

nphot_sum = bright_sources.nphot.sum()
weighted_dx = (bright_sources.dx*bright_sources.nphot).sum()/nphot_sum
weighted_dy = (bright_sources.dy*bright_sources.nphot).sum()/nphot_sum

print 'weighted dx/dy: ',weighted_dx, weighted_dy
print 'mean dx/dy: ',bright_sources.dx.mean(),bright_sources.dy.mean()
print 'median dx/dy: ',bright_sources.dx.median(),bright_sources.dy.median()

