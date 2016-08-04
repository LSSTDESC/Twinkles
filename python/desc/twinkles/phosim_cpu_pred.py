"""
Estimates the CPU time required for a phosim simulation of a 30-s visit.  The
inputs are filter, moonalt, and moonphase, or obsHistID (an Opsim ID from
a specified (hard coded) Opsim sqlite database.

The random forest is generated (and saved as a pickle file) by 
run1_cpu_generate_rf.py, using only the filter, moonalt, and moonphase
features.  This script needs to be run only once.
"""

from __future__ import print_function, absolute_import
import os
import pickle
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pylab
from desc.twinkles.sqlite_tools import SqliteDataFrameFactory

class CpuPred(object):
    """
    Returns predicted fell-class CPU time in seconds for user-supplied
    filter (0-5 for ugrizy), moon altitude (deg), and moon phase (0-100) 
    -or- ObsHistID from the kraken_1042 Opsim run.  By default the code
    looks for the sqlite database for kraken_1042 in a specific location on
    SLAC Linux.  Also by default it looks only for obsHistID values that are
    in the Twinkles Run 1 field (by selecting on the corresponding fieldID).

    RF_pickle.p is written by run1_cpu_generate_rf.py
    """
    def __init__(self, rf_pickle_file='RF_pickle.p', 
        opsim_db_file='/nfs/farm/g/lsst/u1/DESC/Twinkles/kraken_1042_sqlite.db',
            fieldID=1427):
        self.RFbest = pickle.load(open(rf_pickle_file, 'rb'))
        factory = SqliteDataFrameFactory(opsim_db_file)
        self.obs_conditions = factory.create('obsHistID filter moonAlt moonPhase'.split(), 'Summary',
            condition='where fieldID=%d'%fieldID)

    def __call__(self, obsid):
        """
        Return the predicted CPU time given an obsHistID.  The obsHistID 
        must be in the Opsim database file and fieldID specified on
        initialization of the instance.
        """
        filter_index, moonalt, moonphase = self.conditions(obsid)
        return self.cputime(filter_index, moonalt, moonphase)

    def conditions(self, obsid):
        """
        Return the relevant observing conditions (i.e., those that are
        inputs to the Random Forest predictor) for the given obsHistID
        """
        rec = self.obs_conditions[self.obs_conditions['obsHistID'] == obsid]

        if rec.size != 0:
            # Translate the filter string into an index 0-5
            filter_index = 'ugrizy'.find(rec['filter'].values[0])

            moonalt = math.degrees(rec['moonAlt'].values[0])
            moonphase = rec['moonPhase'].values[0]
        else:
            raise RuntimeError('%d is not a Run 1 obsHistID in field %d'%obsid,fieldID)

        return filter_index, moonalt, moonphase

    def cputime(self, filter_index, moonalt, moonphase):
        return 10.**self.RFbest.predict(np.array([[filter_index, moonalt, 
            moonphase]]))

if __name__ == '__main__':
    # Here are some dumb examples
    pred = CpuPred()
    print(pred(210))

    print(pred.cputime(3.,10.,50.))

    # This one won't work
    #pred(-999)

    # Extract the Run 1 metadata and evaluate the predicted CPU times
    run1meta = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data',
        'run1_metadata_v6.csv'),
        usecols=['filter', 'moonalt','moonphase','cputime_fell'])

    filter = np.array(run1meta['filter'])
    moonalt = np.array(run1meta['moonalt'])
    moonphase = np.array(run1meta['moonphase'])
    actual = np.array(run1meta['cputime_fell'])

    predicted = np.zeros(filter.size,dtype=float)

    for i in range(filter.size):
        predicted[i] = pred.cputime(filter[i],moonalt[i],moonphase[i])

    plt.scatter(np.log10(actual), np.log10(predicted))
    plt.plot([4,6.5],[4,6.5])
    pylab.ylim([4,6.5])
    pylab.xlim([4,6.5])
    plt.xlabel('log10(Actual Fell CPU time, s)')
    plt.ylabel('log10(Predicted Fell CPU time, s)')
    plt.title('Run 1 CPU Times Predicted vs. Actual')
    pylab.savefig('predicted_vs_actual.png',bbox_inches='tight')
    plt.show()
