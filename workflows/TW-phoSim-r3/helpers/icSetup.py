#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## icSetup.py - analyze a directory of Instance Catalogs from UW (Rahul)
##
## Check there is exactly one IC per SED
## Create list of files sorted by obshistid, which is part of the filename, e.g.,
##   phosim_input_215614.txt.gz
##


import os,sys,shutil,gzip

## Locate Instance Catalog
ICroot = '/nfs/farm/g/desc/u1/data/Twinkles/phoSim/Run1_InstCats_SEDs'

## Open IC dir and read in list of files

nlines = 0
nSEDs = 0
goodSEDs = 0
badSEDs = 0

print 'Using instance catalog directory:\n\t',ICroot
dirList = os.listdir(ICroot)
print '# of entries in directory = ',len(dirList)

nEntries = 0
nFiles = 0
nongz = 0
nNonfile = 0
nICfiles = 0
ICfiles = {}
nSEDfiles = 0
SEDfiles = {}

nSEDfiles = 0
SEDfileList = []

## Loop over all entries in this directory
for f in dirList:
    nEntries += 1
    fullPath = os.path.join(ICroot,f)
    ## Skip junk
    if os.path.isdir(fullPath) or os.path.islink(fullPath):
        nNonfile += 1
        continue
    if not f.endswith('.gz'):
        nongz += 1
        continue

    ## We should now have only compressed txt (instance cats) and tar (SEDs) 
    nFiles += 1
    if f.endswith('txt.gz'):
        nICfiles += 1
        ## Extract the obshistid for sorting
        foo = int(f.split('.')[0].split('_')[-1])
        ICfiles[foo] = f

    elif f.endswith('tar.gz'):
        nSEDfiles += 1
        ## Extract the obshistid for sorting
        foo = int(f.split('.')[0].split('_')[-1])
        SEDfiles[foo] = f
        pass

    pass

## Sort list of obshistid values
ICindex = ICfiles.keys()
SEDindex = SEDfiles.keys()

ICindex.sort()
SEDindex.sort()

## Quick checks the two lists are in sync
if len(ICindex) != len(SEDindex):
    print 'Lengths of IClist and SEDlist unequal'
    sys.exit()
    pass

## in sync?
for icx,sedx in zip(ICindex,SEDindex):
    if icx != sedx:
        print 'Unequal indicies'
        pass
    pass

## Print out file list
print '\n Table of IC files'
nx = 0
for icx in ICindex:
    nx += 1
    #    print nx,':\t',ICfiles[icx]
    print ICfiles[icx]
    pass



## All done.
print '\n\nSummary'
print 'nEntries = ',nEntries
print 'nNonfile = ',nNonfile
print 'nFiles   = ',nFiles
print 'nongz    = ',nongz
print 'nICfiles = ',nICfiles
print 'nSEDfiles= ',nSEDfiles




sys.exit()
sys.stdout.write('Starting scan')
sys.stdout.flush()
