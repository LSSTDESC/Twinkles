#
# This setup file assumes that the LSST Stack and sims packages have
# been set up and that the OM10 package as well as a local copy
# obs_lsstSim are installed at the same top level directory as the
# Twinkles repo itself.
#

twinkles_inst_dir=$( cd $(dirname $BASH_SOURCE)/../..; pwd -P )

#
# Set up the local build of obs_lsstSim.
#
setup -j -r ${twinkles_inst_dir}/obs_lsstSim

export OM10_DIR=${twinkles_inst_dir}/OM10
export TWINKLES_DIR=${twinkles_inst_dir}/Twinkles/twinkles
export PYTHONPATH=${OM10_DIR}:${TWINKLES_DIR}:${PYTHONPATH}

PS1="[Twinkles] "
