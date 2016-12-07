## trickle.py -- classes used by trickleStream
import os,sys,datetime,time,math
import subprocess

class stats():
    ## Maintain pipeline stream submission statistics and report for trickleStream
    
    def __init__(self,depth=6):
        self.subList = []
        self.timeList = []
        self.numCycles = 0
        self.depth = depth
        self.chatter = False
        self.totSubmitted = 0
        self.firstTime = 0
        oldTime = datetime.datetime(2001,1,1)
        for i in range (self.depth):
            self.subList.append(-2)
            self.timeList.append(oldTime)
            pass
        return

    def dump(self):
        print "Dump of stats variables."
        print 'subList = ',self.subList  
        print 'timeList = ',self.timeList
        print 'numCycles = ',self.numCycles
        print 'depth = ',self.depth
        print 'chatter = ',self.chatter
        print 'totSubmitted = ',self.totSubmitted
        print 'firstTime = ',self.firstTime
        return
  
    def update(self,num2sub,subtime,totRemaining=-2):
## Maintain run submission statistics and report summary

        self.numCycles += 1
        if self.chatter:print '\nEntering stats.update (',self.numCycles,'): num2sub= ',num2sub,', subtime = ',subtime,', remaining = ',totRemaining
        numSub = len(self.subList)
        numTime = len(self.timeList)
        if numSub != numTime or numSub != self.depth:
            print "%ERROR: in stats.update, length of time and submission arrays not equal"
            return

        if self.numCycles == 1:
            self.firstTime = subtime
            pass

## Find newest entry in list
        newestCycle = numSub-1
        oldestCycle = 0
        for index in range(len(self.subList)-1):
            for index2 in range(index+1,len(self.subList)):
##            print 'Comparing index ',index,' with index ',index2
                t1 = self.timeList[index]
                t2 = self.timeList[index2]
##            print 't1 = ',t1
##            print 't2 = ',t2
                if self.subList[index] != -2:       ## Avoid default time values
                    if self.timeList[index] > self.timeList[index2]:
##                    print '  -- updating newestCycle with index ',index
                        newestCycle = index
                        pass
                    pass
                pass
            pass

        oldestCycle = (newestCycle+1) % numSub      ## reuse oldestCycle variable
        
        if self.chatter:
            print "Original lists:"
            print 'newestCycle = ',newestCycle
            print 'oldestCycle = ',oldestCycle
            pass

## Update lists
        self.subList[oldestCycle] = num2sub
        self.timeList[oldestCycle] = subtime

## Prepare for stats
        wsubList = []       ## working lists (with defaults removed)
        wtimeList = []
        for indx in range(len(self.subList)):
            if self.subList[indx]>-2:
                wsubList.append(self.subList[indx])
                wtimeList.append(self.timeList[indx])
                pass
            pass

        if self.chatter:print 'wsubList = ',wsubList
        if self.chatter:print 'wtimeList = ',wtimeList

        minTime = 0
        maxTime = 0
        if len(wtimeList)>0:
            minTime = min(wtimeList)
            maxTime = max(wtimeList)
            minTimeIndx = wtimeList.index(minTime)
            maxTimeIndx = wtimeList.index(maxTime)
            
            if self.chatter:print 'minTime = ',minTime,', timeList[',minTimeIndx,']'
            if self.chatter:print 'maxTime = ',maxTime,', timeList[',maxTimeIndx,']'
        else:
            print 'Nothing in working time list!!'
            pass

## Calculate time span of available submission blocks
        tdiff = maxTime - minTime
        hours = tdiff.days*24. + tdiff.seconds/60./60.
        if self.chatter:print 'tdiff = ',tdiff
        if self.chatter:print 'hours = ',hours

        gtdiff = subtime - self.firstTime
        ghours = gtdiff.days*24 + gtdiff.seconds/60./60.
        
## Sum submissions
        self.totSubmitted += num2sub
        totSub = 0
        if self.chatter:print 'self.subList = ',self.subList
        for num in self.subList:
            if num > -1: totSub += num
            pass

