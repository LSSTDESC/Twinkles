#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## scratch.py - Manage local /scratch space


import os,sys,shutil,socket

class scratch(object):
    def __init__(self):
        self.scratch = None
        self.prefix = 'LSSTSIM'
        self.scratches = ['/scratch']
        self.scrMode = 0o3755
        self.cleanupFlag = True
        self.host = socket.gethostname()
        self.trace = False
        return

    def getScratch(self):
    ## Set up scratch space
        if self.trace: print 'Entering getScratch().'
        if self.scratch == None:
            scratchRoot = ''
            for scratch in self.scratches:
                if os.path.isdir(scratch):
                    scratchRoot = scratch
                    break
                pass

            if scratchRoot == '':
                print "Unable to find suitable scratch space."
                print self.scratches
                sys.exit(1)

            ## Define scratch directory
            ##  Naming convention for scratch directories:
            ##    Standalone job:     /scratch/PID-<processID>
            ##    Ordinary batch job: /scratch/LSF-<jobID>
            ##    Pipeline batch job: /scratch/LSSTSIM/<taskName>/<subtaskName>/<StreamNum>/<jobID>
            ##  Naming convention for scratch directories:
            jobid = os.path.join(self.prefix,'PID-'+str(os.getpid()))
            if os.environ.get('LSB_JOBID') != None:
                jobid=os.path.join(self.prefix,'LSF-'+os.environ['LSB_JOBID'])
                if os.environ.get('PIPELINE_TASKPATH') != None:
                    jobid = os.path.join(self.prefix,os.environ.get('PIPELINE_TASKPATH').replace('.','/'),os.environ.get('PIPELINE_STREAMPATH').split('.')[0],os.environ.get('LSB_JOBID'))
                    pass
                pass
            
            self.scratch = os.path.join(scratchRoot,str(jobid))
            print 'defined self.scratch = ',self.scratch

            ## Create scratch directory
            if os.path.exists(self.scratch):
                print 'WARNING: scratch directory already exists.  Removing...'
                shutil.rmtree(self.scratch)
                pass
            os.makedirs(self.scratch,self.scrMode)
            pass
        else:
            print 'WARNING: scratch already defined - ',self.scratch
            pass
            
        return self.scratch

    
    def cleanScratch(self):
        ## Cleanup the 'scratch' space
        if self.trace: print 'Entering cleanScratch().'

        if self.scratch != None:
            ## Now obliterate the scratch space
            if self.cleanupFlag:
                print "Cleaning up scratch area"
                shutil.rmtree(self.scratch)
                self.scratch = None
            else:
                print "Retaining scratch area"
                pass
            pass
        return

    def statScratch(self):
        print '\n\n====================================================='
        print 'Status of scratch space'
        print ' scratch     = ',self.scratch
        print ' prefix      = ',self.prefix
        print ' scratches   = ',self.scratches
        print ' scrMode     = ',oct(self.scrMode)
        print ' host        = ',self.host
        print ' cleanupFlag = ',self.cleanupFlag
        print ' trace       = ',self.trace
        print '=======================================================\n\n'
        return
