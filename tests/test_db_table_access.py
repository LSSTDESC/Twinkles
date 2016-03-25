"""
Unit tests for db_table_access module.
"""
import unittest
import MySQLdb
import desc.twinkles.db_table_access as db_table_access

def get_db_info():
    """
    Try to connect to Travis CI MySQL services or the user's via
    ~/.my.cnf and return the connection info.  Otherwise, return
    an empty dict, which should skip the tests.
    """
    db_info = {}
    try:
        try:
            # Travis CI usage:
            my_db_info = dict(db='myapp_test', user='travis')
            test = MySQLdb.connect(**my_db_info)
        except Exception, eobj:
            print eobj
            # User's configuration:
            my_db_info = dict(read_default_file='~/.my.cnf')
            test = MySQLdb.connect(**my_db_info)
        test.close()
        db_info = my_db_info
    except Exception, eobj:
        print eobj
        pass
    return db_info

_db_info = get_db_info()

@unittest.skipUnless(_db_info, "MySQL database not available")
class db_table_access_TestCase(unittest.TestCase):
    "Test db_table_access class."
    def setUp(self):
        "Create set of LsstDatabaseTable objects."
        global _db_info
        self.desc = db_table_access.LsstDatabaseTable(**_db_info)
        _db_info['table_name'] = 'test_ForcedSource'
        self.forced = db_table_access.ForcedSourceTable(**_db_info)
        _db_info['table_name'] = 'test_CcdVisit'
        self.ccdVisit = db_table_access.CcdVisitTable(**_db_info)
        del _db_info['table_name']

    def tearDown(self):
        "Drop the test tables and delete the LsstDatabaseTable objects."
        self.desc.apply('drop table if exists test_CcdVisit')
        self.desc.apply('drop table if exists test_ForcedSource')
        try:
            del self.ccdVisit
        except AttributeError:
            pass
        try:
            del self.forced
        except AttributeError:
            pass
        try:
            del self.desc
        except AttributeError:
            pass

    def test_table_names(self):
        "Test that the tables have the expected names."
        self.assertEqual(self.desc._table_name, '')
        self.assertEqual(self.forced._table_name, 'test_ForcedSource')
        self.assertEqual(self.ccdVisit._table_name, 'test_CcdVisit')

    def test_connection_pool(self):
        """
        Test that connection objects match for objects with the same
        connection info.
        """
        self.assertEqual(self.desc._mysql_connection,
                         self.forced._mysql_connection)
        self.assertEqual(self.desc._mysql_connection,
                         self.ccdVisit._mysql_connection)

    def test_connection_ref_counts(self):
        "Test the reference counts for the db connection."
        key = self.desc._conn_key
        self.assertEqual(self.desc._LsstDatabaseTable__connection_refs[key], 3)

    def test_destructor(self):
        "Test the destructor for correct connection management."
        del self.ccdVisit
        key = self.forced._conn_key
        self.assertEqual(
            self.forced._LsstDatabaseTable__connection_refs[key], 2)
        del self.forced
        key = self.desc._conn_key
        self.assertEqual(
            self.desc._LsstDatabaseTable__connection_refs[key], 1)

if __name__ == '__main__':
    unittest.main()