## Calculate runs/hour
        if ghours>0:
            grate = self.totSubmitted/ghours
            pgrate = '%5.1f' % (grate)
            pghours = '%5.2f' % (ghours)
            print 'Total stream submission rate     = ',pgrate,' runs/hour (',self.totSubmitted,'/',pghours,')'
            pass

        rate = 0
        if hours>0:
            rate = totSub/hours
            prate = '%5.1f' % (rate)
            phours = '%5.2f' % (hours)
            print 'Rolling avg strm submission rate = ',prate, ' runs/hour (',totSub,'/',phours,' over last ',len(wtimeList),' cycles)'
        else:
            if self.chatter: print 'Unable to calculate stream submission rate'
            pass

## Estimate ETA based on rolling average
        if rate>0 and totRemaining>0:
            etah = totRemaining/rate
##           print 'totRemaining = ',totRemaining,', rate = ',rate,', eta = ',etah
            rdays = int(etah/24)
            rhours = etah - rdays*24.
##            print 'remaining time = %3id %2.1fh' % (rdays,rhours)
            rseconds = int(rhours * 60 * 60)
            rdiff = datetime.timedelta(rdays,rseconds)
            now = datetime.datetime.now()
            ETA = now+rdiff
            print 'ETA: ',rdiff,'  --or--  ',ETA
            pass
        
        return
###############  end class stats


##########################################################################################################    
##########################################################################################################    
##########################################################################################################    

                


