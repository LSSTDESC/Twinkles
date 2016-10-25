#!/bin/bash

## phoSimPrep.sh - set up environment to run phoSimPrep.py
#set -x
echo
echo "============================================================================================="
echo
echo "Entering phoSimPrep.sh"
dir=`dirname $(readlink -f $0)`
echo "dir = "$dir

echo "Setup system updates"
#/usr/bin/scl enable devtoolset-3 bash
#/usr/bin/scl enable devtoolset-3
source /opt/rh/devtoolset-3/enable
rc1=$?
if [ $rc1 != 0 ]; then
    echo "ERROR: cannot set system updates, rc = "$rc1
    exit $rc1
fi

echo "Setup Twinkles environment"
## source /nfs/farm/g/desc/u1/twinkles/setup.sh      ##### PRODUCTION
source $TW_ROOT/newICgen/setup.sh                 ##### DEVELOPMENT/TESTING/DEBUGGING


## Redefine $HOME to prevent contention of /u/lt/lsstsim
cp -prv $HOME/.lsst $PWD
export HOME_ORIGINAL=$HOME
export HOME=$PWD
echo "Listing of HOME = "$HOME" :"
ls -ltraF

echo
echo "===> Call phoSimPrep.py"
$dir/phoSimPrep.py
rc=$?


# Exit with phoSimPrep.py exit code
exit $rc
