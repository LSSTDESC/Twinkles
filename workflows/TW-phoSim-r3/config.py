## config.py - Configuration data common to multiple task scripts.

## This config assumes the context of a running Pipeline Task (i.e.,
## the availability of certain env-vars)

import sys,os

## Setup logging, python style
import logging as log
log.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s in %(filename)s line %(lineno)s: %(message)s', level=log.INFO)

## For archiving old working directories
archivesDirName = 'archives'
phoSimOutputRoot = 'phosim_output'
#filePermissions = 0o2775     #   rwxrwsr-x
filePermissions = 0o3755     #   rwxr-sr-t

## Somewhere here should be code to detect architecture and set $ARCH
ARCH = 'redhat6-x86_64-64bit-gcc44'

## phoSim installation
PHOSIMINST = os.path.join('/nfs/farm/g/lsst/u1/software',ARCH,'phoSim/3.5.3')

## phoSim input (instance catalogs and SED files)
PHOSIMIN = '/nfs/farm/g/desc/u1/data/Twinkles/phoSim/Run1_InstCats_SEDs'
## os.path.join(os.environ['TW_ROOT'],'phosim_input','20160219')

## phoSim visit list (obsHistIDs)
PHOSIMVL = os.path.join(os.environ['TW_CONFIGDIR'],'twinkles_visits.txt')

## phoSim instance catalog list
PHOSIMICMODE = 'dynamic'   ## use generatePhosimInputs.py to generate IC/SED filess in real-time
#PHOSIMICMODE = 'static'    ## select from a list of pre-defined IC/SED files
PHOSIMICL = os.path.join(os.environ['TW_CONFIGDIR'],'instanceCatalogList.txt')

## phoSim sensor list
PHOSIMSL = os.path.join(os.environ['TW_CONFIGDIR'],'sensorList.txt')

## phoSim physics override (aka "command") file (template)
PHOSIMCF = os.path.join(os.environ['TW_CONFIGDIR'],'phoSim_commands.txt')

########### CHECKPOINTING ##############
## Number of phoSim "internal checkpoints" to produce
PHOSIMCPMAX = 0

## Max time (seconds) per dmtcp checkpoint
CPMAXTIME = 86400     ## 24 hours
########### /CHECKPOINTING ##############

## phoSim opts
#PHOSIMOPTS=' -s R22_S11 '
#PHOSIMOPTS=' -s R01_S11 '
PHOSIMOPTS=' -e 0 '   ## eliminate the 'amplifier' output files from phoSim

## phoSim output (both "output" and "work" areas - /work used only as archive between checkpoints)
PHOSIMOUT = os.path.join(os.environ['TW_ROOT'],'phosim_output')

## phoSim (persistent) scratch space directory path
##    SLAC:  /lustre/ki/pfs/fermi_scratch/lsst/<task>/<subtask>/<stream>/<substream>
PHOSIMSCRATCH = os.path.join('/lustre/ki/pfs/fermi_scratch/lsst',os.environ['PIPELINE_TASKPATH'].replace('.','/'),os.environ['PIPELINE_STREAMPATH'].replace('.','/'))

PHOSIMCLEANUP = True

## SED files (from DM stack)
PHOSIMSEDS = '/lustre/ki/pfs/fermi_scratch/lsst/phosim/sims_sed_library'

#SEDLIB = '/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/DMstack/v12_0/opt/lsst/sims_sed_library'

## Twinkles UW-FATBOY cache location
TW_CACHEDIR = '/nfs/farm/g/desc/u1/data/Twinkles/fatboy_caches'
TW_OPSSIMDIR = '/nfs/farm/g/desc/u1/data/Twinkles'

## Location of Twinkles git project and binary for instanceCatalog generation
#TWINKLES_ROOT = '/nfs/farm/g/desc/u1/software/redhat6-x86_64-64bit-devtoolset-3/Twinkles/...........'
#TWINKLES_ROOT = os.path.join(os.getenv('TW_ROOT'),'Twinkles.master')
TWINKLES_ROOT = '/nfs/farm/g/desc/u1/software/redhat6-x86_64-64bit-devtoolset-3/Twinkles/prod'
TWINKLES_BIN = TWINKLES_ROOT+'/bin'

