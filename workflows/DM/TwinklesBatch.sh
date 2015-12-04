#!/bin/bash

ulimit -c ${CORE_LIMIT:-1000} # Limit core dump
set -e # exit on error

# Set up a unique work directory for this pipeline stream
stream=$(echo $PIPELINE_STREAMPATH | cut -f1 -d.)
export WORK_DIR=${OUTPUT_DATA_DIR}/work/${stream}

# Test which version of RHEL we are using
majversion=$(lsb_release -rs | cut -f1 -d.)

# Set up Twinkles environment and invoke process specific script
if [ $majversion -eq 6 ] 
then
scl enable devtoolset-2 'source ${DM_DIR}/${DM_SETUP}; set -xe; export SHELLOPTS; source ${SCRIPT_LOCATION}/${PIPELINE_PROCESS}'
else
source ${DM_DIR}/${DM_SETUP}; set -xe; export SHELLOPTS; source ${SCRIPT_LOCATION}/${PIPELINE_PROCESS}
fi
