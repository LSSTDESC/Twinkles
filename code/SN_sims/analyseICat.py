import pandas as pd
import numpy as np

def readPhoSimInstanceCatalog(fname,
                              names=['obj', 'SourceID', 'RA', 'DEC', 'MAG_NORM',\
                                      'SED_NAME', 'REDSHIFT', 'GAMMA1',\
                                      'GAMMA2', 'MU', 'DELTA_RA', 'DELTA_DEC',\
                                      'SOURCE_TYPE', 'DUST_REST_NAME',\
                                      'Av', 'Rv', 'Dust_Lab_Name', 'EBV']):
    """
    read the phoSimInstanceCatalog and return the contents

    Parameters
    ----------
    fname : mandatory, string
        filename of the phosim instance catalog
    names : a list of column names matching the number of columns

    Returns
    -------
    (meta, df) where meta is a dictionary of the metadata in the file and
    df is a `pandas.dataFrame`
    """

    metalines = []
    with open(fname) as f:
        line = f.readline()
        linenum = 0
        while not line.startswith('object'):
                metalines.append(line)
                linenum +=1
                line = f.readline()

    print linenum
    meta = metadataFromLines(metalines)
    df = pd.read_csv(fname, skiprows=linenum, names=names, sep='\s+')
    return meta, df

def metadataFromLines(lines):

    info = [line.split() for line in lines]
    meta = {key: np.float(value) for key, value in info}

    print meta
    return meta


if __name__ =="__main__":

    meta, df = readPhoSimInstanceCatalog('/Users/rbiswas/src/LSST/sims_catUtils/examples/SNOnlyPhoSimCatalog.dat')
    print df.head()


