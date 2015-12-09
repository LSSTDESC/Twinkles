#!/bin/bash

ulimit -c ${CORE_LIMIT:-1000} # Limit core dump
set -e # exit on error

# Set up a unique work directory for this pipeline stream
stream=$(echo $PIPELINE_STREAMPATH | cut -f1 -d.)
export WORK_DIR=${OUTPUT_DATA_DIR}/work/${stream}
export OUT_DIR=${WORK_DIR}/output
export IN_DIR=${WORK_DIR}/input

export VISIT=840^841^842^843^844^845^846^847^848
export FILTER=r

# Workaround for EUPS trying to write to home directory
export HOME=`pwd`

# Test which version of RHEL we are using
majversion=$(lsb_release -rs | cut -f1 -d.)

export SCRIPT=${SCRIPT_LOCATION}/${PIPELINE_PROCESS:-$1}

# Set up Twinkles environment and invoke process specific script
if [ $majversion -eq 6 ] 
then
scl enable devtoolset-3 'source ${DM_DIR}/${DM_SETUP}; set -xe; export SHELLOPTS; source ${SCRIPT}'
else
source ${DM_DIR}/${DM_SETUP}; set -xe; export SHELLOPTS; source ${SCRIPT}
fi
