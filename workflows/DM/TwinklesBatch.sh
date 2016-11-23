#!/bin/bash

ulimit -c ${CORE_LIMIT:-1000} # Limit core dump
set -e # exit on error

# Set up a unique work directory for this pipeline stream
stream=$(echo $PIPELINE_STREAMPATH | cut -f1 -d.)
export WORK_DIR=${OUTPUT_DATA_DIR}/work/${stream}
# Only set IN_DIR and OUT_DIR if not already set
export OUT_DIR=${OUT_DIR:-${WORK_DIR}/output}
export IN_DIR=${IN_DIR:-${WORK_DIR}/input}

# Workaround for EUPS trying to write to home directory
export HOME=`pwd`

# Workaround for low level libraries such as OpenBLAS allocating many threads
export OMP_NUM_THREADS=1 

# Test which version of RHEL we are using
majversion=$(lsb_release -rs | cut -f1 -d.)

export SCRIPT=${SCRIPT_LOCATION}/${PIPELINE_PROCESS:-$1}

# Set up Twinkles environment and invoke process specific script
# If DM already set up then no need to do it again
if [ -v LSST_HOME ]
then
set -xe; export SHELLOPTS; source ${SCRIPT} 
elif [ $majversion -eq 6 ] 
then
scl enable devtoolset-3 'source ${DM_DIR}/${DM_SETUP}; set -xe; export SHELLOPTS; source ${SCRIPT}'
else
source ${DM_DIR}/${DM_SETUP}; set -xe; export SHELLOPTS; source ${SCRIPT}
fi
