## simple batch script to run on SRS pipeline
##
## Somewhere here should be code to detect architecture and set $ARCH
ARCH=redhat6-x86_64-64bit-gcc44

## phoSim installation
#PHOSIMINST=/afs/slac/g/lsst/software/redhat6-x86_64-64bit-gcc44/phoSim/phosim-3.3.2
PHOSIMINST=/nfs/farm/g/lsst/u1/software/$ARCH/phoSim/3.4.2

## phoSim opts
PHOSIMOPTS=' -s R22_S11 '


echo "========================================================================"
echo "========================================================================"
echo
echo "Entering runPhoSim.sh"
echo
echo "========================================================================"
echo "========================================================================"
printenv | sort
echo "========================================================================"
echo "========================================================================"
echo
echo
echo
echo

## phoSim output
PHOSIMOUT=$TW_PHOSIMOUT
echo "PHOSIMOUT = "$PHOSIMOUT

## phoSim instanceCatalog
PHOSIMIC=$TW_INSTANCE_CATALOG
echo "PHOSIMIC = "$PHOSIMIC

## Create ./work, if necessary
if [ -d $PHOSIMOUT/work ]
 then
  echo work directory exists
 else
  echo creating work directory
  mkdir $PHOSIMOUT/work
fi

## Create ./output, if necessary
if [ -d $PHOSIMOUT/output ]
 then
  echo output directory exists
 else
  echo creating output directory
  mkdir $PHOSIMOUT/output
fi

## Run phosim...
echo "Begin phoSim..."
date
#$PHOSIMINST/phosim.py $PHOSIMINST/examples/star -c $PHOSIMINST/examples/nobackground -w $PHOSIMOUT/work -o $PHOSIMOUT/output
echo time $PHOSIMINST/phosim.py $PHOSIMIC $PHOSIMOPTS -w $PHOSIMOUT/work -o $PHOSIMOUT/output
time $PHOSIMINST/phosim.py $PHOSIMIC $PHOSIMOPTS -w $PHOSIMOUT/work -o $PHOSIMOUT/output
rc=$?
echo 
echo "===================================================================================="
echo
echo "Completed with return code = "$rc
date
exit $rc



