## config.py - Configuration data common to multiple task scripts.

import sys,os

## Somewhere here should be code to detect architecture and set $ARCH
ARCH = 'redhat6-x86_64-64bit-gcc44'

## phoSim installation
#PHOSIMINST=/afs/slac/g/lsst/software/redhat6-x86_64-64bit-gcc44/phoSim/phosim-3.3.2
PHOSIMINST = os.path.join('/nfs/farm/g/lsst/u1/software',ARCH,'phoSim/3.4.2')

## phoSim instance catalog list
PHOSIMICL = os.path.join(os.environ['TW_CONFIGDIR'],'instanceCatalogList.txt')

## phoSim output
PHOSIMOUT = os.path.join(os.environ['TW_ROOT'],'phosim_output')

## phoSim work
PHOSIMWORK = os.path.join(os.environ['TW_ROOT'],'phosim_work')

## phoSim input (instance catalogs)
PHOSIMIN = os.path.join(os.environ['TW_ROOT'],'phosim_input')

## phoSim 3.4.2 env-var setup
PHOSIMSETUP = {'CCP':'g++','CCS':'g++','CFIODIR':'/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/externals/cfitsio/3.370/lib/','CFIO_INC_DIR':'/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/externals/cfitsio/3.370/include/','FFTW3_DIR':'/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/externals/fftw/fftw-3.3.4/lib/','FFTW3_INC_DIR':'/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/externals/fftw/fftw-3.3.4/include/'}
