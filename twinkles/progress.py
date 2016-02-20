#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys, os

df = pd.read_csv('run.log')
print df.time.diff()
if len(sys.argv) > 1:
    _ = plt.hist(df.time.diff(), bins=np.arange(200., 400., 20.))
    plt.show()
