#!/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.3.0/bin/python

## findSED.py - parse instance catalog and verify all needed SED files are available

import os,sys,shutil,gzip

## Locate Instance Catalog
ICroot = '/nfs/farm/g/desc/u1/Pipeline-tasks/Twinkles-phoSim/phosim_input/20160219'
ICfile = 'phosim_input_484933.txt.gz'

IC = os.path.join(ICroot,ICfile)

## Locate SED files
SEDroot = '/nfs/farm/g/desc/u1/Pipeline-tasks/Twinkles-phoSim/SEDs/2016.01.26'

## Open IC and read

nlines = 0
nSEDs = 0
goodSEDs = 0
badSEDs = 0

print 'Using instance catalog:\n\t',IC
print 'Scanning for SED files in ',SEDroot
sys.stdout.write('Starting scan')
sys.stdout.flush()

with gzip.open(IC,'rb') as f:
    for line in f:
        nlines += 1
        if nlines%10000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
            pass
        if line.startswith('object '):
            nSEDs += 1
            parts = line.split()
            SEDfile = parts[5]
            SED = os.path.join(SEDroot,SEDfile)
            if os.access(SED,os.R_OK):
                #print "okay ",SEDfile
                goodSEDs += 1
            else:
                print "bad! ",SEDfile
                badSEDs += 1
                pass
            
            pass
        pass
    pass




print '\n\n\nSummary:'
print 'Read instance catalog: ',IC
print 'Total lines      = ',nlines
print 'Total SEDs       = ',nSEDs
print 'Total good SEDs  = ',goodSEDs
print 'Total bad SEDs   = ',badSEDs

sys.exit(0)
