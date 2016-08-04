"""
Tools for reading sqlite3 databases.
"""
from __future__ import absolute_import
import sqlite3
import pandas as pd

class SqliteDataFrameFactory(object):
    """
    Class to generate pandas data frames from columns in an sqlite3 db.
    """
    def __init__(self, sqlite_file):
        "Create a sqlite3 connection object."
        self.sqlite_file = sqlite_file
        self.conn = sqlite3.connect(sqlite_file)

    def create(self, columns, table, condition=None):
        """
        Given a sequence of columns, create a data frame from the
        data in table, with an optional query condition.

        Example:
        df_factory = SqliteDataFrameFactory('kraken_1042_sqlite.db')
        df = df_factory.create("obsHistID fieldRA fieldDec".split(),
                               "Summary", condition="where filter='r'")
        """
        query = 'select %s from %s' % (','.join(columns), table)
        if condition is not None:
            query += ' ' + condition
        data = [row for row in self.conn.execute(query)]
        return pd.DataFrame(data=data, columns=columns)
