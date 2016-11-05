#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## phoSimPrep.py - Perform potentially lengthy preparatory steps prior to running phoSim
##

import os,sys,shutil

## Insert task config area for python modules (insert as 2nd element in sys.path)
sys.path.insert(1,os.getenv('TW_CONFIGDIR'))
from config import *


print '\n\nWelcome to phoSimPrep.py\n========================\n'

## Generate instanceCatalog on-the-fly

## Create scratch directory in (persistent) /lustre, if necessary.
## File path = PHOSIMSCRATCH (defined in config.py)

if not os.path.exists(PHOSIMSCRATCH): os.makedirs(PHOSIMSCRATCH)

## ### Until actual code is available, simply copy/link necessary files
## ### into pre-agreed scratch space.
## base = 'phosim_input_200'

## src = os.path.join(PHOSIMIN,base+'.txt.gz')
## dst = os.path.join(PHOSIMSCRATCH,'instanceCatalog.txt.gz')
## print 'Instance Catalog:'
## print 'src = ',src
## print 'dst = ',dst
## shutil.copy2(src,dst)

## src = os.path.join(PHOSIMIN,base+'.tar.gz')
## dst = os.path.join(PHOSIMSCRATCH,'SEDs.tar.gz')
## print 'SEDs:'
## print 'src = ',src
## print 'dst = ',dst
## shutil.copy2(src,dst)

## generate instance catalog and SED files for phoSim

#  generatePhosimInput.py obsHistID [options]
destIC = os.path.join(PHOSIMSCRATCH,'instanceCatalog.txt')
destSEDdir = PHOSIMSCRATCH
obsHistID = os.getenv('TW_OBSHISTID')
cacheDir = os.getenv('TW_CACHEDIR')
opssimDir = os.getenv('TW_OPSSIMDIR')
twbinDir = os.getenv('TW_BIN')
print 'destIC = ',destIC
print 'destSEDdir = ',destSEDdir
print 'obsHistID = ',obsHistID
print 'cacheDir = ',cacheDir
print 'opssimDir = ',opssimDir
print 'twbinDir = ',twbinDir

##       SCRIPT to generate phoSim instance catalog and custom SED library
##
# generatePhosimInput.py <opsHistID> --OpSimDBDir <loc-opsSim database> --seddir <loc-to-write-output SEDs> --outfile <instanceCat-name> --cache_dir <catsim-cacheDir>
### e.g., (the SEDs will occupy the "spectra_files" directory)
# generatePhosimInput.py 200 --OpSimDBDir /nfs/farm/g/desc/u1/data/Twinkles --seddir . --outfile phosim_input_200.txt

genCmd = os.path.join(twbinDir,'generatePhosimInput.py')

print '\nGenerate InstanceCatalog and SED files'
cmd = "time "+genCmd+" "+obsHistID+" --OpSimDBDir "+opssimDir+" --seddir "+destSEDdir+" --outfile "+destIC+" --cache_dir "+cacheDir
print 'cmd = ',cmd
print
sys.stdout.flush()
rc = os.system(cmd)
sys.stdout.flush()
print 'rc = ',rc
if rc > 255: rc = 1

## Confirm working directory
cmd = 'ls -l '+destSEDdir
print cmd
os.system(cmd)

## Run a trial phoSim to ensure all inputs+code respond reasonably?
##      (not yet, if ever)

sys.exit(rc)




