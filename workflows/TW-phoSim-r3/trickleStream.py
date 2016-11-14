#!/usr/bin/env python
## trickleStream.py - trickle streams into a pipeline task

"""
trickleStream.py

   Trickle new top-level pipeline streams into an existing task.
Basic operation of the script is to awaken, assess the current state
of the task and then, based on some simple rules, decide how many new
streams to create, create those new streams, then go to sleep.  This
cycle repeats until the target number of streams has been created.

-------------------------------------------------------------------------

It is assumed that some analysis has already been performed on the
task of interest to determine how each process step loads the
computing infrastructure.  In particular, one must provide, for
load-intensive job steps, the maximum number of simultaneously running
jobs which can be safely run without causing infrastructure melt-down.
There are many components to the infrastructure, including: AFS and
NFS file servers, xroot, and the network fabric.  Exactly how to
determine the maximum number of jobs involves experimentation and
monitoring. The use of Ganglia can be useful for analyzing
infrastructure loading.  The limits determined on an otherwise
unloaded system may be quite different from the limits one should use
in a realistic day-to-day environment, or in an environment where
large, unrelated bursts of computing occur.  This script cannot detect
or take these changing environments into account, so caveat emptor.

Before use, customize this script for the specific task of interest.
This involves defining six variables within a dictionary as in the
following example:

trickleParms = {}

trickleParms['task'] = 'P118-FT1'              Task name
trickleParms['maxRuns'] = 20000                Target number of streams for this task
trickleParms['firstStep'] = 'setupRun'         Name of first process step in task
trickleParms['steps'] = [step1,step2]          List of process steps used to limit stream creation, where
  step1 = ['/processRun processClump',300,10]     [name of process step, limit/cycle, multiplier](*)
  step2 = ['mergeClumps',300,1] 
trickleParms['maxStreamsPerCycle'] = 70        Maximum number of new streams per cycle
trickleParms['timePerCycle'] = 60              Time (seconds) between cycles

The first two items are obvious.

The 'firstStep' is used to determine exactly how many top-level streams have already been created.

The 'steps' item is where each potentially demanding job step is characterized

(*) The process step name is a string that may optionally include the
name of the subtask, as appropriate (only one level of subtask is
supported).  The limit/cycle is the maximum number simultaneously
running jobs of this type which can be safely run.  The multiplier is
the number of job steps of this type that result from a single
top-level stream (note that this number may vary within a task, so an
estimate may be needed).

The 'maxStreamPerCycle' is needed to prevent a large number of
simultaneously launching jobs from overloading the file server(s) upon
which the code resides, e.g., /u30 and /u35

The 'timePerCycle' may be chosen as desired but note that values less
than ~60 seconds may not increase the frequency of the cycles, as each
cycle may take that long (or longer) to complete.  The use of this
value is as the sleep time the script takes upon completion of one
cycle and before starting the next.

Once customized, simply run the script and preserve the output as a
bookkeeping record, e.g.,

$ ./trickleStream.py > ts.log &

Progress can then be monitored by watching the log,

$ tail -f ts.log


"""


import os,sys,datetime,time
import subprocess

## This rarely needs to be updated, but it should be in sync with the
## version used by the reprocessing task
REPcommonToolsDir = '/nfs/farm/g/glast/u38/Reprocess-tasks/commonTools/00-02-01'
sys.path.insert(0, REPcommonToolsDir)

from trickle import *       ## classes needed by trickleStream (stats and trickle)




## Define task-specific data


trickleParms = {}


## Task-specific settings.
trickleParms['task'] = 'P302-FITS'
#trickleParms['maxRuns'] = 34154             ## Block 1, 1/26/2015
#trickleParms['maxRuns'] = 36020             ## Block 2, 2/18/2015 & version 2.0 block 1
#trickleParms['maxRuns'] = 37023             ## Block 2 v2.0, 4/18/2015
#trickleParms['maxRuns'] = 37888             ## Block 3 v2.0, 6/11/2015
#trickleParms['maxRuns'] = 38198             ## Block 4 v2.0, -FINAL- 6/27/2015
trickleParms['maxRuns'] = 38238             ## Block 5 v2.0, emergency 40 runs 8/5/2015
trickleParms['firstStep'] = 'setupRun'


## one config...
##step1 = ['/mergeRun mergeClumps',2000,1]
##trickleParms['steps'] = [step1]
##trickleParms['maxStreamsPerCycle'] = 150
##trickleParms['timePerCycle'] = 120


## ****** Semi-restrained running ********
step1 = ['/mergeRun mergeClumps',2500,1]
trickleParms['steps'] = [step1]
trickleParms['maxStreamsPerCycle'] = 50
trickleParms['timePerCycle'] = 60


## ## Flat-out running configuration
## step1 = ['mergeClumps',2500,1]
## trickleParms['steps'] = [step1]
## trickleParms['maxStreamsPerCycle'] = 200
## trickleParms['timePerCycle'] = 180


## Restrained running configuration
## step1 = ['mergeClumps',400,1]
## trickleParms['steps'] = [step1]
## trickleParms['maxStreamsPerCycle'] = 100
## trickleParms['timePerCycle'] = 120


######################
###    BEGIN       ###
######################


start = datetime.datetime.now()
print "\n--------> Entering trickleStream at ",start,', for task: ',trickleParms['task'],'\n'
sys.stdout.flush()

mytask = trickle(trickleParms)

## mytask.chatter = True  ## Debug
## mytask.dryRun = True   ## Debug
## mytask.maxCycles = 2   ## Debug

mytask.run()

sys.exit(0)
