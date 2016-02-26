inst_dir=$( cd $(dirname $BASH_SOURCE)/../..; pwd -P )
if [ ! -d "$inst_dir/ups_db" ]; then
   mkdir $inst_dir/ups_db
fi
export EUPS_PATH=$inst_dir:${LSSTSW}/stack
. ${LSSTSW}/bin/setup.sh
setup lsst_sims
eups declare Twinkles -r . -c
setup Twinkles
