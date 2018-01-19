from __future__ import absolute_import, print_function, division

import pandas as pd
__all__ = ['read_catsimInstCat']

def read_catsimInstCat(filename):
    """"
    read a catsim Instance Catalog style csv into a `pandas.dataFrame`

    Parameters
    ----------
    filename : string, mandatory
        absolute path to csv file to be read into a dataframe
    
    Return
    ------
    `pd.dataframe` with correct column headers and values
    """
    df = pd.read_csv(filename)
    mydict = dict()
    for col in df.columns:
        mydict[col]=col[1:]
    df.rename(columns=mydict, inplace=True)
    return df

