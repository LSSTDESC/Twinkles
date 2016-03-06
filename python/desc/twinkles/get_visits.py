"""
Module for function to find the visits for each filter via the
registry.sqlite3 file.
"""
import os
from collections import OrderedDict
import sqlite3

def get_visits(data_repo):
    """
    Return a dictionary of visits ids keyed by 'ugrizy' filter.
    data_repo is the output repository of the Twinkles Level 2
    pipeline.
    """
    # Normally one would use the data butler to do this, but the
    # registry.sqlite3 file needs to be processed by
    # genInputRegistry.py, and that script is, as of 2016-03-05,
    # inconsistent with obs_lsstSim/policy/LsstSimMapper.paf.  Since
    # we only need to read the raw_visit table, it is more efficient
    # read the registry file with sqlite3 directly.
    conn = sqlite3.connect(os.path.join(data_repo, '_parent',
                                        'registry.sqlite3'))
    filters = 'ugrizy'
    visits = OrderedDict([(filter_, []) for filter_ in filters])
    for filter_ in filters:
        query = "select visit from raw_visit where filter='%s'" % filter_
        for row in conn.execute(query):
            visits[filter_].append(row[0])

    return visits

if __name__ == '__main__':
    data_repo = '/nfs/farm/g/desc/u1/users/jchiang/Twinkles/work/multiband/output'
    visits = get_visits(data_repo)

    print visits





