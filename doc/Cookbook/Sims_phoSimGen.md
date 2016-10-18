# Recipe: Simulating inputs for the PhoSim Simulator (PhoSim Instance Catalogs)

This recipe shows how to generate inputs to `phoSim` known as phosim Instance Catalogs for the Twinkles Sky.  These catalogs record the position and characteristics of every astrophysical object in the simulation, along with characteristics of the observation and form the input to PhoSim. We will discuss the generation of such catalogs using the tools available to Twinkles. 

The starting point comprises an `OpSim` output database which stores each OpSim pointing as a record, the `CatSim` mock sky database. You will also need to [setup Twinkles](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Setup.md). As you can see by following that link, this requires having
- the LSST simulation stack running (version > 2.3.1)
- A working version of OM10 
- Setup Twinkles 
- And the abililty to conect the UW catsim database on the server fatboy (For the first time, this might need some steps in contacting people)
Instructions for getting all this done are on the  [setup Twinkles](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Setup.md)

### Setting up Twinkles
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

Now, there are scripts that use the OpSim output which is a sqlite database of ~ 4 GB size representing a simulated LSST Survey.  If you do not already have access to one of these databases, they can be downloaded from [here](https://www.lsst.org/scientists/simulations/opsim/opsim-survey-data). Once you have downloaded an OpSim simulated survey, you can point Twinkles toward it by copying the file `setup/setup_location_templates.sh` to `setup/setup_locations.sh` and set the value of the OpSimDir to suit their needs.

After you have done this, everytime you want to work with Twinkles in a new SHELL, you have to setup Twinkles. Once you have `eups` database loaded in that SHELL, you can source the
script 
```
source setup/setup_twinkles.sh
```
if your sims stack has the tag `sims` (you can check by using `eups list -v sims_catUtils`: the output includes each record of an installation of the package `sims_catUtils` known to the `eups` database with each record listing a version, the eups database location, location of the package, and finally the tag. Of these packages the one that is setup will have the tag followed by the word setup as following the tag of interest. If this tag is not 'sims' (for example, if you use a conda install, this tag is most likely 'current'), you can pass that tag to the setup script like this:
```
source setup/setup_twinkles.sh current
```
At this point, the directories of the Twinkles repositories become available as part of the `desc` namespace, and an environment variable `$TWINKLES_DIR` is exported to the SHELL.
The code uses this variable.

### Generate the `phoSim` inputs

The inputs to `phoSim` are phoSim Instance Catalogs which contains
-  all of the meta-data characterizing the observation :
- the astrophysical sources and their fluxes/models at the time of observation.

The relevant information is represented in `Twinkles` as `desc.twinkles.TwinklesSky`. In order to create an instance of `TwinklesSky`, it requires input in the form of
- instances of `lsst.sims.utils.ObservationMetaData`
- The catalogDB Objects that define the properties of astrophysical sources in the form of database tables on fatboy. These are hard-coded into the class, as there is not much to choose. The exception is the classs representing SN, since we may use different SN tables. Each class of object Stars (static and variable) and Galaxies (Bugle, Disc, AGN) form their own groups in a Compound Catalog class. This is particularly important for the construction of time-delayed AGN (manifestations of strongly lensed AGNs). 

#### Functionality 

`desc.twinkles.TwinklesSky` implements a selection cut to remove all stars and galaxies brighter than a particular magnitude (set to 11.0 by default, but can be adjusted for
each of these classes in terms of a g band magnitude). Finally, it has a method `writePhoSimCatalog` for serializing this information to an ascii file (phosim instance catalog) in a file format appropriate for phosim inputs. For static objects, PhoSim uses seds that are stored (with compression) in `CatSim`. For supernovae, the SEDs at each point of time are calculated on the fly from a model and written to disk. While writing out the phoSim instance catalog, the `writePhoSimCatalog` method also writes these SEDs to disk.

There is an additional subtlety: If we want to be doing many pointings, it is inefficient to open too many new connections to fatboy (even though parallel connections are allowed).
Hence, `TwinklesSky` has an attribute `availableConnections` which allows it to reuse connections made to fatboy. This is also used as an input (It can start as None) 

The class constructor for `TwinklesSky` has parameters

- obs_metadata : Observaton MetaData of the relevant OpSim pointing
- brightestStar_gmag_inCat : the g band magnitude threshold for rejecting bright stars 
- brightestGal_gmag_inCat : the g band magnitude threshold for rejecting bright Galalxies 
- sntable : name of the supernova Table to use.
- sn_sed_file_prefix : controls the location and filenames of the SN spectra written to disk
- availableConnections : At the beginning, this can be None, but it is good to hand back available connections to a new instance rather than having it create the connections


#### Putting it altogether ...

To generate all the phosim instance catalogs and the spectra, we must:

Iterate through each pointing of OpSim relevant for us:

1. Create the ObservationMetaData corresponding to the pointing 
2. create an instance of `TwinklesSky` , with this ObservationMetaData as input, along with the selection cut desired and location of filenames for the spectra
3. Have a filename corresponding to the pointing for the catalog, and call the `writePhoSimCatalog` method to write to it
4. Finally, after writing, store the available connections and hand it to the next instance that will be created

All of this is done in an example script `bin/generatePhosimInput.py` 

- First we get a set of pointings by doing a sql query on the OpSim database. We can do the queries restricting to FieldID=1427 (for Twinkles) or can restrict to list of obSHistIds (preferred).
- We then use ObservationMetaDataGneerator to create ObservationMetaData corresponding to these.
Then iterating through the ObservationMetaData in this, we follow the steps above to write out the phosim instance catalog. To run the example (after the setup steps above)
and changing the path to the OpSim database, run 
```
python bin/generatePhoSimInput.py
```

# Older Stuff 
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
