#
# This setup file assumes that the LSST Stack is installed in an area
# pointed to by an environment variable LSST_HOME and that the OM10
# package as well as local copies of pipe_tasks and obs_lsstSim are
# installed at the same top level directory as the Twinkles repo
# itself.
#

#source ${LSST_HOME}/loadLSST.bash

twinkles_inst_dir=$( cd $(dirname $BASH_SOURCE)/../..; pwd -P )

#
# Set up the LSST Stack with the sims packages and the local builds of
# pipe_tasks and obs_lsstSim.
setup lsst_sims
setup -j -r ${twinkles_inst_dir}/pipe_tasks
setup -j -r ${twinkles_inst_dir}/obs_lsstSim

export OM10_DIR=${twinkles_inst_dir}/OM10
export TWINKLES_DIR=${twinkles_inst_dir}/Twinkles/twinkles
export PYTHONPATH=${OM10_DIR}:${TWINKLES_DIR}:${PYTHONPATH}

PS1="[Twinkles] "

