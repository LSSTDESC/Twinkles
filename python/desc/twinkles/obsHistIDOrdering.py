from __future__ import absolute_import, division, print_function
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

__all__ = ['OpSimOrdering']
class OpSimOrdering(object):
    def __init__(self, opSimDBPath, timeMax=0.9):
        self._opsimDF = self.fullOpSimDF(opSimDBPath)
        self._opsimDF['predictedPhoSimTimes'] = np.random.uniform(size=len(self._opsimDF))
        self._opsimDF['year'] = self._opsimDF.night // 365
        self.timeMax = timeMax
        self.distinctGroup = ['night', 'filter']
    
    @property
    def filteredOpSim(self):
        pts = self._opsimDF.copy()
        pts.drop_duplicates(subset='obsHistID', inplace=True, keep='first')
        thresh = self.timeMax
        return pts.query('predictedPhoSimTimes < @thresh')
    
    @property
    def Twinkles_WFD(self):
        groupDistinct = self.filteredOpSim.groupby(self.distinctGroup)
        SelectedObsHistIDs = groupDistinct.propID.transform(min) == self.filteredOpSim.propID
        return self.filteredOpSim[SelectedObsHistIDs]
     
    @property
    def Twinkles_3p1(self):
        grouped = self.Twinkles_WFD.groupby(self.distinctGroup)
        idx  = grouped.predictedPhoSimTimes.transform(min) == self.Twinkles_WFD.predictedPhoSimTimes
        return self.Twinkles_WFD[idx].sort_values(by='expMJD', inplace=False)
    
    @property
    def Twinkles_3p2(self):
        """
        dr5
        """
        doneObsHist = tuple(self.Twinkles_3p1.obsHistID.values.tolist())
        return self.filteredOpSim.query('year == 4 and obsHistID not in @doneObsHist').sort_values(by='expMJD',
                                                                                                   inplace=False)
    @property
    def Twinkles_3p3(self):
        obs_1 = self.Twinkles_3p1.obsHistID.values.tolist()
        obs_2 = self.Twinkles_3p2.obsHistID.values.tolist()
        obs = tuple(obs_1 + obs_2)
        return self.filteredOpSim.query('obsHistID not in @obs')
        
    @staticmethod
    def fullOpSimDF(opsimdbpath, query="SELECT * FROM Summary WHERE FieldID == 1427 ORDER BY PROPID"):
        engine = create_engine('sqlite:///' + opsimdbpath)
        pts = pd.read_sql_query(query, engine)
        return pts
