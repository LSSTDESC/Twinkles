#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## phoSimPrep.py - Perform potentially lengthy preparatory steps prior to running phoSim
##

import os,sys,shutil
import tarfile

## Insert task config area for python modules (insert as 2nd element in sys.path)
sys.path.insert(1,os.getenv('TW_CONFIGDIR'))
from config import *
import scratch


print '\n\nWelcome to phoSimPrep.py\n========================\n'

## Generate instanceCatalog on-the-fly

## Create persistent scratch directory in /lustre, if necessary.
## File path = PHOSIMPSCRATCH (defined in config.py)
if not os.path.exists(PHOSIMPSCRATCH): os.makedirs(PHOSIMPSCRATCH)


## Create true scratch directory in /scratch
scr = scratch.scratch()
SCRATCH = scr.getScratch()
scr.statScratch()

    
## generate instance catalog and SED files for phoSim

#  generatePhosimInput.py obsHistID [options]
destIC = os.path.join(PHOSIMPSCRATCH,'instanceCatalog.txt')
#destSEDdir = PHOSIMPSCRATCH
destSEDdir = SCRATCH
obsHistID = os.getenv('TW_OBSHISTID')
cacheDir = TW_CACHEDIR
opssimDir = TW_OPSSIMDIR
twbinDir = TWINKLES_BIN
print 'destIC = ',destIC
print 'destSEDdir = ',destSEDdir
print 'obsHistID = ',obsHistID
print 'cacheDir = ',cacheDir
print 'opssimDir = ',opssimDir
print 'twbinDir = ',twbinDir
sys.stdout.flush()

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
if rc > 255:
    rc = 1
    print 'Awkward return code, redefining rc = ',rc
    pass


## tar up the sprinkled SED files
print 'tar up the sprinkled SED files and store in /lustre'
workingdir = os.getcwd()
os.chdir(destSEDdir)       ## Move to directory containing SED dir to feed tar relative paths

seddir = 'spectra_files'   ## This is where the sprinkled SEDs are generated
tarinput = seddir
tarname = seddir+'.tar.gz'
taroutput = os.path.join(PHOSIMPSCRATCH,tarname)  ## output goes into /lustre

tarobj = tarfile.open(name=taroutput,mode='w:gz')
tarobj.add(tarinput,recursive=True)  ## add entire directory tree of SEDs to tar archive
tarobj.close()

os.chdir(workingdir)



## Protect scratch directory: rwxr-sr-t
cmd = 'chmod -R 3755 '+PHOSIMPSCRATCH
print 'Protect scratch directory and its contents\n',cmd

rc2 = os.system(cmd)
if rc2 != 0:
    print "%ERROR: unable to execute command, ",cmd
    sys.exit(1)
    pass
pass


## Confirm working directory contents
cmd = 'ls -l '+PHOSIMPSCRATCH
print cmd
os.system(cmd)


## Clean up the local scratch space
scr.cleanScratch()
scr.statScratch()

## Run a trial phoSim to ensure all inputs+code respond reasonably?
##      (not yet, if ever)

sys.exit(rc)

































