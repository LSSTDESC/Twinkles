"""

Estimates the CPU time required for a phosim simulation of a 30-s visit.  The
inputs are filter, moonalt, and moonphase, or obsHistID (an Opsim ID from
a specified (hard coded) Opsim sqlite database.

The random forest is generated (and saved as a pickle file) by 
run1_cpu_generate_rf.py, using only the filter, moonalt, and moonphase
features.  This script needs to be run only once.

"""

import pickle
import math
import numpy as np
import pandas as pd

print('Loading Random forest pickle')
RFbest = pickle.load(open("RF_pickle.p", "rb"))
print('Pickle loaded')

class CpuPred(object):

    def params(self, filter_arg, moonalt_arg, moonphase_arg):
        """
        Returns predicted fell-class CPU time in seconds for user-supplied
        filter (0-5 for ugrizy), moon altitude (deg), and moon phase (0-100).
        """
        self.time = 10**RFbest.predict(np.reshape([filter_arg, moonalt_arg, \
            moonphase_arg], (1, 3)))

    def opsimdb(self,obsid):
        """
        Returns predicted fell-class CPU time in seconds, for a specified
        obshistid for the Opsim sqlite database specified in -opsim_sqlite_db-
        below.  If it does not correspond to a defined visit then an exception
        is thrown.
        """
        
        opsim_sqlite_db = '/nfs/farm/g/lsst/u1/DESC/Twinkles/kraken_1042_sqlite.db'

        from desc.twinkles.sqlite_tools import SqliteDataFrameFactory
        factory = SqliteDataFrameFactory(opsim_sqlite_db)

        rec = factory.create('obsHistID filter moonAlt moonPhase'.split(), 'Summary',
            condition="where obsHistID='%i' order by obsHistID asc"%obsid)

        if rec.size <> 0:
            # Translate the filter string into an index 0-5
            filtmap = 'u g r i z y'.split()
            filt = filtmap.index(rec["filter"].values[0])

            moonalt = math.degrees(rec["moonAlt"].values[0])
            moonphase = rec["moonPhase"].values[0]
            obshistid = rec["obsHistID"].values[0]

            self.time = 10**RFbest.predict(np.reshape([filt, \
                moonalt, moonphase], (1, 3)))
        else:
            raise RuntimeError("%d is not a Run 1 obsHistID"%obsid)

if __name__ == '__main__':
    # Here are some dumb examples
    pred = CpuPred()
    pred.params(3,10.,50.)
    print(pred.time)

    pred.opsimdb(210)
    print(pred.time)

    # This one won't work
    #pred.opsimdb(-999)

    # Extract the Run 1 metadata and evaluate the predicted CPU times
    run1meta = pd.read_csv("../../../data/run1_metadata_v6.csv",usecols=\
        ["filter","moonalt","moonphase","cputime_fell"])

    filter = np.array(run1meta["filter"])
    moonalt = np.array(run1meta["moonalt"])
    moonphase = np.array(run1meta["moonphase"])
    actual = np.array(run1meta["cputime_fell"])

    predicted = np.zeros(filter.size,dtype=float)

    for i in range(filter.size):
        pred.params(filter[i],moonalt[i],moonphase[i])
        predicted[i] = pred.time

    import matplotlib.pyplot as plt
    import pylab

    plt.scatter(np.log10(actual), np.log10(predicted))
    plt.plot([4,6.5],[4,6.5])
    pylab.ylim([4,6.5])
    pylab.xlim([4,6.5])
    plt.xlabel('log10(Actual Fell CPU time, s)')
    plt.ylabel('log10(Predicted Fell CPU time, s)')
    plt.title('Run 1 CPU Times Predicted vs. Actual')
    pylab.savefig('predicted_vs_actual.png',bbox_inches='tight')
    plt.show()
