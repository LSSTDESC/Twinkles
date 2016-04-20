"""
Create postage stamps from Exposure FITS files written by the LSST Stack.
"""
from __future__ import absolute_import, division
import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage


class PostageStampMaker(object):
    "Class to create postage stamps for Exposure FITS files."
    def __init__(self, expfile):
        self.exposure = afwImage.ExposureF(expfile)

    @staticmethod
    def pixel(wcs, ra, dec):
        """
        Use the Wcs object, wcs, to return the Pixel object corresponding
        to ra, dec, both in degrees.
        """
        ra_angle = afwGeom.Angle(ra, afwGeom.degrees)
        dec_angle = afwGeom.Angle(dec, afwGeom.degrees)
        return wcs.skyToPixel(ra_angle, dec_angle)

    @staticmethod
    def center_coord(exposure):
        """
        Return the Coord object of the center of the image.
        """
        bbox = exposure.getBBox()
        x_center = bbox.getMinX() + float(bbox.getWidth())/2.
        y_center = bbox.getMinY() + float(bbox.getHeight())/2.
        coord = exposure.getWcs().pixelToSky(x_center, y_center)
        return coord

    def makeBBox(self, ra, dec, arcsec):
        """
        Compute the bounding box with sides of size arcsec, centered at
        ra, dec, both in degrees.
        """
        wcs = self.exposure.getWcs()
        center_pix = self.pixel(wcs, ra, dec)
        pixel_scale = wcs.pixelScale().asArcseconds()
        npix = int(float(arcsec)/pixel_scale)
        llc = afwGeom.Point2I(int(center_pix.getX() - float(npix)/2. + 0.5),
                              int(center_pix.getY() - float(npix)/2. + 0.5))
        bbox = afwGeom.Box2I(llc, afwGeom.Extent2I(npix, npix))
        return bbox

    def create(self, ra, dec, arcsec):
        """
        Factory method to return the cropped Exposure object with the
        desired geometry.
        """
        bbox = self.makeBBox(ra, dec, arcsec)
        return self.exposure.Factory(self.exposure, bbox)

    def create_stamps(self, stamp_specs):
        """
        Return a tuple of postage stamps derived from self.exposure given
        a sequence of (ra, dec, arcsec) tuples.
        """
        return tuple(self.create(*x) for x in stamp_specs)

def create_postage_stamps(ra, dec, size, fits_files):
    """
    Create a list of postage stamps for a specified region from a sequence
    of Exposure FITS files.
    """
    stamps = []
    for fits_file in fits_files:
        my_stamp_maker = PostageStampMaker(fits_file)
        stamps.append(my_stamp_maker.create(ra, dec, size))
    return stamps

if __name__ == '__main__':
    import os
    import lsst.afw.display.ds9 as ds9

    my_expfile = os.path.join(os.path.split(os.environ['TWINKLES_DIR'])[0],
                              'tests', 'small_CoaddTempExp.fits.gz')

    my_ra, my_dec, my_arcsec = 53.010895, -27.437648, 10
    outfile = 'postage_stamp.fits'

    stamp_maker = PostageStampMaker(my_expfile)
    postage_stamp = stamp_maker.create(my_ra, my_dec, my_arcsec)

    postage_stamp.writeFits(outfile)

    ds9.mtv(postage_stamp.getMaskedImage().getImage())
