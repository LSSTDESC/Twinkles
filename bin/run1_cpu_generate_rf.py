#!/usr/bin/env python
"""
Generates Random Forest predictor for Run 1 CPU times, based on the iPython
ML notebook by Phil Marshall
https://github.com/drphilmarshall/StatisticalMethods/blob/master/examples/SDSScatalog/Quasars.ipynb
and updates by Humna Awan and Tom McClintock
https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/examples/notebooks/Run1CPUTimes.ipynb

@author: sethdigel
"""
from __future__ import print_function
import copy
import numpy as np
import os
import pandas as pd
import pickle
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import mean_squared_error

# Define the seed for the Random Forest regressor, train_test_split
seed = 999

# Read the Run 1 metadata (just the columns that will be used)
# For this file, the CPU times for Run 1 visits that did not finish (because
# they reached the 120-hour CPU limit) were estimated from the CPU times 
# from a 1 sec phosim simulation of the same visit (Run 1sx).
# -cputime_fell- is the CPU time scaled to the equivalent running time on
# a 'fell' # class host in the batch farm.  If the visit was not actually
# run on a fell host, the scale factor applied was estimated from the 
# Run 1sx times for a few visits that were re-run on hosts of different
# classes.
run1meta = pd.read_csv(os.path.join(os.environ['TWINKLES_DIR'], 'data', 
    'run1_metadata_v6.csv'),
    usecols=['filter', 'moonalt', 'moonphase', 'cputime_fell'])

# N.B. The Random Forest is used to estimate the logarithm of the CPU time,
# which has a much smaller dynamic range
cputime = np.log10(run1meta['cputime_fell'])

# Remove the features that did not actually turn out to be useful
# (Actually, here just remove the cputime_fell, which is the quantity to be
# estimated from the other metadata)
run1meta_features = copy.copy(run1meta)
del run1meta_features['cputime_fell']
#del run1meta_features['runlimit']
#del run1meta_features['expmjd']
#del run1meta_features['rotskypos']
#del run1meta_features['altitude']
#del run1meta_features['rawseeing']
#del run1meta_features['airmass']
#del run1meta_features['hostname']
#del run1meta_features['filtskybrightness']
#del run1meta_features['dist2moon']
#del run1meta_features['sunalt']

# Define the inputs X and outputs Y and divide them both into training and
# testing subsets
X = run1meta_features.values
y = cputime.values
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=seed)

RF = RandomForestRegressor(random_state=seed)
# Run a grid search with Random Forests over n_estimators
param_grid_RF = {'n_estimators': np.array([16,32,64, 128, 256, 512])}

np.set_printoptions(suppress=True)
print(param_grid_RF)

RF_tuned = GridSearchCV(RF, param_grid_RF, verbose=3)

RF_tuned.fit(X_train, y_train)
print(RF_tuned.get_params())

y_RF_tuned_pred = RF_tuned.predict(X_test)

mse_RF_tuned = mean_squared_error(y_test,y_RF_tuned_pred)
r2_RF_tuned = RF_tuned.score(X_test, y_test)

# Print some metrics of the quality of the RF modeling
print('MSE (tuned RF) =', mse_RF_tuned)
print('R2 score (tuned RF) =',r2_RF_tuned)

RFbest = RF_tuned.best_estimator_

print(run1meta_features.keys())
print(RFbest.feature_importances_)

print('Writing pickle file with the RF best estimator...')
pickle.dump(RFbest, open('RF_pickle.p', 'wb' ))
