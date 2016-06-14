"""
Unit tests for instance catalog analysis code.
"""
from __future__ import print_function, absolute_import
import os
import unittest
import desc.twinkles

class AnalyseICat_TestCase(unittest.TestCase):
    """
    Test case class fo analyseICat .py code.
    """
    def setUp(self):
        """
        Some toy metadata in key-value pairs for testing.
        """
        header = """Opsim_obshistid 220
SIM_SEED 11699
Unrefracted_RA 53.0091385
Unrefracted_Dec -27.4389488
Opsim_moonra 256.312326
Opsim_moondec -23.4843941
Opsim_rotskypos 256.719412
Opsim_filter 1
Opsim_rawseeing 0.869226
Opsim_sunalt -32.2253236
Opsim_moonalt -36.2196989
Opsim_dist2moon 124.329951
Opsim_moonphase 3.838714
Opsim_expmjd 59580.1354
Opsim_altitude 67.7483059
Opsim_azimuth 270.941772
exptime 30
airmass 1.080465
SIM_NSNAP 1
SIM_VISTIME 30"""
        data = header.split()
        self.md = dict((key, float(value)) for key, value
                       in zip(data[::2], data[1::2]))
        self.lines = header.split('\n')

    def tearDown(self):
        "Clean up."
        pass

    def test_metadataFromLines(self):
        "Test metadataFromLines."
        my_md = desc.twinkles.metadataFromLines(self.lines)
        self.assertEqual(my_md, self.md)

    def test_readPhoSimInstanceCatalog(self):
        "Test the reading of a PhoSim instance catalog."
        filename = os.path.join(os.environ['TWINKLES_DIR'], 'tests',
                                'phosim_test_instance_catalog.txt')
        df = desc.twinkles.readPhoSimInstanceCatalog(filename)
        self.assertEqual(df.meta, self.md)
        self.assertEqual(len(df), 79)
        self.assertEqual(df['SourceID'][0], 992887068677)

if __name__ == '__main__':
    unittest.main()
