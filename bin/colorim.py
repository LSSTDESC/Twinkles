from __future__ import absolute_import
from matplotlib import pylab as plt

import lsst.daf.persistence as dp
import lsst.afw.display as display
import lsst.afw.display.rgb as rgb

# get a butler
butler = dp.Butler('output_data')
dataId = {'tract':0, 'patch':'0,0'}

bandpass_color_map = {'green':'r', 'red':'i', 'blue':'g'}

# get ref catalog
refs = {}
exposures = {}
for bandpass in bandpass_color_map.values():
    dataId['filter'] = bandpass
    refs[bandpass] = butler.get('deepCoadd_ref', dataId=dataId)
    exposures[bandpass] = butler.get('deepCoadd', dataId=dataId)

rgb_im = rgb.makeRGB(*(exposures[bandpass_color_map[color]].getMaskedImage().getImage()
                       for color in ('red', 'green', 'blue')))

item = exposures.popitem()
dims = item[1].getDimensions()
exposures.update((item,))

fig = plt.figure(figsize=(10,10))
plt.imshow(rgb_im, interpolation='nearest')
# Uncomment the following line to plot the detections
#plt.scatter(refs['g'].getX(), dims[1]-refs['g'].getY(), edgecolors='none', alpha=0.3)
plt.xlim(0, dims[0])
plt.ylim(dims[1], 0)
plt.show()
