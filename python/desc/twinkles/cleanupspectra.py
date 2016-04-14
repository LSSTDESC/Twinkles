from __future__ import absolute_import, division, print_function
import tarfile
import pandas as pd
import gzip
import shutil
import os
import time


def namelist(fname):
    """
    return the tarfile nameand the targz file name
    """
    basename = fname.split('.')[0]
    tarfilename = basename + '.tar'
    targzname = tarfilename + '.gz'
    return tarfilename, targzname


def tarfilelist(lst, fname):
    """
    tar up all the filenames in lst into base.tar where base = basename for
    fname
    """

    outfname, _ = namelist(fname)
    f = tarfile.open(outfname, 'w')
    for s in lst:
        f.add(s)
    f.close()
    return outfname


def snspectralist(fname, logffname=None):
    """
    List all the spectra files associated with a phosim instance catalog
    """
    x = []
    with open(fname, 'r') as f:
        for line in f:
            if 'spectra_file' in line:
                x.append(line.split()[5])
    return x

def listFiles(logfile, prefix='InstanceCatalogs/phosim_input_'):
    """
    Read the log file to get a list of phosim instance catalogs done
    """
    df = pd.read_csv(logfile)
    fileList = [prefix + str(x) + '.txt' for x in df.obsHistID.values]
    return fileList


    return x

def gziptarfile(fname, prefix=''):
    """
    gzip a tarred up file
    """
    tarfilename, targzname = namelist(fname)
    targzname = prefix + targzname
    with open(tarfilename, 'rb') as f_in, gzip.open(targzname, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
def cleanup(fname):

    l = snspectralist(fname)
    tarfilename, _ = namelist(fname)
    for file in l:
        os.remove(file)
    os.remove(tarfilename)


if __name__=='__main__':
    import pandas as pd
    import sys
    import gzip

    logfilename = 'run.log'
    filenames = listFiles(logfilename, prefix='InstanceCatalogs/phosim_input_')
    for fname in filenames:

        starttime = time.time()
        print(fname)
        tgzfile = fname.split('.')[0] + '.tar.gz'
        if os.path.exists(tgzfile):
            continue
        with open(fname, 'rb') as fin, gzip.open(fname + '.gz', 'wb') as fout:
            shutil.copyfileobj(fin, fout)
        x = snspectralist(fname)
        listtime = time.time()
        print(len(x))
        tarfiles = tarfilelist(x, fname)
        tartime = time.time()
        gziptarfile(fname)
        ziptime = time.time()
        totaltime = ziptime - starttime
        zippingtime = ziptime - starttime
        tarringtime = tartime - starttime
        print(totaltime, zippingtime, tarringtime)
        cleanup(fname)
        print(fname, tarfile, x)
