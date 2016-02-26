import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage


class PostageStampMaker(object):
    def __init__(self, expfile):
        self.exposure = afwImage.ExposureF(expfile)
    def getScienceArray(self):
        return self.exposure.getMaskedImage().getImage().getArray()
    def getBBox(self, ra, dec, arcsec):
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
        bbox = self.getBBox(ra, dec, arcsec)
        return self.exposure.Factory(self.exposure, bbox)

if __name__ == '__main__':
    import lsst.afw.display.ds9 as ds9
    expfile = '/home/jchiang/work/LSST/DESC/Twinkles/tests/v840-fr.fits'
    ra, dec, arcsec = 53.010895, -27.437648, 10
    outfile = 'postage_stamp.fits'

    stamp_maker = PostageStampMaker(expfile)
    postage_stamp = stamp_maker.Factory(ra, dec, arcsec)

    postage_stamp.writeFits(outfile)

#    ds9.mtv(postage_stamp.getMaskedImage().getImage())
