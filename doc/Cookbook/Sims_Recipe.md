## Recipe: Simulating LSST Image Data

_Scott Daniel, Rahul Biswas and Simon Krughoff_

This recipe shows how to generate simulated image data using LSST DM Sims tools.
The inputs are an `OpSim` output database, the `CatSim` mock sky database,
and a choice of sky position. You will also need a working `sprinkler` to
add extra supernovae and lensed quasars.


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
