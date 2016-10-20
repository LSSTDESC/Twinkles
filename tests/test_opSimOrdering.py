import os
import numpy as np
import pandas as pd
from desc.twinkles import OpSimOrdering
from lsst.utils import getPackageDir
import unittest

class TestOpSimOrdering(unittest.TestCase):

    def setUp(self):
        self.opSimDBPath = '/Users/rbiswas/data/LSST/OpSimData/minion_1016_sqlite.db'
        self.ops = OpSimOrdering(self.opSimDBPath, timeMax=3.)
        self.numRecords = len(self.ops.filteredOpSim)

    def test_numRecords(self):

        pts = self.ops.fullOpSimDF(self.opSimDBPath)
        pts.drop_duplicates(subset='obsHistID', inplace=True)
        self.assertEqual(len(pts), self.numRecords)

    def test_conservedNumRecordsInSplit(self):
        n1 = self.ops.Twinkles_3p1.obsHistID.size
        n2 = self.ops.Twinkles_3p2.obsHistID.size
        n3 = self.ops.Twinkles_3p3.obsHistID.size
        self.assertEqual(n1 + n2 + n3, self.numRecords)

    def test_uniqueObsHistIDs(self):
        v1 = self.ops.Twinkles_3p1.obsHistID.values.tolist()
        v2 = self.ops.Twinkles_3p2.obsHistID.values.tolist()
        v3 = self.ops.Twinkles_3p3.obsHistID.values.tolist()
        arr = np.array(v1 + v2 + v3)
        self.assertEqual(np.unique(arr).size, self.numRecords)

    def test_Twink_3p1_uniqueCombinations(self):
        v1 = self.ops.Twinkles_3p1.obsHistID.values.tolist()
        df = self.ops.filteredOpSim.set_index('obsHistID').ix[v1]
        # number of members in each unique combination of night and filter
        nums = df.groupby(['night', 'filter']).expMJD.count().unique().tolist()
        self.assertEqual(len(nums), 1)
        self.assertEqual(nums[0], 1)


if __name__ == '__main__':
    unittest.main()
