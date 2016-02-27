"""
Test code for PostageStampMaker module.
"""
import os
import unittest
from PostageStampMaker import PostageStampMaker


class PostageStampTestCase(unittest.TestCase):
    "TestCase class for PostageStampMaker module."
    def setUp(self):
        """
        Set up each test with a new PostageStampMaker object using the
        test FITS file, coordinates of the image center, and a postage
        stamp size of 10 arcsec.
        """
        expfile = os.path.join(os.environ['TWINKLES_DIR'], '..',
                               'tests', 'small_CoaddTempExp.fits.gz')
        self.stamp_maker = PostageStampMaker(expfile)
        self.ra = 53.010895
        self.dec = -27.437648
        self.size = 10

    def test_bbox_generation(self):
        "Test the make bounding box function."
        bbox = self.stamp_maker.makeBBox(self.ra, self.dec, self.size)
        self.assertEqual((bbox.getWidth(), bbox.getHeight()), (30, 30))

    def test_create(self):
        "Test that the postage stamp has the expected size."
        my_exposure = self.stamp_maker.create(self.ra, self.dec, self.size)
        my_imarr = my_exposure.getMaskedImage().getImage().getArray()
        self.assertEqual(my_imarr.shape, (30, 30))

    def test_create_2(self):
        """
        Test that the center pixel of both the postage stamp and original
        image have the same value.
        """
        my_exposure = self.stamp_maker.create(self.ra, self.dec, self.size)
        my_imarr = my_exposure.getMaskedImage().getImage().getArray()
        ref_exposure = self.stamp_maker.exposure
        ref_imarr = ref_exposure.getMaskedImage().getImage().getArray()
        self.assertEqual(my_imarr[my_imarr.shape[0]/2][my_imarr.shape[1]/2],
                         ref_imarr[ref_imarr.shape[0]/2][ref_imarr.shape[1]/2])
