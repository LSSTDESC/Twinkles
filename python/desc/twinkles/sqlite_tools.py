"""
Tools for reading sqlite3 databases.
"""
from __future__ import absolute_import
import sqlite3
import pandas as pd

__all__ = ['SqliteDataFrameFactory', 'get_twinkles_visits']

class SqliteDataFrameFactory(object):
    """
    Class to generate pandas data frames from columns in an sqlite3 db.
    """
    def __init__(self, sqlite_file):
        """
        Create a sqlite3 connection object.

        Parameters
        ----------
        sqlite_file : str
            The sqlite filename.
        """
        self.sqlite_file = sqlite_file
        self.conn = sqlite3.connect(sqlite_file)

    def create(self, columns, table, condition=None, distinct=False):
        """
        Given a sequence of columns, create a data frame from the
        data in table, with an optional query condition.

        Parameters
        ----------
        columns : sequence
            The names of the columns to include in the data frame.
        table : str
            The name of the db table to query.
        condition : str
            An SQL "where" clause to extract records that satisify the
            specified constraints.
        distinct : bool, optional
            Flag to indicate that duplicate records should be omitted.
            This is False by default.

        Returns
        -------
        pandas DataFrame

        Example:
        df_factory = SqliteDataFrameFactory('kraken_1042_sqlite.db')
        df = df_factory.create("obsHistID fieldRA fieldDec".split(),
                               "Summary", condition="where filter='r'")
        """
        if distinct:
            query = 'select distinct %s from %s' % (','.join(columns), table)
        else:
            query = 'select %s from %s' % (','.join(columns), table)
        if condition is not None:
            query += ' ' + condition
        return pd.read_sql_query(query, self.conn)

def get_twinkles_visits(opsim_db_file, fieldID=1427):
    """
    Return a sorted list of visits for a given fieldID from an OpSim
    db file.

    Parameters
    ----------
    obsim_db_file : str
        Filename of the OpSim db sqlite file
    fieldID : int, optional
        ID number of the field for which to return the visit numbers.
        The default value is the Twinkles field.

    Returns
    -------
    list : A list of obsHistIDs (i.e., visit numbers).

    Since a given visit can belong to more than one proposal, there
    may be multiple rows in the Summary table with the corresponding
    obsHistID.  This function removes the duplicates.
    """
    connect = sqlite3.connect(opsim_db_file)
    query = """select distinct obsHistID from Summary where fieldID=%i
               order by obsHistID asc""" % fieldID
    obsHistIDs = [x[0] for x in connect.execute(query)]
    return obsHistIDs
