"""
Display and plotting tools module.
"""
from __future__ import absolute_import
import astropy.io.fits as fits
import astropy.visualization as viz
from astropy.visualization.mpl_normalize import ImageNormalize
import astropy.wcs
import matplotlib.pyplot as plt

def image_norm(image_data, stretch=viz.AsinhStretch):
    """
    Create the ImageNormalize object based on the desired stretch and
    pixel value range.

    See http://docs.astropy.org/en/stable/visualization/normalization.html
    """
    interval = viz.MinMaxInterval()
    vmin, vmax = interval.get_limits(image_data.flatten())
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=stretch())
    return norm

def render_fits_image(hdu, cmap=plt.cm.gray, stretch=viz.AsinhStretch,
                      xlabel='RA', ylabel='Dec', title=None,
                      subplot=111, fig=None, norm=None):
    """
    Use matplotlib and astropy to render a FITS image HDU.
    Return the figure, axes, and image normalize objects.
    """
    if norm is None:
        norm = image_norm(hdu.data, stretch)

    # Set up the figure axes to use the WCS from the FITS header.
    wcs = astropy.wcs.WCS(hdu.header)
    if fig is None:
        fig = plt.figure()
    axes = fig.add_subplot(subplot, projection=wcs)

    im = plt.imshow(hdu.data, norm=norm, cmap=cmap, origin='lower',
                    interpolation='none')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title is not None:
        axes.set_title(title)
    return fig, axes, norm
