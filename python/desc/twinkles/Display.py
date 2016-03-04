"""
Display and plotting tools module.
"""
import astropy.io.fits as fits
import astropy.visualization as viz
import astropy.wcs
import matplotlib.pyplot as plt

def render_fits_image(hdu, scale='asinh', cmap=plt.cm.gray,
                      xlabel='RA', ylabel='Dec', title=None):
    "Use matplotlib and astropy to render a FITS image HDU"
    wcs = astropy.wcs.WCS(hdu.header)
    fig = plt.figure()
    axes = fig.add_subplot(111, projection=wcs)
    plt.imshow(viz.scale_image(hdu.data, scale=scale),
               cmap=cmap, origin='lower', interpolation='none')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title is not None:
        axes.set_title(title)
    return fig
