#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## setupVisit.py - Set up for a run of phoSim for a single visit
##
##  Required env-vars
## TW_ROOT
## TW_CONFIGDIR
## TW_ICFILE
## TW_SIXDIGSTREAM

import os,sys,shutil

print '\n\nWelcome to setupVisit.py\n========================\n'

## Should probably go into config.py
archivesDirName = 'archives'
phoSimOutputRoot = 'phosim_output'
filePermissions = 0o2775     #   rwxrwxr-x


## Insert task config area for python modules (insert as 2nd element in sys.path)
sys.path.insert(1,os.getenv('TW_CONFIGDIR'))
from config import *

## Setup logging, python style
import logging as log
log.basicConfig(format='%(asctime)s %(levelname)s in %(filename)s line %(lineno)s: %(message)s', level=log.INFO)


## Say hello
sstream = os.getenv('TW_SIXDIGSTREAM')
log.info("Starting stream %s",sstream)


## Read in list of instance catalogs to process (ORDER IS IMPORTANT!)
icList = PHOSIMICL
try:
    icListObj = open(icList)
except:
    log.error("Unable to open instance catalog list: "+icList)
    sys.exit(99)

lineList = icListObj.read().splitlines()
log.info("Opened and read list of instance catalogs, \n\t%s",icList)


## Unpack the instance catalog list
nics = 0
icList = []
for line in lineList:
    if len(line) == 0 or line.startswith('#'): continue  # ignore empty/comment lines
    nics += 1
    #print nics,': ',line
    icList.append(line)
    pass
log.info('Number of instance catalogs found = %i',len(icList))


## Select instance catalog for this stream
stream = int(sstream)
print 'This is pipeline stream ',stream
if stream < 0 or stream > nics-1:
    log.error("This pipeline stream is out of range (not sufficient instance catalogs): %i",stream)
    sys.exit(99)
    pass
icSelect = icList[stream]
log.info('Selected instance catalog: \n\t%s',icSelect)


## Preserve the instance catalog info for subsequent processing steps
cmd = 'pipelineSet TW_INSTANCE_CATALOG '+icSelect
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass


## Create working  directory structure for this invocation of phoSim

### Check if directory already exists from previous execution and, if not, create it.
## Directory structure: $TW_ROOT/output/<stream>/{work,output}
outDir = os.path.join(os.environ['TW_ROOT'],phoSimOutputRoot,os.environ['TW_SIXDIGSTREAM'])
log.info('PhoSim output directory = \n\t%s',outDir)

### Is there a previous instance of this job step that requires archiving?
if not os.access(outDir,os.F_OK):                          ## NO
    log.info('Creating output directory: \n\t%s',outDir)
    os.makedirs(outDir)
    os.chmod(outDir,filePermissions)
    pass
else:                                                      ## YES
    ## Create appropriate archive directory, 'archive-N'
    archiveRoot = os.path.join(outDir,archivesDirName)
    if not os.access(archiveRoot,os.F_OK):
        log.info('Creating archives directory: \n\t%s',archiveRoot)
        os.makedirs(archiveRoot)
        os.chmod(archiveRoot,filePermissions)
        pass
    archiveDirList = os.listdir(archiveRoot)
    if len(archiveDirList) == 0:
        newArchiveName = 'archive-1'
    else:
        oldNumList = []
        for oldArc in archiveDirList:
            if oldArc.startswith('archive'):oldNumList.append(int(oldArc.split('-')[-1]))
            pass
        if len(oldNumList) > 0:
            oldNumList.sort()
            #print 'oldNumList = ',oldNumList
            newArchiveName = 'archive-'+str(oldNumList[-1]+1)
        else:
            log.error('Unexpected content in archives directory: \n\t%s\n\t %s',archiveRoot,archiveDirList)
            sys.exit(99)
            pass
        pass
    archiveDir = os.path.join(archiveRoot,newArchiveName)
    log.info("Creating new archive directory: \n\t%s",archiveDir)
    os.makedirs(archiveDir)
    os.chmod(archiveDir,filePermissions)
    
### And then squirrel away the old output in the new archive directory
    outDirList = os.listdir(outDir)
    log.info("Moving old files to archive")
    for item in outDirList:
        if not item == archivesDirName:
            sitem = os.path.join(outDir,item)
            ditem = os.path.join(archiveDir,item)
            #print 'shutil.move(',sitem,',',ditem,')'
            shutil.move(sitem,ditem)
            pass
        pass
    

## Pass along the path to the output directory
cmd = 'pipelineSet TW_PHOSIMOUT '+outDir
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable \n $%s",cmd)
    sys.exit(99)
    pass


## All done.
log.info ('BYE!\n\n\n*****\n')
log.shutdown()
sys.exit()
