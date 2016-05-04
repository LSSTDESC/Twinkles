"""
Functions for extracting information from a repository registry file.
"""
from __future__ import absolute_import
import os
from collections import OrderedDict
import sqlite3
import astropy.time

__all__ = ['find_registry', 'get_visit_mjds', 'get_visits']

def find_registry(data_repo, registry_name='registry.sqlite3'):
    basePath = data_repo
    while not os.path.exists(os.path.join(basePath, registry_name)):
        if os.path.exists(os.path.join(basePath, "_parent")):
            basePath = os.path.join(basePath, "_parent")
        else:
            raise RuntimeError("Could not find registry file")
    return os.path.join(basePath, registry_name)

def get_visit_mjds(data_repo):
    """
    Return a dictionary of visit MJDs keyed by visit number.
    data_repo is the output repository of the Twinkles Level 2
    pipeline.
    """
    registry_file = find_registry(data_repo)
    conn = sqlite3.connect(registry_file)
    mjds = OrderedDict()
    query = "select visit, taiObs from raw where channel='0,0' order by visit asc"
    for row in conn.execute(query):
        visit_time = astropy.time.Time(row[1], format='isot')
        mjds[row[0]] = visit_time.mjd
    return mjds

def get_visits(data_repo):
    """
    Return a dictionary of visits ids keyed by 'ugrizy' filter.
    data_repo is the output repository of the Twinkles Level 2
    pipeline.
    """
    registry_file = find_registry(data_repo)
    conn = sqlite3.connect(registry_file)
    filters = 'ugrizy'
    visits = OrderedDict([(filter_, []) for filter_ in filters])
    for filter_ in filters:
        query = "select visit from raw_visit where filter='%s'" % filter_
        for row in conn.execute(query):
            visits[filter_].append(row[0])

    return visits
