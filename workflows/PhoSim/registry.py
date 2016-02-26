#!/usr/bin/env python
#
# registry.py - python wrapper to dataCatalog RESTful interface
#
"""
Registry is a class that wraps a subset of the SRS DataCatalog RESTful client interface.
It offers these advantages over the raw interface:
1. Sets up authentication (using my personal credentials)
2. Sensibly handles exceptions
3. Provides a simple way to register/add location/recrawl datasets
4. Can print out a summary of interesting metadata for a specified dataset
"""
#-------------------------------------------------------------------------

import os,sys
import subprocess,shlex
import datetime

##################################################################
#######
##################################################################

class registry(object):

    def __init__(self,debug=False,dryrun=False):
        ## INITIALIZE REGISTRY OBJECT
        ## Debugging/Development options
        self.debug = debug      ## True enable debug output
        self.quiet = False     ## True disables routine output
        self.dryrun = dryrun

        ## RESTful interface to dataCatalog
        self.dcVer = 'dev/0.4'       ## version of datacatalog software to use
        self.dcVersion = None
        self.client = None

        ## Controls
        self.addLoc = True       ## Add new location (site), if necessary
        self.reCrawl = True      ## Flag a reCrawl, if appropriate
        self.abortOnException = False   # dataCatalog Restful interface errors

        ## DataCatalog metadata
        self.filetypeMap = {'fits':'fits','fit':'fits','root':'root','txt':'txt','jpg':'jpg','png':'png','pdf':'pdf','html':'html','htm':'html','xls':'xls','lims':'lims'}
        self.dryRunList = ['create_dataset','patch_dataset','mkdir','mkloc']

        ## Statistics
        self.numNewFolders = 0
        self.numRegistered = 0
        self.numAlreadyRegistered = 0
        self.numAddLocs = 0
        self.numReCrawl = 0
        self.numExceptions = 0
        return


    def init(self):
        """initialize the RESTful interface to the dataCatalog"""
        if self.client != None: return
        print 'Initializing RESTful dataCatalog interface'
        dc1 = '/afs/slac.stanford.edu/u/gl/srs/datacat/'+self.dcVer+'/lib'
        sys.path.append(dc1)
 
        import datacat
        config_path = os.path.join(os.getenv('DATACAT_CONFIG','/nfs/farm/g/lsst/u1/software/datacat'),'config.cfg')
        self.dcVersion = datacat.__version__
        self.client = datacat.client_from_config_file(config_path)

        return


    def dumpConfig(self):
        """Diagnostic print of class configuration"""
        print '\n Registry configuration:'
        print 'dcVersion = ',self.dcVersion
        if self.client == None:
            print 'RESTful interface has not been initialized'
        else:
            print 'RESTful interface ready to go.'
            pass
        print 'Add new location, if needed    ',self.addLoc
        print 'Flag a recrawl, if needed      ',self.reCrawl
        print 'Abort on exception             ',self.abortOnException
        print 'Debug flag                     ',self.debug
        print 'Dryrun flag                    ',self.dryrun
        print
        return


    def dumpStats(self):
        """Print dataCatalog registration summary statistics"""
        print '\n DataCatalog registration summary statistics:'
        print 'Number of new folders             = ',self.numNewFolders
        print 'Number of datasets registered     = ',self.numRegistered
        print 'Number of datasets not registered = ',self.numAlreadyRegistered
        print 'Number of added locations         = ',self.numAddLocs
        print 'Number of re-crawl requests       = ',self.numReCrawl
        print 'Number of exceptions encountered  = ',self.numExceptions
        print
        return

        

    def doDC(self, method, *args, **kwargs):
        """
      Execute a single RESTful dataCatalog interface method, ** with exception handling **
      RESTful client methods available to doDC():
         exists()         check if dataset or folder exists
         mkdir()          create dataCatalog folder(s)
         create_dataset() register dataset in dataCatalog
         path()           fetch metadata for dataset or folder
         mkloc()          add a new location (site) for dataset
         patch_dataset()  update metadata for dataset
      """
        cname = method.im_class.__name__
        fname = method.im_func.__name__
        mname = cname+'.'+fname
        if self.debug: print 'Entering doDC',mname,',',args,',',kwargs
        if not fname in self.dryRunList or not self.dryrun:
            try:
                return method(*args, **kwargs)
            except Exception as e:
                ekeys = e.__dict__.keys()
                self.numExceptions += 1
                print '\n%Exception in ',mname
                for key in ekeys:
                    if key == 'raw': continue
                    print ' ',key,': ',getattr(e,key)
                    pass
                if self.abortOnException: raise Exception(e)
                rc = 1
                pass
        else:
            print '\n***Dry run'
            return
        pass


    def register(self,fn,dcFolder,site,fType,dType,metaData={}):
        """
        Register a single file in the dataCatalog
         fn = fully-qualified path/filename.ext of file to register
         dcFolder = dataCatalog folder to hold dataset
         site = location of file, e.g., BNL, slac, slac.lca.archive
         fType = file type (ennumerated set defined in dataCatalog)
         dType = data type (ennumerated set defined in dataCatalog)
         metaData = [optional] dict of metadata to be stored with dataset
        
         A request to register a file in the dataCatalog may have one of these effects:
           1) fresh registration with one site + crawl
           2) add new location + crawl
           3) recrawl  (for existing registration being updated because file has changed)
        NOTE: 'crawl' currently only works at SLAC
        """
        
        if not self.quiet: print '\n** registry.register: ',fn

        addLoc = False
        reCrawl = False
        crawlSite = False
        if site.startswith('slac') or site.startswith('SLAC'):crawlSite = True


        ## Verify RESTful interface is ready to go
        if self.client == None:
            self.init()
            pass

        ## Use filename as dataset name
        if dcFolder.endswith('/'): dcFolder = dcFolder.rstrip('/')
        datasetName = os.path.basename(fn)
        dcLoc = os.path.join(dcFolder,datasetName)
        if self.debug:
            print 'dcFolder = ',dcFolder
            print 'datasetName = ',datasetName
            print 'dcLoc = ',dcLoc
            pass
        


        ## Create target dataCatalog folder, if necessary, then perform fresh registration
        if not self.doDC(self.client.exists, dcFolder):
            if self.debug or not self.quiet: print 'Create folder and register.'
            self.doDC(self.client.mkdir, dcFolder, parents=True)
            self.numNewFolders += 1
            self.doDC(self.client.create_dataset, dcFolder, datasetName, dType, fType, site=site, resource=fn, versionMetadata=metaData)
            self.numRegistered += 1
            return


        ## Folder already exists, decide how to handle this registration request
        if not self.doDC(self.client.exists, dcLoc):
            if self.debug or not self.quiet: print 'File not previously registered: fresh registration'
            self.doDC(self.client.create_dataset, dcFolder, datasetName, dType, fType, site=site, resource=fn, versionMetadata=metaData)
            self.numRegistered += 1
        else:
            if self.debug: print 'File already registered'
            self.numAlreadyRegistered += 1
            ds = self.doDC(self.client.path, dcLoc, site='all')
            if self.debug: print 'ds = ',ds
            if self.debug: print 'ds.__dict__.keys() = ',ds.__dict__.keys()
            if 'site' in ds.__dict__.keys():
                ## Single site already defined for this dataset
                if self.debug: print 'Single site already defined: ',ds.site
                if not ds.site == site:
                    addLoc = True
                else:
                    if crawlSite: reCrawl = True
                    pass
            elif 'locations' in ds.__dict__.keys():
                ## Multiple sites already defined for this dataset
                if self.debug: print 'Multiple sites already defined.'
                locList = ds.locations
                found = False
                for loc in locList:
                    if loc.name == site:
                        if crawlSite: reCrawl = True              # slac already registered
                        found = True
                        pass
                    pass
                if not found:
                    addLoc = True         # slac not registered
                    if crawlSite: reCrawl = True
            else:
                print '%ERROR: Expected metadata not present in object returned from client.path()'
                print 'ds = ',ds
                sys.exit(1)
                pass
                
            if self.debug:
                print 'addLoc  = ',addLoc
                print 'reCrawl = ',reCrawl
                pass

            if addLoc:
                ## Add a new location (site) for this dataset
                if self.debug or not self.quiet: print 'Adding location ',site
                self.doDC(self.client.mkloc, dcLoc, site=site, resource=fn)
                self.numAddLocs += 1
                pass
            
            if reCrawl:
                ## Request dataset be reprocessed by the crawler
                if self.debug or not self.quiet: print 'Requesting reCrawl'
                patch_dict = {"scanStatus":"UNSCANNED"}
                self.doDC(self.client.patch_dataset, dcLoc, patch_dict, site=site)
                self.numReCrawl += 1
                pass
            pass
        return


    def inspect(self,dataset):
        """Extract and print information about the specified dataset in the dataCatalog"""
        print 'Inspecting dataset: ',dataset

        dsList = ['dataType','fileFormat','created','master','scanned','site','path','name','locationCreated','resource','size','scanStatus']
        locList = ['site','resource','scanStatus','scanned','size']
        if not self.doDC(self.client.exists, dataset):
            print 'Specified dataset does not exist in the dataCatalog'
            return

        ## Fetch metadata
        ds = self.doDC(self.client.path, dataset, site='all')
        #print 'dir(ds) = ',dir(ds)

        ## Print out selected metadata (see dsList and locList)
        dlist = ds.__dict__.keys()
        dlist.sort()
        if 'locations' not in dlist: print 'Single location'
        for d in dlist:
            if d in dsList: print d,' = ',ds.__dict__[d]
            pass
        ##  The following only for datasets with multiple locations registered
        if 'locations' in dlist:
            print 'Multiple locations'
            for n in range(len(ds.locations)):
                print '* Location ',n
                klist = ds.locations[n].__dict__.keys()
                klist.sort()
                for k in klist:
                    if k in locList: print '  ',k,' = ',ds.locations[n].__dict__[k]
                    pass
                pass
            pass
        pass

        ## Done.
        return