class trickle():
        #self.pipelineCmd        = '/afs/slac.stanford.edu/g/glast/ground/bin/pipeline '
        #self.pFind              = '/afs/slac.stanford.edu/u/gl/glast/pipeline-II/prod/pipeline '

    def __init__(self,trickleParms={}):
        self.pipelineCmd        = '/u/lt/lsstsim/pipeline/prod/pipeline '
        self.pFind              = '/u/lt/lsstsim/pipeline/prod/pipeline '
        self.chatter            = False
        self.dryRun             = False
        self.maxCycles          = 0  ## max # of cycles; 0 => as many as necessary
        self.stepsPerTopLevel   = []     ## to store dynamic value (#process steps created by a single top-level stream)
        self.task               = trickleParms['task']
        self.maxRuns            = trickleParms['maxRuns']
        self.firstStep          = trickleParms['firstStep']
        self.steps              = trickleParms['steps']
        self.maxStreamsPerCycle = trickleParms['maxStreamsPerCycle']
        self.timePerCycle       = trickleParms['timePerCycle']
        return
    
    def dumpParms(self):
        print '\n==============================================================================='
        print '  TRICKLE PARMS'
        print '==============================================================================='
        print 'task = ',self.task
        print 'maxRuns = ',self.maxRuns
        print 'firstStep = ',self.firstStep
        print 'steps = ',self.steps
        print 'maxStreamsPerCycle = ',self.maxStreamsPerCycle
        print 'timePerCycle = ',self.timePerCycle
        print '------DEBUG----------------'
        print 'maxCycles = ',self.maxCycles
        print 'chatter = ',self.chatter
        print 'dryRun = ',self.dryRun
        print '===============================================================================\n'
        sys.stdout.flush()
        return


    def processState2(self,taskString):

        ## "NEW way"
        
        ## Determine status of selected (sub)task job step
        chatter = self.chatter
        if chatter: print "Entering processState2(",taskString,")"

        ## These are the officially defined states within Pipeline-II
        allStates = ['WAITING','READY','QUEUED','SUBMITTED','RUNNING','SUCCESS','FAILED','TERMINATING','TERMINATED','CANCELING','CANCELED','SKIPPED']
        activeStates = ['WAITING','READY','QUEUED','SUBMITTED','RUNNING']
        dormantStates = ['SUCCESS','FAILED','TERMINATING','TERMINATED','CANCELING','CANCELED','SKIPPED']
        failedStates = ['FAILED','TERMINATING','TERMINATED']

        total = 0
        active = 0
        dormant = 0
        failed = 0
        bad = 0

        ## Reorgainze the 'taskString' variable.  Need to concatenate
        ## task/subtask/subtask w/o embedded spaces
        taskitems = taskString.split()    ## split into tokens.  First is task name
        if chatter:print 'taskitems = ',taskitems
        if len(taskitems)<2:
            print '%ERROR: taskString must contain at least task name and a processStep. ',taskString
        elif len(taskitems) == 2:
            task = taskitems[0]
            process = taskitems[1]
        else:
            task = taskitems[0]+taskitems[1]
            process = ''
            for item in taskitems[2:]:
                process += item+' '
            pass
        

    ## Output from pipeline find command: 
    ## Fetch information for this task process step:
        cmd = self.pFind+' --mode PROD find --count '+task+' '+process+' status'
        if chatter: print "%TIMESTAMP-A:   ",datetime.datetime.now()
        if chatter: print cmd
        cmdList = cmd.split()
        so = subprocess.Popen(cmdList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        responseList = so.communicate()[0].splitlines()
        if chatter: print "%TIMESTAMP-B:   ",datetime.datetime.now()


    ##
    ## Unpack data from pipeline command, and interpret
        totStatusLines = len(responseList)
        if chatter: print 'Total status lines = ',totStatusLines

        states = {}
        for stateCount in responseList:
            foo = stateCount.strip().split(',')
            states[foo[1]]=int(foo[0])
            pass

    ## Tally active and dormant states for load limiting
        for state in states:
            total += states[state]
            if chatter: print 'There are ',states[state],' jobs in ',state
            if state in activeStates:
                active += states[state]
            elif state in dormantStates:
                dormant += states[state]
            else:
                print "%ERROR - Unrecognized job state:  ",state,' in ',taskString
                bad += states[state]
                pass
            if state in failedStates:
                failed += states[state]
                pass
            pass

        

        return (total,active,dormant,bad,failed)





    
    def processState(self,taskString):

    ## "OLD Way"
        
    ## Determine the distribution of execution states for selected task process step
        chatter = self.chatter
        if chatter: print "Entering processState(",taskString,")"

    ## Output from pipeline find command:  [submitDate,host,exitCode], where 'null' means not available
    ##  e.g., [null,null,null]     means a stream has been created but not yet submitted
    ##        [<date>,null,null]   means submitted but not yet running
    ##        [<date>,<host>,null] means running
    ##        [<data>,<host>,<rc>] means complete (with return code)

    ## Development/debug stuff
    ##     funnyRuns = [3151382,3153041,3170471,3192384,3209081,3209092,3291550]
    ##    print 'entering processState():  ',datetime.datetime.now()

    ##
    ## Fetch information for this task process step:
        cmd = self.pFind+' --mode PROD find '+taskString+' submitDate host exitCode stream'
        if chatter: print "%TIMESTAMP-A:   ",datetime.datetime.now()
        if chatter: print cmd  ######## CHATTER
        cmdList = cmd.split()
        so = subprocess.Popen(cmdList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        responseList = so.communicate()[0].splitlines()
        if chatter: print "%TIMESTAMP-B:   ",datetime.datetime.now()


    ##
    ## Unpack data from pipeline command, and interpret
        totProcessSteps = len(responseList)
        if chatter: print 'Total process steps = ',totProcessSteps
        (numWaiting,numSubmitted,numRunning,numGood,numBad,numWeird) = (0,0,0,0,0,0)
        n = 0
        for process in responseList:
            (submitDate,host,exitCode,stream) = process.split(',')
            n += 1
            nstream = int(stream)

    ## Interpret job execution state (currently only works for batch jobs -- not scriptlets)
            if submitDate == 'null' and host == 'null' and exitCode == 'null':
                numWaiting += 1
                if chatter and numWaiting < 11:print '(waiting) submitDate = ',submitDate,', host = ',host,', exitCode = ',exitCode,', stream ',stream
            elif submitDate != 'null' and host == 'null' and exitCode == 'null':
                numSubmitted += 1
                if chatter and numSubmitted < 11:print '(submitted) submitDate = ',submitDate,', host = ',host,', exitCode = ',exitCode,', stream ',stream
            elif submitDate != 'null' and host != 'null' and exitCode == 'null':
                numRunning += 1
                if chatter and numRunning < 11:print '(running) submitDate = ',submitDate,', host = ',host,', exitCode = ',exitCode,', stream ',stream
            elif submitDate != 'null' and host != 'null' and exitCode != 'null':
                if exitCode == '0':
                    numGood += 1
                    if chatter and numGood < 11:print '(good) submitDate = ',submitDate,', host = ',host,', exitCode = ',exitCode,', stream ',stream
                else:
                    numBad += 1
                    if chatter: print 'BAD: ',n,submitDate,host,exitCode,stream
                    pass
                pass
            else:
                print "%WARNING: unexpected set of parameters: ",n,submitDate,host,exitCode,stream
                numWeird =+ 1
                pass
            pass

        summedTotal = numWaiting+numSubmitted+numRunning+numGood+numBad+numWeird
        if chatter:
            print '\tnumWaiting   ',numWaiting
            print '\tnumSubmitted ',numSubmitted
            print '\tnumRuning    ',numRunning
            print '\tnumGood      ',numGood
            print '\tnumBad       ',numBad
            print '\tnumWeird     ',numWeird
            print '\tsummedTotal  ',summedTotal
            print "%TIMESTAMP-C:   ",datetime.datetime.now()
            pass

        if totProcessSteps != summedTotal:
            print "%ERROR: totProcessSteps (",totProcessSteps,") != sum of individual states (",summedTotal,")"
            pass

        return [totProcessSteps,numWaiting,numSubmitted,numRunning,numGood,numBad,numWeird]





    def num2sub(self):
## Determine how many new top-level streams to create this cycle to
## avoid overloading computing infrastructure
##
##  Basic philosophy: calculate the maximum number of streams to
##  create based on the current situation for any number of criteria,
##  then select the *minimum* of those.
##
## Currently, those criteria all generating independent maxima
## include: individual job step limits (e.g., high I/O), number of new
## process launches (overloading the shared code disk); total streams
## in task.
        
    ## Figure out how many jobs to submit for this task
        chatter = self.chatter

    ## How many limiting job steps?
        numSteps = len(self.steps)
        if chatter: print 'Number of job steps used in load calculation = ',numSteps

    ## Determine total number of top-level streams and how many are active
##         print "\nOLD WAY..."
##         topLevel = self.processState(self.task+' '+self.firstStep)
##         print 'topLevel = ',topLevel
##         print "\nNEW WAY..."
        topLevel = self.processState2(self.task+' '+self.firstStep)
        if chatter: print 'topLevel = ',topLevel

    ## Determine maximum # of top-level streams to submit based upon limiting job steps
        num2submit = 'init'         ## initial (non)value
        for step in self.steps:
            subTask = False
            stepName = step[0]
            stepLimit = step[1]
            stepMultiplier = step[2]

            if chatter:
                print 'stepName = ',stepName
                print 'stepLimit = ',stepLimit
                print 'stepMultiplier = ',stepMultiplier
                pass

            if stepName.find('/') >= 0:subTask = True
            if chatter:
                if subTask:
                    print "This is a subtask step"
                else:
                    print "This is a top-level task step"
                    pass
                pass

            ## stepParms [from processState2] = (total,active,dormant,bad)
            if stepName == self.firstStep:
                stepParms = topLevel   ## Avoid duplication of effort
            else:
            ## Determine number of jobs in active and dormant pipeline states
                stepParms = self.processState2(self.task+' '+stepName)
                sys.stdout.flush()
                pass

            if chatter: print stepName,' [',stepLimit,',',stepMultiplier,'] = ',stepParms

            adjStepLimit = float(stepLimit)/stepMultiplier
            steps2submit = stepLimit - stepParms[1]
            ## 5/2/2013 subtract # active toplevel job steps from total (due to new pipeline throttling improvements)
            steps2submit = int(float(steps2submit)/stepMultiplier)
            if subTask: steps2submit -= topLevel[1]

            print 'STEP: ',stepName
            print '\t total # of instances          = ',stepParms[0]
            print '\t dormant (complete)            = ',stepParms[2]
            print '\t bad (unknown status)          = ',stepParms[3]
            print '\t failed                        = ',stepParms[4]
            print '\t active (running or committed) = ',stepParms[1]
            print '\t active limit                  = ',stepLimit
            if subTask:
                print '\t ==> top-level steps to submit = (',stepLimit,'-',stepParms[1],')/',stepMultiplier,' - ',topLevel[1],' = ',steps2submit
            else:
                print '\t ==> top-level steps to submit = (',stepLimit,'-',stepParms[1],')/',stepMultiplier,' = ',steps2submit
                pass

            if steps2submit < 1.0:
                print '      ---> Too many process steps active, no new top-level streams this cycle'
                steps2submit = -1   ## this means do not submit any jobs this cycle
                pass
##            print '   ',stepName,' limit = ',steps2submit

            if num2submit == 'init':
                num2submit = steps2submit
            elif steps2submit < num2submit:
                num2submit = steps2submit
                print '%% ',stepName,' limiting number of new top-level streams to ',num2submit
                pass
            pass

    ## Determine max # of top-level streams based on overall task limit
        max2submit = self.maxRuns - topLevel[0]
        print '   Streams remaining in task = ',max2submit
        if max2submit < 0:
            max2submit = 0
            print '%WARNING: it appears too many top-level streams have been created, ',topLevel[0]
            pass

        if num2submit > max2submit:
            num2submit = max2submit
            print '%% Limiting:  only ',max2submit,' top-level streams left in task.'
            pass

    ## Determine max # of top-level streams based on per cycle limit
        print '   Maximum streams per cycle = ',self.maxStreamsPerCycle
        if num2submit > self.maxStreamsPerCycle:
            num2submit = self.maxStreamsPerCycle
            print '%% Limiting: only ',num2submit,' top-level streams per cycle allowed'
            pass

        print 'Final number of top-level streams to submit this cycle = ',num2submit

        


## FUTURE TO-DO: maintain dynamic calculation of how many substreams derive from single top-level stream
##     ## Step 3: Determine current load
##     setupInPipe = numSetupRun[1]+numSetupRun[2]+numSetupRun[3]
##     processInPipe = processClump[1]+processClump[2]+processClump[3]
##     mergeInPipe = mergeClumps[2]+ mergeClumps[3]

##     ## Step 3.1: Calculate the average number of sub-streams per top-level stream
##     if numSetupRun[0]>0:
##         clumpsPerStream = float(processClump[0])/numSetupRun[0]
##     else:
##         print '%WARNING: Data from pipeline server is suspicious - kludging around problem...'
##         clumpsPerStream = 100000000
##         pass
##     print 'active processClump = ',processInPipe,' (max allowed = ',maxProcessClumps,')'
##     print 'avg number of clumps per stream = ',clumpsPerStream
##     print 'active mergeClumps = ',mergeInPipe,' (max allowed = ',maxMergeClumps,')'

        sys.stdout.flush()
        return (num2submit,max2submit)






    def run(self):
## run trickleStream


        cycle = 0
        totSub = 0
        lastcycles = [-2,-2,-2,-2,-2,-2]    #last 6 cycles of submittals (~ 1 hour)
        cycleindex = 0

        reproStats = stats(depth=10)
        self.dumpParms()

        while 1:
            if os.path.exists("./stop"):
                print "User requested stop (eponymously named file in working directory)"
                sys.exit(0)
                pass
            cycle += 1
            now = datetime.datetime.now()
            print '\n\n  Begin cycle ',cycle,' at ',now
            sys.stdout.flush()

            ## Calculate number of top-level streams to create
            (num2submit,remaining) = self.num2sub()
            sys.stdout.flush()

            if self.chatter: print 'Number to submit = ',num2submit,', number remaining = ',remaining
            ts = datetime.datetime.now()
            print '[',ts,']'
            sys.stdout.flush()

            ## Then, declare victory or create some streams or wait awhile
            if num2submit == 0:
                print '\n\nALL DONE.'
                sys.exit(0)
            elif num2submit > 0:
                cmd = self.pipelineCmd+' createStream --nStreams '+str(num2submit)+' '+self.task
                print cmd
                sys.stdout.flush()
                if self.dryRun:
                    print '%%WARNING: Dry Run - no pipeline streams created'
                else:
                    os.system(cmd)
                    pass
                ts = datetime.datetime.now()
                print '[',ts,']'
                sys.stdout.flush()
            else:
                print "Too many processes running."
                pass

            ## Generate statistics
            reproStats.update(num2submit,now,remaining)

            ## Continue or bail?
            if self.maxCycles > 0 and cycle >= self.maxCycles:
                print 'Reached maximum cycle limit of ',self.maxCycles,', quitting...'
                sys.exit(0)
            elif num2submit == 0:
                print '\n\nALL DONE!'
                sys.exit(0)
                pass

            
            ## Sleep until next cycle
            print "Sleeping for ",self.timePerCycle,' seconds @ ',datetime.datetime.now()
            print '...'
            sys.stdout.flush()
            time.sleep(self.timePerCycle)
            pass
        return

###############  end class trickle
