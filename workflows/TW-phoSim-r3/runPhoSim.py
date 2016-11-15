#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## runPhoSim.py - Run phoSim (one visit)

import os,sys
import subprocess,shlex

print '\n\n=====================================================================\n Entering runPhoSim.py\n=====================================================================\n'
sys.stdout.flush()



################## DEBUG #######################
################## DEBUG #######################
################## DEBUG #######################
## print 'Exiting without doing anything...'
## sys.exit(0)
################## DEBUG #######################
################## DEBUG #######################
################## DEBUG #######################




## Insert task config area for python modules (insert as 2nd element in sys.path)
sys.path.insert(1,os.getenv('TW_CONFIGDIR'))
from config import *
from setupPhoSimInput import setupPhoSimInput

log.info('Entering runPhoSim.py')

print 'PHOSIMPSCRATCH = ',PHOSIMPSCRATCH

## ################################# DEBUG ############################
#sys.exit(1)
debug=False

if debug:
    print "\n\n######################## RUNNING IN DEBUG MODE ######################\n\n"
## log.info("DEBUG:        Exiting!")
## sys.exit(1)
    if int(os.environ['PIPELINE_STREAMPATH'].split('.')[1]) > 4:
        print 'PIPELINE_STREAMPATH too large'
        sys.exit(1)
        pass
    pass

## ################################# DEBUG ############################


## In a weak attempt to prevent resource overload, offset the
## starttime by N minutes, where N is the substream number (0-188)
if not debug:
    min2delay = os.environ['PIPELINE_STREAMPATH'].split('.')[1]
    print 'min2delay = ',min2delay
    sec2delay = int(min2delay)*60
    cmd = "sleep "+str(sec2delay)
    print 'cmd = ',cmd
    os.system(cmd)
    pass

## Prepare for phoSim: inputs and work directory in _SCRATCH_ space
log.info('Prepare phoSim input area')
icFile = os.path.basename(os.environ['TW_INSTANCE_CATALOG'])
log.info('icFile = '+icFile)

prep = setupPhoSimInput(icFile)   ###########
#prep.inputRoot = PHOSIMIN
prep.inputRoot = PHOSIMPSCRATCH
prep.phosimInstDir = PHOSIMINST
prep.SEDlib = PHOSIMSEDS   ## production SEDs
prep.sedFile = 'spectra_files.tar.gz' ## sprinkled SEDs

prep.refCF = PHOSIMCF   ## cmd file template (may require editing)
prep.persistentScratch = True  ## dynamically generated instance catalog + SEDs
prep.cleanupFlag = False  ## DEBUG - keep contents of scratch

(work1,ic,seds,cFile) = prep.run()

print 'Return from prep.run:'
print ' work1 = ',work1
print '    ic = ',ic
print '  seds = ',seds
print ' cFile = ',cFile
print

## Which sensor is being simulated?
sensor = os.environ['TW_SENSOR']


## Prepare output directory in permanent NFS space

outDir = os.path.join(os.environ['TW_PHOSIMOUT'],sensor,'output')
if not os.access(outDir,os.W_OK):
    log.info('Creating output dir '+outDir)
    os.makedirs(outDir)
    pass

## Prepare work directory in permanent NFS space (but may not use it)
work2 = os.path.join(os.environ['TW_PHOSIMOUT'],sensor,'work')
if not os.access(work2,os.W_OK):
    log.info('Creating NFS workdir '+work2)
    os.makedirs(work2)
    pass

## Select either the scratch (work1) or permanent (work2) version of the workDir
workDir = work1

## Assess whether checkpointing is in progress and prepare, if necessary
prep.cpPrep(workDir)


## DEBUG stuff
prep.dump()


## Prepare phoSim command
log.info('Prepare phoSim command')
cmd = PHOSIMINST+'/phosim.py '+ic+' -c '+cFile+' -s '+sensor+' '+PHOSIMOPTS+' --sed '+seds+' -w '+workDir+' -o '+outDir
#cmd = 'time '+PHOSIMINST+'/phosim.py '+ic+' -c '+cFile+' -s '+sensor+' '+PHOSIMOPTS+' --sed '+seds+' -w '+workDir+' -o '+outDir
#cmd = 'time '+PHOSIMINST+'/phosim.py '+ic+' -c '+cFile+' -s '+sensor+' '+PHOSIMOPTS+' -w '+workDir+' -o '+outDir
print 'cmd = ',cmd
sys.stdout.flush()


