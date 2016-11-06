#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## status.py - Summarize status of a phoSim task whichh uses checkpoints

import os,sys

## Pretend to be a Pipeline task
TASK = 'PhoSim-deep-pre3'
CPNUM = 8
TW_ROOT='/nfs/farm/g/desc/u1/Pipeline-tasks/'+TASK
os.environ['TW_ROOT'] = TW_ROOT
TW_CONFIGDIR = TW_ROOT+'/config'
os.environ['TW_CONFIGDIR'] = TW_CONFIGDIR
TW_WORK = TW_ROOT+'/phosim_output'
os.environ['TW_WORK'] = TW_WORK

## Insert task config area for python modules (insert as 2nd element in sys.path)
sys.path.insert(1,os.getenv('TW_CONFIGDIR'))
from config import *

log.info('Entering status.py for task '+TASK)

#    min2delay = os.environ['PIPELINE_STREAMPATH'].split('.')[1]
sys.stdout.flush()



#########################################################################
##### PRELIMINARIES
#########################################################################

sfd = open('sensorList.txt','r')
sensorRefList = sfd.read().splitlines()
sfd.close()
print "There are ",len(sensorRefList)," sensors being simulated in this task."


#########################################################################
##### PART I: simply based on contents of work & output  directories
#########################################################################

## Locate /work directories
visitList = os.listdir(TW_WORK)
visitList.sort()
numVisits = len(visitList)
stuckList = []
totDONE = 0
totRuns = 0
print "There are ",numVisits," visits simulated in this task."
nVisits = 0

visitSummary = {}   ## {visitNum:[list of data]}
allVisits = []      ## list of visitSummary items

## Loop over visits
for visit in visitList:
    print "\n\tVISIT ",visit,"\n"
    visitStream = int(visit)
    visitDir = os.path.join(TW_WORK,visit)
    if not os.path.isdir(visitDir):
        print "Warning: encountered a non-visit directory: ",visitDir
        continue
    print 'Exploring directory: ',visitDir
    nVisits += 1
    sensorList = os.listdir(visitDir)
    if 'archives' in sensorList: sensorList.remove('archives')
    sensorList.sort()
    print "There are ",len(sensorList)," sensors being processed for this visit"
    #print 'sensorList = ',sensorList

## Loop over sensors
    nSensors = 0
    for sensor in sensorList:
        sensorDir = os.path.join(visitDir,sensor)
        if sensor == 'archives': continue
        if not os.path.isdir(sensorDir):
            print "Warning: encountered non-sensor directory: ",sensorDir
            continue
        nSensors += 1
        totRuns += 1
        
## Determine Pipeline stream for this sensor
        sensorStream = -1
        if sensor in sensorRefList:
            sensorStream = sensorRefList.index(sensor)
            pass

## Dive into the work directories      
        workDir = os.path.join(sensorDir,'work')
        outDir = os.path.join(sensorDir,'output')
        if not os.path.exists(workDir):
            print "No work directory for visit ",visit,', sensor ',sensor
            continue
        workList = os.listdir(workDir)
        nckpt = 0
        ckptList = []
        
## Count checkpoint files (files containing "ckptdt" or "ckptfp")
        for wfile in workList:
            if wfile.find('ckptdt') != -1:
                nckpt += 1
                ckpt = os.path.splitext(os.path.splitext(wfile)[0])[0].split('_')[-1]
                ckptList.append(ckpt)
                pass
            pass

        ckptList.sort()
        if len(ckptList) > 0 and int(ckptList[-1]) == CPNUM-1:
            oList = os.listdir(outDir)
            if len(oList) > 1:
                ckptList.append("DONE")
                totDONE += 1
            else:
                stuckList.append([visit,sensor,visitStream,sensorStream,list(ckptList)])
                pass
            pass
        #print 'visit ',visit,', sensor ',sensor,', stream.substream ',visitStream,'.',sensorStream,', ckpt list ',ckptList
        visitSummary[nSensors] = [visit,sensor,visitStream,sensorStream,list(ckptList)]
        pass
    allVisits.append(dict(visitSummary))
    #    print "\n################################################################\n"
    pass


#################################################################################
#################################################################################
############    Summary   #######################################################
#################################################################################
#################################################################################


## Generate summary report
print '\n\nSUMMARY'
print 'Number of visits = ',len(allVisits)


allHist = []
for visit in range(len(allVisits)):
    visitHist = [0,0,0,0,0,0,0,0,0,0]
    visitSummary = allVisits[visit]
    #    print 'visitSummary for visit ',visit,' = ',visitSummary
    #    print 'visit ',visit,', for ',len(visitSummary),' sensors'
    for sensor in visitSummary.keys():
        sensorSummary = visitSummary[sensor]
        ckptList = sensorSummary[4]
        ix = len(ckptList)
        visitHist[ix] += 1
        pass
    pass
    #print 'visitHist = ',visitHist
    allHist.append(list(visitHist))

    numSensors = 0
    print '\nVisit ',visit,' summary:'
    for bin in range(len(visitHist)):
        numSensors += visitHist[bin]
        if bin == 0: print ' No checkpoints complete = ',visitHist[0]
        if bin > 0 and bin < len(visitHist)-1: print 'Completed checkpoint ',bin-1,' = ',visitHist[bin]
        if bin == len(visitHist)-1:            print '                    DONE = ',visitHist[bin]
        pass
    print 'Number of sensors for which data was found this visit = ',numSensors
    pass

if len(stuckList) > 0:
    print '\nPrinting list of jobs which seem stuck after last checkpoint:'
    for stuck in stuckList:
        print stuck
        pass
    pass

print '\n\n------------------\nTotal sensor jobs = ',totRuns
print 'Total DONE jobs   = ',totDONE,' (',float(totDONE)/float(totRuns)*100.,'%)'






#####  PART II: based on log file parsing

## Locate logFile directory tree

## Loop over visits (streams)

## Loop over sensors (sub-streams)

## Loop over all logFiles (current + archives)

## based on PIPELINE_AUTORETRYNUMBER, and PIPELINE_EXECUTIONNUMBER, determine current checkpoint

## based on output from the setupPhoSimInput object, determine current and final checkpoint.

## Record CPU time (and memory?)

## Print summary of:
##   1) all jobs (# sensors per visit)
##      running; complete (success); complete (failed); not started
##      historam or CSV of CPU and memory used vs checkpoint number
##
##   2) Checkpoint summary (histo of current or # completed checkpoints?)

