from __future__ import absolute_import, division, print_function
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from lsst.utils import getPackageDir
from .phosim_cpu_pred import CpuPred 


__all__ = ['OpSimOrdering']

class OpSimOrdering(object):
    """
    Code to split the Twinkles 3 obsHistIDs into sets that will be ordered so
    that we would try to do Twinkles_3p1 first, followed by Twinkles_3p2,
    followed by Twinkles_3p3
    Parameters
    ----------
    opSimDBPath : absolute path to OpSim database
    timeMax : float, unit of hours, default to 0.9
        a threshold of time, such that any OpSim pointings with predictedPhoSim
        times above that threshold will be dropped.

    Attributes
    ----------
    distinctGroup : list
        unique combination of variables in which the records are grouped. The
        variables are 'night' and 'filter'
    timeMax : float,
        max value of `predictedPhoSimTimes` in sec for a record for it to be
        used in the calculation
    filteredOpSim : `pd.DataFrame`
        dataFrame representing the OpSim data with duplicate records dropped in
        favor of the ones with propID ==54 (WFD) and any record that has a
        `predictedPhoSimTimes` > `self.timeMax` dropped
    """
    def __init__(self, opSimDBPath, randomForestPickle=None, timeMax=120.0):
        """
        Parameters
        ----------
        opSimDBPath : string, mandatory
            absolute path to a sqlite OpSim database
        randomForestPickle : string, defaults to None
            absolute path to a pickle of an instance of
            `sklearn.ensemble.forest.RandomForestRegressor`
        timeMax: float, defaults to 120.0
            max value of predicted PhoSim Run times of selected OpSim records.
            Records with predicted PhoSIm run times beyond this value are
            filtered out of `filteredOpSim`
        """
        twinklesDir = getPackageDir('Twinkles')
        self._opsimDF = self.fullOpSimDF(opSimDBPath)
        if randomForestPickle is None:
            randomForestPickle = os.path.join(twinklesDir, 'data',
                                              'RF_pickle.p')
        if not os.path.exists(randomForestPickle):
            raise ValueError('pickle does not exist at {}'.format(randomForestPickle))

        self.cpuPred = CpuPred(rf_pickle_file=randomForestPickle,
                                             opsim_df=self._opsimDF,
                                             fieldID=1427)
        self._opsimDF['predictedPhoSimTimes'] = self.predictedTimes()

        self._opsimDF['year'] = self._opsimDF.night // 365
        self.timeMax = timeMax * 3600.
        self.distinctGroup = ['night', 'filter']

    def predictedTimes(self):
        opsim_len = len(self._opsimDF)
        times = np.ones(opsim_len) * np.nan 
        for i, obshistid in enumerate(self._opsimDF.reset_index()['obsHistID']):
            times[i] = self.cpuPred(obshistid)
        return times

    
    @property
    def uniqueOpSimRecords(self):
        """
        - drop duplicates in favor of propID for WFD
        """
        pts = self._opsimDF.copy()
        # Since the original SQL query ordered by propID, keep=first 
        # preferentially chooses the propID for WFD
        pts.drop_duplicates(subset='obsHistID', inplace=True, keep='first')
        return pts

    @property
    def filteredOpSim(self):
        """
        - drop records where the phoSim Runtime estimate exceeds threshold
        """
        thresh = self.timeMax
        return self.uniqueOpSimRecords.query('predictedPhoSimTimes < @thresh')

    @property
    def obsHIstIDsTooLong(self):
        """
        obsHistIDs dropped from Twink_3p1, Twink_3p2, Twink_3p3 because the
        estimated phoSim run time is too long.
        """
        filteredObsHistID = \
            tuple(self.filteredOpSim.reset_index().obsHistID.values.tolist())

        missing = self.uniqueOpSimRecords.query('obsHistID not in @filteredObsHistID')
        if len(missing) > 0:
            return missing.obsHistID.values
        else:
            return list()

    @property
    def Twinkles_WFD(self):
        """
        return a dataframe with all the visits for each unique combination with
        the lowest propID (all WFD visits or all DDF visits) in each unique
        combination
        """
        groupDistinct = self.filteredOpSim.groupby(self.distinctGroup)
        SelectedObsHistIDs = groupDistinct.propID.transform(min) == self.filteredOpSim.propID
        return self.filteredOpSim[SelectedObsHistIDs]
     
    @property
    def Twinkles_3p1(self):
        """
        For visits selected in Twinkles_WFD, pick the visit in each unique
        combination with the lowest value of the `predictedPhoSimTimes`
        """
        grouped = self.Twinkles_WFD.groupby(self.distinctGroup)
        idx  = grouped.predictedPhoSimTimes.transform(min) == self.Twinkles_WFD.predictedPhoSimTimes
        return self.Twinkles_WFD[idx].sort_values(by='expMJD', inplace=False)
    
    @property
    def Twinkles_3p2(self):
        """
        dr5 Observations that are in `filteredOpSim` and have not been done in 
        Twinkles_3p1
        """
        doneObsHist = tuple(self.Twinkles_3p1.obsHistID.values.tolist())
        return self.filteredOpSim.query('year == 4 and obsHistID not in @doneObsHist').sort_values(by='expMJD',
                                                                                                   inplace=False)
    @property
    def Twinkles_3p3(self):
        obs_1 = self.Twinkles_3p1.obsHistID.values.tolist()
        obs_2 = self.Twinkles_3p2.obsHistID.values.tolist()
        obs = tuple(obs_1 + obs_2)
        return self.filteredOpSim.query('obsHistID not in @obs').sort_values(by='expMJD', inplace=False)
        
    @staticmethod
    def fullOpSimDF(opsimdbpath, query="SELECT * FROM Summary WHERE FieldID == 1427 ORDER BY PROPID"):
        engine = create_engine('sqlite:///' + opsimdbpath)
        pts = pd.read_sql_query(query, engine)
        return pts
