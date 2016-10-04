"""
Test code for sqlite based tools.
"""
from __future__ import absolute_import
import os
import unittest
import sqlite3
from desc.twinkles import get_twinkles_visits, SqliteDataFrameFactory

class SqlLiteToolsTestCase(unittest.TestCase):
    "TestCase class for sqlite_tools module."
    def setUp(self):
        """
        Create a test dataset as an sqlite db for exercising
        get_twinkles_vists.
        """
        self._test_file = 'my_test_sqlite.db'
        connection = sqlite3.connect(self._test_file)
        connection.execute("create table Summary (obsHistID, fieldID)")
        self._obsHistIDs = (359, 123, 59025, 430201, 430201)
        self._fieldID = 1942
        for obsHistID in self._obsHistIDs:
            connection.execute("""insert into Summary values
                                  (%i, %i)""" % (obsHistID, self._fieldID))
        other_fieldIDs = (49530, 2093, 59220)
        other_obsHistIDs = (340298, 2342, 1550)
        for obsHistID, fieldID in zip(other_obsHistIDs, other_fieldIDs):
            connection.execute("""insert into Summary values
                                  (%i, %i)""" % (obsHistID, fieldID))
        connection.commit()
        connection.close()

    def tearDown(self):
        "Clean up test file."
        os.remove(self._test_file)

    def test_get_twinkles_visits(self):
        "Test get_twinkles_visits."
        obsHistIDs = get_twinkles_visits(self._test_file, fieldID=self._fieldID)
        self.assertEqual(len(obsHistIDs), len(set(self._obsHistIDs)))
        self.assertEqual(obsHistIDs, sorted(list(set(self._obsHistIDs))))
        self.assertEqual(get_twinkles_visits(self._test_file, 1941), [])

    def test_sqliteDataFrameFactory(self):
        "Test SqliteDataFrameFactory"
        my_factory = SqliteDataFrameFactory(self._test_file)
        df = my_factory.create('obsHistID fieldID'.split(), 'Summary')
        df_sel = df[df['fieldID'] == self._fieldID]
        self.assertEqual(len(df_sel), len(self._obsHistIDs))
        self.assertTupleEqual(tuple(df_sel['obsHistID']), self._obsHistIDs)

if __name__ == '__main__':
    unittest.main()