## Execute phoSim
if prep.checkpoint:
    log.info('Execute phoSim at checkpoint '+str(prep.nextCP)+' in [0,'+str(prep.reqCP)+']')
else:
    log.info('Execute phoSim\n\n\n')
    pass
sys.stdout.flush()

## New way to execute phoSim, buffers stderr in case phosim does not adjust the return code properly
cmdList = shlex.split(cmd)
xphosim = subprocess.Popen(cmdList, stderr=subprocess.PIPE)
yak = xphosim.communicate()
rc = xphosim.returncode
print 'phoSim rc = ',rc,', type(rc) = ',type(rc)
if len(yak[1]) > 0:
    print '\n\n$WARNING: phoSim stderr output:\n',yak[1]
    print 'TERMINATING...'
    sys.exit(1)
#    if rc == 0:
#        print '\nphoSim returned error output but a zero return code...setting rc=1'
#        rc = 1
#        pass
    pass

## Original way of executing phoSim
#rc = os.system(cmd)

sys.stdout.flush()

## phoSim complete
print '\n\n\n******************************************************************'
print       '                 phoSim exited'
print       '******************************************************************\n'
print 'phoSim rc = ',rc
if rc > 255:       ## phoSim can return rc=256 which maps to '0' :(
    rc = rc % 255
    print 'Converting illegal return code to range [0,255].  New rc = ',rc
    pass

## Take a look at phoSim work and output directories
cmd = 'ls -ltraF '+workDir
print 'Contents of /work, ',workDir
sys.stdout.flush()
os.system(cmd)
sys.stdout.flush()
print       '******************************************************************\n'

cmd = 'ls -ltraF '+outDir
print 'Contents of /output, ',outDir
sys.stdout.flush()
os.system(cmd)
sys.stdout.flush()
print       '******************************************************************\n'

## Special handling of checkpointing
if prep.checkpoint:
    log.info('Checkpointing active')
    print 'prep.reqCP  = ',int(prep.reqCP)
    print 'prep.nextCP = ',int(prep.nextCP)
    if int(prep.reqCP) == int(prep.nextCP):
        log.info("Final checkpoint segment complete: "+str(prep.reqCP))
    else:
        log.info("Completed checkpoint "+str(prep.nextCP)+" in [0,"+str(prep.reqCP)+']')
##        rc = special value for Pipeline
        rc=3
        pass
    pass

## Clean up scratch area
log.info('Clean up scratch area')
prep.clean()



log.info('Exit with rc='+str(rc))
sys.exit(rc)

"""  From phoSim v3.5.2:

Usage: phosim.py instance_catalog [<arg1> <arg2> ...]

Options:
  -h, --help            show this help message and exit
  -c EXTRACOMMANDS, --command=EXTRACOMMANDS
                        command file to modify the default physics
  -p NUMPROC, --proc=NUMPROC
                        number of processors
  -o OUTPUTDIR, --output=OUTPUTDIR
                        output image directory
  -w WORKDIR, --work=WORKDIR
                        temporary work directory
  -b BINDIR, --bin=BINDIR
                        binary file directory
  -d DATADIR, --data=DATADIR
                        data directory
  --sed=SEDDIR          SED file directory
  --image=IMAGEDIR      postage stamp image directory
  -s SENSOR, --sensor=SENSOR
                        sensor chip specification (e.g., all, R22_S11,
                        "R22_S11|R22_S12")
  -i INSTRUMENT, --instrument=INSTRUMENT
                        instrument site directory
  -g GRID, --grid=GRID  execute remotely (no, condor, cluster, diagrid)
  -u UNIVERSE, --universe=UNIVERSE
                        condor universe (standard, vanilla)
  -e E2ADC, --e2adc=E2ADC
                        whether to generate amplifier images (1 = true, 0 =
                        false)
  --keepscreens=KEEPSCREENS
                        whether to keep atmospheric phase screens (0 = false,
                        1 = true)
  --checkpoint=CHECKPOINT
                        number of checkpoints (condor only)
  -v, --version         prints the version

"""
