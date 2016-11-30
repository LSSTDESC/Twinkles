#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## setupPhoSimInput.py - Set up instance catalog and SED files for a
## run of phoSim, along with a work directory

##
##  Required env-vars
## TW_ROOT
## TW_CONFIGDIR
## TW_ICFILE
## TW_SIXDIGSTREAM

import os,sys,shutil
import argparse
import scratch
trace = True

class setupPhoSimInput(object):
    def __init__(self,icFile=None):
        self.debug = True
        self.projectName = 'LSSTSIM'
        self.icFile = icFile
        self.inputRoot = ''
        self.phosimInstDir = ''
        
        self.refCF = None   ## Reference copy of the phoSim command file (physics overrides)
        
        self.SEDlib = ''      ## Reference copy of the production SEDs for phoSim
        self.sedFile = None   ## tar file containing custom SEDs for this visit
        self.specialSEDdir = 'spectra_files'   ## name of directory to contain custom SEDs
        self.locSpecialSEDs = None  ## full path to (unpacked) custom SED files

        self.scratchObj = scratch.scratch()  ## Create a scratch object
        self.scratch = None             ## high-performance I/O scratch space (if possible)
        self.scratches = ['/scratch']   ## list of scratch candidates
#        self.scratches = ['/lustre/ki/pfs/fermi_scratch','/scratch','/tmp']

        self.persistentScratch = False  ## Will the scratch area persist after this task step?
        self.cleanupFlag = True         ## True => erase scratch directory at end of task

        ## "local" files and directories used directly by phoSim
        self.locIC = None    ## full path to uncompressed instanceCatalog
        self.locCF = None    ## full path to command file for batch running
        self.locSEDs = None  ## full path to complete SED directory tree (production + custom)
        self.locWork = None  ## full path to (scratch) /work directory
        
        self.checkpoint = False    ## is checkpointing active?
        self.lastCP = None  ## which checkpoint was performed
        self.nextCP = None  ## which checkpoint will be performed
        self.reqCP = None
        self.archiveWorkDir = None    ## location of checkpoint files
        return



    def getScratch(self):
        ## Set up scratch space
        self.scratch = self.scratchObj.getScratch()
        self.scratchObj.statScratch()
        
        ## Create phoSim 'work' directory in scratch area
        self.locWork = os.path.join(self.scratch,'work')
        if not os.access(self.locWork,os.W_OK):os.makedirs(self.locWork,0o3755)
        return



    def protectScratch(self):
        ## Protect scratch directory and everything in it: rwxr-sr-t
        if trace: print 'Entering protectScratch().'
        cmd = 'chmod -R 3755 '+self.scratch
        print 'Protect scratch directory\n',cmd

        rc = os.system(cmd)
        if rc != 0:
            print "%ERROR: unable to execute command, ",cmd
            sys.exit(1)
        return



    def getSEDfromIC(self,ic):
        ## Construct SED file name from instanceCatalog file name IC
        ## and SED file names should be identical except one is txt.gz
        ## and the other tar.gz.  Example: phosim_input_1000185.txt.gz
        ## This is the UW convention for Twinkles 1, Run 1 (Feb 2016)
        if trace: print 'Entering getSEDfromIC(',ic,').'
            
        icx = ic.split('.')
        icSuffix = icx[-2]+'.'+icx[-1]
        if icx[-2]=='txt' and icx[-1]=='gz':
            sedname = ''.join(icx[:-2])
        else:
            print 'Illegal instance catalog name: ',ic
            sys.exit(1)

        sed = sedname+'.tar.gz'
        return sed

    def prepInputs(self):
        ## Check file integrity
        if trace: print 'Entering prepInputs()'

        ## Confirm command file is available
        print 'refCF  = ',self.refCF
        if not os.access(self.refCF,os.R_OK):
            print 'Unable to access command file:'
            print self.refCF
            sys.exit(1)
            pass

        ## copy command file to $PWD
        fdest = os.environ['PWD']
        self.locCF = os.path.join(fdest,os.path.basename(self.refCF))
        cmd = 'cp '+self.refCF+' '+self.locCF
        print 'cmd = ',cmd
        rc = os.system(cmd)
        if rc != 0: sys.exit(1)

        ## Confirm instanceCatalog is available
        icFull = os.path.join(self.inputRoot,self.icFile)
        print 'icFull  = ',icFull
        if not os.access(icFull,os.R_OK):
            print 'Unable to access instance catalog:'
            print icFull
            sys.exit(1)
            pass

        ## copy instance catalog to scratch and uncompress, if necessary
        if self.persistentScratch:
            self.locIC = icFull
        else:
            if self.icFile.endswith(".gz"):
                self.locIC = os.path.join(self.scratch,os.path.splitext(self.icFile)[0])
                cmd = 'zcat '+icFull+' > '+self.locIC
            else:
                self.locIC = os.path.join(self.scratch,self.icFile)
                cmd = 'cat '+icFull+' > '+self.locIC
                pass
            print 'cmd = ',cmd
            rc = os.system(cmd)
            if rc != 0:
                print "ERROR: attempting to copy instance catalog to scratch"
                sys.exit(1)
                pass
            pass


        ## if specialSEDdir already exists in scratch, it was dymically generated
        if os.access(os.path.join(self.scratch,self.specialSEDdir),os.R_OK):
            self.locSpecialSEDs = os.path.join(self.scratch,self.specialSEDdir)
            pass

        ## Otherwise, check if auxiliary SED file (.tar.gz) was specified
        elif self.sedFile != None:
            sedFull = os.path.join(self.inputRoot,self.sedFile)
            print 'sedFull = ',sedFull
            if not os.access(sedFull,os.R_OK):
                print 'Unable to access auxiliary SED file tarball:'
                print sedFull
                sys.exit(1)
                pass
        ## copy SED files (uncompress and untar) to scratch
        ##### NOTE: by convention, tarball contains a single 'spectra_files' directory
            self.locSpecialSEDs = os.path.join(self.scratch,self.specialSEDdir)
            cmd = 'tar -C '+self.scratch+' -xf '+sedFull
            print 'cmd = ',cmd
            rc = os.system(cmd)
            if rc != 0: sys.exit(1)
            pass
        
        return

    def makeSEDtree(self):
        ## Create sym-link directory tree of phoSim SEDs
        if trace: print 'Entering makeSEDtree().'

        self.locSEDs = os.path.join(self.scratch,'SEDs')

        if os.path.isdir(self.locSEDs):     ## Remove old sym links to SED files, if present
            print "Working copy of SEDs already exists: ",self.locSEDs
            print "Removing old copy..."
            shutil.rmtree(self.locSEDs)
            pass

        print 'Create sym links to production SED files'
        cmd = 'cp -as '+self.SEDlib+' '+self.locSEDs
        print 'cmd = ',cmd
        rc = os.system(cmd)
        if rc != 0: sys.exit(1)

        ## Change SEDs directory permissions
        cmd = 'chmod -R 3755 '+self.locSEDs
        print 'cmd = ',cmd
        rc = os.system(cmd)
        if rc != 0: sys.exit(1)

        ## Add link to special SEDs for just this run
        if self.locSpecialSEDs != None and not os.path.islink(self.locSpecialSEDs):
            print 'Create sym link to custom SED file directory'
            os.symlink(self.locSpecialSEDs,os.path.join(self.locSEDs,self.specialSEDdir))
            pass
        
        return

    def cpPrep(self,workdir):
        ## Assess checkpoint situation and prepare to resume after CP, if necessary
        ##   Checkpointing is considered "active" if either of two conditions hold:
        ##     1) An existing 'work' directory is discovered containing ckpt files, or
        ##     2) The checkpoint directives are present in the command file
        
        if workdir == self.locWork: return  ## no CP in progress
        self.archiveWorkDir = workdir

        ## Look into the supplied workdir for signs of checkpointing
        ##  files will have the forms: foo_ckptdt_N.fits.gz and
        ##  foo_ckptfp_N.fits.gz

        lastCP = -1
        flist = os.listdir(workdir)
        for file in flist:
            if file.endswith('.fits.gz') and file.find('ckpt') != -1:
                ## Determine the last completed checkpoint sequence number
                self.checkpoint = True
                numCP = int(os.path.splitext(os.path.splitext(file)[0])[0].split('_')[-1])
                if numCP > lastCP: lastCP = numCP
                pass
            pass
        if self.checkpoint:
            print 'The last completed checkpoint was: ',lastCP
        else:
            print 'There is no checkpoint history for this run'
            pass
        nextCP = lastCP + 1
        self.lastCP = lastCP
        self.nextCP = nextCP
        
        ## Copy the checkpoint files (and anything else) into the
        ## scratch/work directory which is both new and empty
        for file in flist:
            if not file.endswith(".fits.gz"):continue
            fullFile = os.path.join(workdir,file)
            shutil.copy(fullFile,self.locWork)
            pass

        ## Modify the phoSim command file to correctly perform the
        ## appropriate checkpoint
        fin = open(self.locCF,'r')
        tmpFile = self.locCF+'.tmp'
        fout = open(tmpFile,'w')
        lines = fin.readlines()
        for line in lines:
            if line.startswith('checkpointtotal'):
                self.checkpoint = True
                self.reqCP = line.strip().split()[-1]
                print 'Final checkpoint requested = ',self.reqCP
                pass
            elif line.startswith('checkpointcount'):
                nline = line.replace('%',str(self.nextCP),1)
                print 'original line = ',line.strip()
                print 'new line      = ',nline.strip()
                line = nline
                pass
            fout.write(line)
            pass
        fin.close()
        fout.close()
        print 'Updated command file created'
        shutil.move(tmpFile,self.locCF)
        print 'Working command file replaced'
            
        return

    def clean(self):
        ## Cleanup the 'scratch' space
        if trace: print 'Entering cleanup().'
        os.system('echo clean;ls -l '+self.scratch)    ##### DEBUG
        ## But first, if checkpointing active, preserve ckpt files in archiveWork
        if self.checkpoint and self.archiveWorkDir != None:
            print 'Sleep(30) to kludge around file system race condition'
            os.system('sleep 30')
            print 'Archive checkpoint files in /work dir'
            sFiles = os.listdir(self.locWork)
            aFiles = os.listdir(self.archiveWorkDir)
            for sFile in sFiles:
                if sFile not in aFiles and os.path.exists(sFile): shutil.copy2(sFile,self.archiveWorkDir)
                pass
        ## Now obliterate the scratch space
        if self.cleanupFlag:
            print "Cleaning up scratch area"
            self.scratchObj.cleanScratch()
            #shutil.rmtree(self.scratch)
        else:
            print "Retaining scratch area"
            pass
        return

    def run(self):
        ## TWINKLES: Run through all steps to prepare phoSim inputs and return resultant paths
        if trace: print 'Entering Run()'
        self.getScratch()
        #os.system('echo checkpoint1;ls -l '+self.scratch)    ##### DEBUG

        self.prepInputs()
        #os.system('echo checkpoint2;ls -l '+self.scratch)    ##### DEBUG

        self.makeSEDtree()
        os.system('echo checkpoint3;ls -l '+self.scratch)    ##### DEBUG

        self.protectScratch()
        os.system('echo checkpoint4;ls -l '+self.scratch)    ##### DEBUG
        return(self.locWork,self.locIC,self.locSEDs,self.locCF)

    def run2(self):
        ## DEEP: Run through all steps to prepare phoSim inputs and return resultant paths
        if trace: print 'Entering Run()'
        self.getScratch()
        #        self.sedFile = self.getSEDfromIC(self.icFile)
        self.prepInputs()
        self.makeSEDtree()
        return(self.locWork,self.locIC,self.locSEDs,self.locCF)

    def dump(self):
        print '\n--> Dump setupPhoSimInput data:'
        print 'inputRoot      = ',self.inputRoot
        print 'icFile         = ',self.icFile
        print 'sedFile        = ',self.sedFile
        print 'scratches      = ',self.scratches
        print 'scratch        = ',self.scratch
        print 'specialSEDdir  = ',self.specialSEDdir
        print ' ***** RESULTS'
        print 'locWork        = ',self.locWork
        print 'locIC          = ',self.locIC
        print 'locSEDs        = ',self.locSEDs
        print 'locCF          = ',self.locCF
        print ' ***** REFERENCE'
        print 'locSpecialSEDs = ',self.locSpecialSEDs
        print 'phosimInstDir  = ',self.phosimInstDir
        print 'SEDlib         = ',self.SEDlib
        print 'refCF          = ',self.refCF
        print ' ***** CHECKPOINTS'
        print 'checkpoint     = ',self.checkpoint
        print 'reqCP          = ',self.reqCP
        print 'lastCP         = ',self.lastCP
        print 'nextCP         = ',self.nextCP
        print 'archiveWorkDir    = ',self.archiveWorkDir
        print ' ***** MISCELLANEOUS'
        print 'cleanupFlag    = ',self.cleanupFlag
        print '---------------\n'
        return

if __name__ == '__main__':
    print 'main program!'
    prep = setupPhoSimInput('phosim_input_1000185.txt.gz')
    prep.dump()
    (work,ic,seds) = prep.run()
    print 'Return from prep.run:'
    print ' work = ',work
    print '   ic = ',ic
    print ' seds = ',seds


    ## end
    #    prep.clean()
    prep.dump()
    sys.exit()
