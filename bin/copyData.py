"""
Copies parts of a data repository corresponding to certain visits into a new
repository to make a small test repository

To Use change the strings in script part:
    - change the srcdir to point to the repo that is to be copied
    - obtain the list visits to a list of obshistIDs of visits that are desired in the subset
    - change newRepo to point to the absolute path of location where you want this 
"""
from __future__ import absolute_import
import shutil
import os
import glob
import pandas as pd


def copyRepoForVisits(srcRepo, newRepo, visitSeq, dirDepth=3):
    """
    Copy a part of source repository srcRepo to a new Repo
    keeping only information corresponding to visits iDs in
    visitSeq.
    This is done by using the structure of the repository
    and not by directory structure independent methods. It copies
    directories and files which have the format 'vvisitID' within
    a depth of 3 in the source repository.

    Parameters
    ----------
    srcRepo : str, mandatory
        absolute path to data repository from which results are to be
        copied
    newRepo : str, mandatory
        absolute path to location where newrepository is to be written
    visitSeq : Iterable of integers, mandatory
        sequence of integers indexing the visits that should be copied
    dirDepth : integer, optional, defaults to 3
        Depth to which the directory of the form v visitID will be
        searched for

    Returns
    -------
    list of integers indexing visits that were requested but not found
    in the original data repository

    Examples
    --------
    """
    if not os.path.exists(newRepo):
        os.makedirs(newRepo)
    # list of directory trees to copy over
    srcs = []
    # list of visits that have not been found
    notFoundList = []
    newRepo = os.path.abspath(newRepo)

    for visit in visitSeq:
        visitFound = False
        for depth in range(dirDepth):
            mystr = srcRepo + '/*'*depth + '/v' + visit + '*'
            src = glob.glob(mystr)
            if len(src) > 0:
                srcs += src
                visitFound = True
        if not visitFound:
            notFoundList.append(visit)
    for src in srcs:
        dest = os.path.join(newRepo, src.split(srcdir)[1][1:])
        shutil.copytree(src, dest)
    return notFoundList

if __name__ == '__main__':

    # Generate the visits (obsHistIDs)
    df = pd.read_csv('obsHistIDs.csv').head(5)
    visits = [str(id) for id in df.obsHistID.values]

    # Directories
    srcdir = '/global/homes/t/tony_j/Twinkles/985visits/985visits'
    newRepo = 'repo4'

    vnf = copyRepoForVisits(srcRepo=srcdir, newRepo=newRepo, visitSeq=visits)
    print(vnf)
