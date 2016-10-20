import os
import numpy as np
import pandas as pd
from desc.twinkles import OpSimOrdering
from lsst.utils import getPackageDir
import unittest

class TestOpSimOrdering(unittest.TestCase):

    def setUp(self):
        self.opSimDBPath = '/Users/rbiswas/data/LSST/OpSimData/minion_1016_sqlite.db'
        self.ops = OpSimOrdering(self.opSimDBPath, timeMax=0.8)
        self.numRecords = len(self.ops.filteredOpSim)
        self.numUniqueRecords = len(self.ops.uniqueOpSimRecords)

    def test_numRecords(self):
        """
        Given the setup where no records are dropped due to predictedPhoSimTime
        being too long, show that the filtered OpSim records (in favor of lower
        propID belonging to the OpSim WFD proposals has the same number of records
        as dropping duplicates.
        """
        pts = self.ops.fullOpSimDF(self.opSimDBPath)
        pts.drop_duplicates(subset='obsHistID', inplace=True)
        self.assertEqual(len(pts), self.numUniqueRecords)
        self.assertGreaterEqual(self.numUniqueRecords, self.numRecords)

    def test_conservedNumRecordsInSplit(self):
        """
        Check that all of the records in the filtered OpSim are in one of the
        three splits by first checking that the sum of numbers of records in
        each split matches the number of records in the filtered OpSim
        """
        n1 = self.ops.Twinkles_3p1.obsHistID.size
        n2 = self.ops.Twinkles_3p2.obsHistID.size
        n3 = self.ops.Twinkles_3p3.obsHistID.size
        self.assertEqual(n1 + n2 + n3, self.numRecords)

    def test_uniqueObsHistIDs(self):
        """
        Check that when all the obsHistIDs in the splits are combined
        together they are all unique. This completes the check that all of 
        the records in the filtered OpSim are in one of the splits and also
        that no pointing is in two splits
        """
        v1 = self.ops.Twinkles_3p1.obsHistID.values.tolist()
        v2 = self.ops.Twinkles_3p2.obsHistID.values.tolist()
        v3 = self.ops.Twinkles_3p3.obsHistID.values.tolist()
        arr = np.array(v1 + v2 + v3)
        self.assertEqual(np.unique(arr).size, self.numRecords)

    def test_Twink_3p1_uniqueCombinations(self):
        """
        By the definition of the process, Twink_3p_1 should have one
        and only one record representing each each unique combination
        """
        v1 = self.ops.Twinkles_3p1.obsHistID.values.tolist()
        df = self.ops.filteredOpSim.set_index('obsHistID').ix[v1]
        # number of members in each unique combination of night and filter
        nums = df.groupby(['night', 'filter']).expMJD.count().unique().tolist()
        self.assertEqual(len(nums), 1)
        self.assertEqual(nums[0], 1)
    def test_Twink_3p1_allUniqueCombinations(self):
        """
        Check that Twink_3p_1 includes a record for each unique combination in
        filteredOpSim
        """
        v1 = self.ops.Twinkles_3p1.obsHistID.values.tolist()
        df = self.ops.filteredOpSim.set_index('obsHistID').ix[v1]
        Twink_3p1_Groups = df.groupby(['night', 'filter']).groups.keys()
        Orig_groups = self.ops.filteredOpSim.groupby(['night', 'filter']).groups.keys()
        self.assertEqual(len(Twink_3p1_Groups), len(Orig_groups))


if __name__ == '__main__':
    unittest.main()
