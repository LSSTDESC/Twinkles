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

## Insert task config area for python modules (insert as 2nd element in sys.path)
sys.path.insert(1,os.getenv('TW_CONFIGDIR'))
from config import *

## Say hello
sstream = os.getenv('TW_SIXDIGSTREAM')
log.info("Starting stream %s",sstream)

## Select visit to simulate from file of obsHistIDs
vf = open(PHOSIMVL,'r')
vn = 0
for line in vf:
    if not line.strip().isdigit():continue
    if vn == int(sstream):
        obsHistID = line.strip()
        print 'Selected obsHistID = ',obsHistID
        break
    vn += 1
    pass
vf.close()

## Preserve the obsHistID for subsequent processing steps
cmd = 'pipelineSet TW_OBSHISTID '+obsHistID
print cmd
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass
   

## Prepare instanceCatalog

##  There are two modes.  Static assumes all instance catalogs are
##  pre-created and a list exists in the task's config directory
##  Dynamic employs the generatePhosimInputs script in the phoSimPrep
##  processing step.

icMode = PHOSIMICMODE

if icMode == 'static':
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
    icSelect = os.path.join(PHOSIMIN,icList[stream])
    log.info('Selected instance catalog: \n\t%s',icSelect)
    sedSelect = ' '

elif icMode == 'dynamic':
    log.info('phoSim instance catalog will be generated dynamically')
    icSelect = 'instanceCatalog.txt'  ## working name for instance catalog
    sedSelect = 'SEDs.tar.gz'  ## defunct. Files created in spectra_files/
    pass



## Preserve the instance catalog and SED info for subsequent processing steps
cmd = 'pipelineSet TW_INSTANCE_CATALOG '+icSelect
print cmd
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass

cmd = 'pipelineSet TW_SEDS '+sedSelect
print cmd
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass





## Read in list of sensors to process
try:
    sListObj = open(PHOSIMSL)
except:
    log.error("Unable to open instance catalog list: "+PHOSIMSL)
    sys.exit(99)

lineList = sListObj.read().splitlines()
log.info("Opened and read list of sensors to process, \n\t%s",PHOSIMSL)


## Unpack the sensor list
ns = 0
sList1 = []
sList2 = []      ## dirty hack to get around limitation of email and Pipeline
for line in lineList:
    if len(line) == 0 or line.startswith('#'): continue  # ignore empty/comment lines
    ns += 1
    if ns < 100: sList1.append(line)
    else: sList2.append(line)
    pass
log.info('Number of sensors to process = %i',ns)



## Preserve the sensor info for subsequent processing steps
cmd = 'pipelineSet TW_NUM_SENSORS '+str(ns)
print cmd
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass


sensorList1 = sList1[0]
for n in range(1,len(sList1)):
    sensorList1 += ','+sList1[n]
    pass
print 'sensorList1 = ',sensorList1
cmd = 'pipelineSet TW_SENSOR_LIST1 '+sensorList1
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass

sensorList2 = 'None'
if len(sList2)>0:
    sensorList2 = sList[0]
    if len(sList)>1:
        for n in range(0,len(sList2)):
            sensorList2 += ','+sList2[n]
            pass
        pass
    pass
    
print 'sensorList2 = ',sensorList2
cmd = 'pipelineSet TW_SENSOR_LIST2 '+sensorList2
print cmd
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass



## Pass along the phoSim physics override file location for subsequent steps
log.info('phoSim command (physics override) file: \n\t%s',PHOSIMCF)
cmd = 'pipelineSet TW_PHYSICS_OVERRIDE '+PHOSIMCF
print cmd
rc = os.system(cmd)
if rc <> 0 :
    log.error("Unable to set pipeline variable")
    sys.exit(99)
    pass



## Create working directory structure for this invocation of phoSim

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
