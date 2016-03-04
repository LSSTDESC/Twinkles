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
    A `pandas.DataFrame` with the phosim Instance Catalog with metadata
    accessed as a dictionary through the meta attribute of the return.
    """

    # read the header into a metadata list, and get number of lines to skip
    # for catalog
    metalines = []
    with open(fname) as f:
        linenum = 0
        for line in f:
            if line.startswith('object'):
                continue
            metalines.append(line)
            linenum +=1

    # process the headers into a metadata list
    meta = metadataFromLines(metalines)

    # read the catalog into a dataframe
    df = pd.read_csv(fname, skiprows=linenum, names=names, sep='\s+')
    df.meta = meta
    return df

def metadataFromLines(lines):
    """
    process the metadata lines into a dictionary
    """
    info = [line.split() for line in lines]
    meta = {key: np.float(value) for key, value in info}

    return meta


if __name__ =="__main__":

    meta, df = readPhoSimInstanceCatalog('/Users/rbiswas/src/LSST/sims_catUtils/examples/SNOnlyPhoSimCatalog.dat')
    print df.head()


