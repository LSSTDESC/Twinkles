from __future__ import absolute_import, division
import os
import unittest
from lsst.utils import getPackageDir
from desc.twinkles.io import read_catsimInstCat

class test_readInstCatalogs(unittest.TestCase):
    """
    tests for reading InstanceCatalogs
    """
    @classmethod
    def setUp(cls):
        twinklesDir = getPackageDir('twinkles')
        fileName = 'CatSimGalszless1p2_test.csv'
        cls.instcat = os.path.join(twinklesDir, 'data', fileName)
        cls.df = read_catsimInstCat(cls.instcat)
        cls.colnames = cls.df.columns

    @classmethod
    def tearDownClass(cls):
        pass

    def test_dataframeExists(self):
        """
        Check that dataframe has rows and columns
        """
        self.assertGreater(len(self.colnames), 1)
        self.assertGreater(len(self.df), 1)

    def test_NoHash(self):
        """
        The first column should not start with a hash
        """
        self.assertFalse(self.colnames[0][0] == '#')

    def test_noSpace(self):
        """
        The column names should not have empty spaces at the
        beginning or end
        """
        for col in self.colnames:
            self.assertTrue(col.strip() == col)

    def test_noCommas(self):
        """
        The column names should not start with commas
        """
        for col in self.colnames:
            self.assertFalse(col[0] == ',')

if __name__ == '__main__':
    unittest.main()


