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


# find all of the CatSim sources that appeared in PhoSim
catsim_phosim = catsim_data.merge(phosim_data, left_on='id', right_on='id',
                                  how='left', suffixes=('_catsim', '_phosim'))

catsim_phosim['dx'] = pandas.Series(catsim_phosim['x_catsim']-catsim_phosim['x_phosim'], index=catsim_phosim.index)
catsim_phosim['dy'] = pandas.Series(catsim_phosim['y_catsim']-catsim_phosim['y_phosim'], index=catsim_phosim.index)

# select points that actually showed up on the PhoSim image
overlap = np.logical_not(np.logical_or(catsim_phosim['x_phosim'].isnull(), catsim_phosim['y_phosim'].isnull()))

dx = catsim_phosim[overlap].as_matrix(columns=['dx']).flatten()
dy = catsim_phosim[overlap].as_matrix(columns=['dy']).flatten()
nphot = catsim_phosim[overlap].as_matrix(columns=['nphot']).flatten()

# limit to sources with more than 0 photons
bright_dex = np.where(nphot>0)
dx=dx[bright_dex]
dy=dy[bright_dex]
nphot=nphot[bright_dex]

# plot the displacement in x and y
sorted_dex = np.argsort(nphot)
plt.figsize=(30,30)
for i_fig, limit in enumerate(((-50, 50), (-200,200), (-4000, 4000))):
    plt.subplot(2,2,i_fig+1)
    plt.scatter(dx[sorted_dex],dy[sorted_dex],c=nphot[sorted_dex],
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

exit(1)


print 'dx sum: ',catsim_phosim['dx'].mean()
print 'dy sum: ',catsim_phosim['dy'].mean()
print 'dx max: ',np.abs(catsim_phosim['dx']).max()
print 'dy max: ',np.abs(catsim_phosim['dy']).max()
dex = np.argmax(np.abs(catsim_phosim['dx']))
print 'bad id ',catsim_phosim['id'][dex]
exit(1)

bad_rows = catsim_phosim[np.logical_or(catsim_phosim['x_phosim'].isnull(), catsim_phosim['y_phosim'].isnull())]
print 'max photons in a null (x,y) source: ',bad_rows['nphot'].max()

not_joined = phosim_data[np.logical_not(phosim_data.id.isin(catsim_phosim.id))]
print not_joined
