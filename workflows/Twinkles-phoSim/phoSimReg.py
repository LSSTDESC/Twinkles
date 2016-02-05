#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## phoSimReg.py - Register phoSim's output data products in the dataCatalog
##
##  Required env-vars
## TW_ROOT
## TW_CONFIGDIR
## TW_ICFILE
## TW_SIXDIGSTREAM

import os,sys,shutil

## Say hello
print '\n\nWelcome to phoSimReg.py\n========================\n'
rc = 0

## Insert task config area for python modules (insert as 2nd element in sys.path)
#sys.path.insert(1,os.getenv('TW_CONFIGDIR'))
from config import *

## Setup logging, python style
import logging as log
log.basicConfig(format='%(asctime)s %(levelname)s in %(filename)s line %(lineno)s: %(message)s', level=log.INFO)

## Initialize dataCatalog
import registry
myDC = registry.registry(debug=True,dryrun=False)
myDC.init()
myDC.dumpConfig()


## DataCatalog path: /LSST-DESC/Twinkles/<taskName>/<stream>/<dataset>
dataCatPrefix = '/LSST-DESC/Twinkles'
task = os.environ['PIPELINE_TASKPATH'].split()[0].replace('.','/')
sstream = os.getenv('TW_SIXDIGSTREAM')   ## sub-stream
topStream = os.getenv('PIPELINE_STREAMPATH').split('.')[0]
topStream6 = "%06d" % int(topStream) 

## PhoSim output path: $TW_PHOSIMOUT/output
phoSimOutDir = os.path.join(os.environ['TW_PHOSIMOUT'],'output')

log.info("\n\tPreparing to register files in directory: "+str(phoSimOutDir))
print 'dataCatPrefix = ',dataCatPrefix
print 'stream =        ',topStream6
print 'task =          ',task

#dSite = 'slac.lca.archive'
#dSite = 'slac.desc.sim'
dSite = 'SLAC'
dType = 'PHOSIM'
filetypeMap = {'fits':'fits','fit':'fits','root':'root','txt':'txt','text':'txt','jpg':'jpg','png':'png','pdf':'pdf','html':'html','htm':'html','xls':'xls','lims':'lims'}


## Metadata for dataCatalog
##   


## Walk directory tree, replicating structure in dataCatalog, and registering all files
##  ******* THIS IS CURRENTLY NOT NECESSARY ********
## for root,dirs,files in os.walk(phoSimOutDir):
##    numIters += 1
##    ## if numIters > 10: break ## DEBUG-DEBUG-DEBUG-DEBUG-DEBUG-DEBUG-DEBUG-DEBUG-DEBUG
##    if debug:
##       print '\n[',numIters,']---------------------'
##       print 'root = ',root
##       print '# dirs = ',len(dirs)
##       print '# files= ',len(files)
##       print '---------------------------------'
##       pass



## Register all files in the phoSim output directory (do not recurse into subdirectories)
fList = os.listdir(phoSimOutDir)
numRegRequests = 0
numFile = 0
for f in fList:
    numFile += 1
    print numFile,': ',f
    fPath = os.path.join(phoSimOutDir,f)
    if os.path.isfile(fPath):
        print 'This is a file!'
        ## Register in dataCatalog (ignore sym links and sub-directories)
        ext = os.path.splitext(f)[-1].strip('.')
        if ext in filetypeMap:
            fType = filetypeMap[ext]
        else:
            fType = 'dat'
            pass

        dPath = os.path.join(dataCatPrefix,task,topStream6)
        fullName = os.path.join(dPath,f)
        print 'fPath = ',fPath
### TEMPORARY KLUDGE: until dataCat can handle filenames ending with ~
        if '~' in fullName or '$' in fullName:
            print '%%WARNING: illegal filename: ',fullName
            continue
### TEMPORARY KLUDGE: until dataCat can handle filenames ending with ~

## Registration (filePathOnDisk, dataCatalogPath, site, fileType, dataType)
        numRegRequests += 1
        myDC.register(fPath,dPath,dSite,fType,dType)
    else:
        print 'This is NOT a file!'
    pass



print '\nRegistration complete.'
print 'Number of registrations requested = ',numRegRequests



## All done
sys.exit(rc)
