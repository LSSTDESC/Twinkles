## Recipe: Simulating PhoSim Instance Catalogs

This recipe shows how to generate inputs to phoSim known as phosim Instance Catalogs for the Twinkles Sky.  These catalogs record the position and characteristics of every astrophysical object in the simulation and form the input to PhoSim. We will discuss the generation of such catalogs using the tools generated in Twinkles.   
ssimulated image data using LSST DM Sims tools.
The inputs are an `OpSim` output database, the `CatSim` mock sky database,
and a choice of sky position. You will also need to setup Twinkles and have a version of the LSST simulation stack running. 
Finally, you will need an open connection to the UW catsim database server fatboy, and a working version of OM10. The instructions for getting all of this running are 
[here](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Setup.md)


Once you have a version of the LSST sims stack working, you have the `eups` database loaded. Now you should be able to do
```
eups list sims_catUtils
```
and see the the versions and tags listed for this eups package.

When first setting up Twinkles, from the top level directory of `Twinkles` use 
```
source setup/declare_eups.sh
```
to declare this package location and name to the `eups` database with a tag given by your user name. This step will not required to be repeated. 
After you have done this, everytime you want to work with Twinkles in a new SHELL, you have to setup Twinkles. Once you have `eups`, you can source the
script 
```
source setup/setup_twinkles.sh
```
if your sims stack has the tag `sims` (you can check by using `eups list -v sims_catUtils`), or you can give it the tag your sims stack has (for example if you did a conda install, this tag is most likely 'current') in the following way:
```
source setup/setup_twinkles.sh current
```
Now the directories of the Twinkles repositories will be availabel as part of the `desc` namespace, and an environment variable `$TWINKLES_DIR` is exported to the SHELL.
The code uses this variable.

_More to come here from Scott and Rahul..._


### Generate the `phoSim` inputs

First generate the inputs to `phoSim` and start them generating (read the `phoSim` docs for the generation part)

The script to do this resides in this repository and will only generate input files for the first ~50 visits.  This is enough to have 10
visits each of g, r, and i band.  The script will also generate a reference catalog for photometric and astrometric calibration.
You'll also need the OpSim sqlite repository for [enigma_1189](http://ops2.tuc.noao.edu/runs/enigma_1189/data/enigma_1189_sqlite.db.gz)
```
$> setup sims_catUtils
$> python generatePhosimInput.py
```
This script will also generate a reference catalog at the same time.  The reference catalog will show up in `twinkles_ref.txt`.

There are some really bright stars that take forever to simulate.  This could be done with a cut
in the original `phoSim` generation script.  I just haven't done it.
```
$> awk '{if(NR < 21 || $5 > 13) print $0}' phosim_input_840.txt >phosim_input_840_stripped.txt
.
.
.
$> awk '{if(NR < 21 || $5 > 13) print $0}' phosim_input_848.txt >phosim_input_848_stripped.txt
```

Note that when using `phoSim` to simulate images using these catalogs, it's important to provide the `-s R22_S11` switch.  This will
only simulate the central chip.  Since these catalogs are intended to cover the central chip at all rotations, it will also spill
onto other chips in the central raft.  Since the boarder chips will not be fully covered, it's not useful to simulate them.
