"""
Create postage stamps from Exposure FITS files written by the LSST Stack.
"""
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

    def makeBBox(self, ra, dec, arcsec):
        """
        Compute the bounding box with sides of size arcsec, centered at
        ra, dec, both in degrees.
        """
        wcs = self.exposure.getWcs()
        center_pix = self.pixel(wcs, ra, dec)
        pixel_scale = wcs.pixelScale().asArcseconds()
        npix = int(arcsec/pixel_scale)
        llc = afwGeom.Point2I(int(center_pix.getX() - npix/2.),
                              int(center_pix.getY() - npix/2.))
        bbox = afwGeom.Box2I(llc, afwGeom.Extent2I(npix, npix))
        return bbox

    def create(self, ra, dec, arcsec):
        """
        Factory method to return the cropped Exposure object with the
        desired geometry.
        """
        bbox = self.makeBBox(ra, dec, arcsec)
        return self.exposure.Factory(self.exposure, bbox)

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
