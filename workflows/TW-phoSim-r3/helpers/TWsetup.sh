source /nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/DMstack/w.2016.40-sims_2.3.1/loadLSST.bash
setup lsst_sims
export OM10_DIR=/nfs/farm/g/desc/u1/twinkles/OM10
export PYTHONPATH=${OM10_DIR}:${PYTHONPATH}
#setup -r /nfs/farm/g/desc/u1/Pipeline-tasks/TW-phoSim-r3/Twinkles.master -j
setup -r /nfs/farm/g/desc/u1/software/redhat6-x86_64-64bit-devtoolset-3/Twinkles/Run3-phoSim-v1 -j
setup -r /nfs/farm/g/desc/u1/twinkles/Monitor -j
setup -r /nfs/farm/g/desc/u1/twinkles/pserv -j
PS1="[Twinkles] "
