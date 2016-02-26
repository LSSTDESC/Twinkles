"""
Create postage stamps from Exposure FITS files written by the LSST Stack.
"""
import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage


class PostageStampMaker(object):
    "Class to create postage stamps for Exposure FITS files"
    def __init__(self, expfile):
        self.exposure = afwImage.ExposureF(expfile)

    def getScienceArray(self):
        "Return the science image as a ndarray"
        return self.exposure.getMaskedImage().getImage().getArray()

    def getBBox(self, ra, dec, arcsec):
        """
        Compute the bounding box with sides of size arcsec, centered at
        ra, dec
        """
        ra_angle = afwGeom.Angle(ra, afwGeom.degrees)
        dec_angle = afwGeom.Angle(dec, afwGeom.degrees)
        wcs = self.exposure.getWcs()
        center_pix = wcs.skyToPixel(ra_angle, dec_angle)
        pixel_scale = wcs.pixelScale().asArcseconds()
        npix = int(arcsec/pixel_scale)
        llc = afwGeom.Point2I(int(center_pix.getX() - npix/2.),
                              int(center_pix.getY() - npix/2.))
        bbox = afwGeom.Box2I(llc, afwGeom.Extent2I(npix, npix))
        return bbox

    def Factory(self, ra, dec, arcsec):
        """
        Factory method to return the cropped Exposure object with the
        desired geometry.
        """
        bbox = self.getBBox(ra, dec, arcsec)
        return self.exposure.Factory(self.exposure, bbox)

if __name__ == '__main__':
    import lsst.afw.display.ds9 as ds9

    my_expfile = '/home/jchiang/work/LSST/DESC/Twinkles/tests/v840-fr.fits'
    my_ra, my_dec, my_arcsec = 53.010895, -27.437648, 10
    outfile = 'postage_stamp.fits'

    stamp_maker = PostageStampMaker(my_expfile)
    postage_stamp = stamp_maker.Factory(my_ra, my_dec, my_arcsec)

    postage_stamp.writeFits(outfile)

    ds9.mtv(postage_stamp.getMaskedImage().getImage())
