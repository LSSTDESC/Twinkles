from __future__ import absolute_import, division, print_function
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

__all__ = ['OpSimOrdering']
class OpSimOrdering(object):
    """
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
        max value of `predictedPhoSimTimes` in hours for a record for it to be
        used in the calculation
    filteredOpSim : `pd.DataFrame`
        dataFrame representing the OpSim data with duplicate records dropped in
        favor of the ones with propID ==54 (WFD) and any record that has a
        `predictedPhoSimTimes` > `self.timeMax` dropped
    """
    def __init__(self, opSimDBPath, timeMax=0.9):
        self._opsimDF = self.fullOpSimDF(opSimDBPath)
        self._opsimDF['predictedPhoSimTimes'] = np.random.uniform(size=len(self._opsimDF))
        self._opsimDF['year'] = self._opsimDF.night // 365
        self.timeMax = timeMax
        self.distinctGroup = ['night', 'filter']
    
    @property
    def filteredOpSim(self):
        """
        - drop duplicates in favor of propID for WFD
        - drop records where the phoSim Runtime estimate exceeds threshold
        """
        pts = self._opsimDF.copy()
        # Since the original SQL query ordered by propID, keep=first 
        # preferentially chooses the propID for WFD
        pts.drop_duplicates(subset='obsHistID', inplace=True, keep='first')
        thresh = self.timeMax
        return pts.query('predictedPhoSimTimes < @thresh')
    
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
