#!/bin/bash

## phoSimPrep.sh - set up environment to run phoSimPrep.py
#set -x
echo
echo "============================================================================================="
echo
echo "Entering phoSimPrep.sh"
date
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
cmd="/nfs/farm/g/desc/u1/software/redhat6-x86_64-64bit-devtoolset-3/setup.sh"
##cmd=" $TW_CONFIGDIR/helpers/TWsetup.sh"
##source /nfs/farm/g/desc/u1/twinkles/setup.sh
echo "source "$cmd
source $cmd

echo "Return from setup, rc = " $?

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


