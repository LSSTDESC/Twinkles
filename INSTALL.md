# Installation Notes

The Twinkles package uses the LSST DM Stack's `afw` code, and also the LSST
Sims tools (among other things). Here's how to get everything working.

## 1. Get Anaconda Python

According to the [LSST community](https://community.lsst.org/t/up-and-running-with-sims-maf-contrib/383), and
various peopls around the DESC, it seems best to install the DM stack using `conda` - or in fact, `miniconda`.
Click [here](http://conda.pydata.org/miniconda.html) and download python 2.7, if you don't have Anaconda python already.
```
bash ~/Downloads/Miniconda-latest-MacOSX-x86_64.sh
```
This installs miniconda into `${HOME}/miniconda2`. You should now pre-pend your `PATH` with `${HOME}/miniconda2/bin` so that this becomes your default version of python.


## 2. Install the LSST DM Stack

First you need to add the LSST "channel:"
```
conda config --add channels http://research.majuric.org/conda/stable
```
Now do:
```
conda install lsst-distrib
```
and find something else to do for half an hour. This will install the stack packages in `${HOME}/miniconda2/pkgs/`.


## 3. Install the LSST Sims Tools

For this you will need a different channel:
```
conda config --add channels https://eupsforge.net/conda/dev
```
This will install the Sims packages, also in `${HOME}/miniconda2/pkgs/`. Then you'll need to do:
```
conda install lsst-sims=master.20150928224422
```
This will upgrade some packages and downgrade others. Note the very specific
version number, and the date these notes were last modified - this could be a source of trouble, so we'd best all watch out.


## 4. Get set up to use the LSST code

See the project's notes [here](https://confluence.lsstcorp.org/display/LSWUG/Using+the+LSST+Stack).
LSST packages have to be added to your PATH, etc before you can use them. This is handled by `eups`. We need to do:
```
    export LSST_DIR = ${HOME}/miniconda2
    set path = (${LSST_DIR}/bin $path)
    source ${LSST_DIR}/bin/eups-setups.sh
    setup obs_lsstSim
    setup lsst_sims
    setup sims_catUtils -t rbiswas -t b1887
```
This needs to be done every time you start a new shell - so these lines could be worth adding to your `.bashrc` file or equivalent. Note that c-shell users can use `eups_setup.csh` and use `setenv` in their `.login` file. Note the additional setup step, needed to get Rahul's latest supernova code.


## 5. Install python packages

We use several useful python packages that don't come with the DM stack:
```
pip install astropy
pip install pandas
pip install nose
pip install scipy
pip install matplotlib
```

## 5. Possible Pitfalls

Here are the problems we've hit when developing the above notes.

1. When running the `examples/notebooks/PostageStampMaker_demo.ipynb` you might see something like the following:
```
ImportError: dlopen(/Users/pjm/miniconda2/opt/lsst/daf_persistence/python/lsst/daf/persistence/_persistenceLib.so, 10): Library not loaded: @rpath/libboost_system.dylib
  Referenced from: /Users/pjm/miniconda2/opt/lsst/boost/lib/libboost_filesystem.dylib
  Reason: image not found
```
You have this library, it's just that python doesn't know where to find it, for some reason. The solution is to add another line to your `.bashrc`, after the setup commands:
```
export DYLD_LIBRARY_PATH = ${LSST_DIR}/opt/lsst/boost/lib:${DYLD_LIBRARY_PATH}
```

2. Getting the Sims vs Stack balance is tricky. For example,
again running the `examples/notebooks/PostageStampMaker_demo.ipynb`, I got this:
```
/Users/pjm/work/stronglensing/LSST/DESC/Twinkles/python/desc/twinkles/generatePhosimInput.py in <module>()
     20 from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
     21 from lsst.sims.catalogs.generation.db import CatalogDBObject
---> 22 from lsst.sims.catalogs.generation.db.dbConnection import DBConnection
     23 from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject, StarObj, MsStarObj, \
     24         BhbStarObj, WdStarObj, RRLyStarObj, CepheidStarObj, GalaxyBulgeObj, GalaxyDiskObj, \

ImportError: cannot import name DBConnection
```
The problem was that I had installed `lsst_sims` from the same channel as
the stack -- but I needed a more up-to-date version, which lives on the
`https://eupsforge.net/conda/dev` channel.

In general, if you hit an `ImportError`, you can use `eups` to check whether you have that package installed:
```
pjm@PPA-PC92478 > eups list | grep catUtils
sims_catUtils         2.0.1-2-gf11df9e+8 	current b1711 v11_0 setup
```
This line - including the version number (2.01) - is useful information when you report the problem to the Twinkles issues. Here's another `ImportError`:
```
/Users/pjm/work/stronglensing/LSST/DESC/Twinkles/python/desc/twinkles/generatePhosimInput.py in <module>()
     21 from lsst.sims.catalogs.generation.db import CatalogDBObject
     22 from lsst.sims.catalogs.generation.db.dbConnection import DBConnection
---> 23 from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject, StarObj, MsStarObj, \
     24         BhbStarObj, WdStarObj, RRLyStarObj, CepheidStarObj, GalaxyBulgeObj, GalaxyDiskObj, \
     25         GalaxyAgnObj, SNObj

ImportError: cannot import name SNObj
```
You'd think this one should have been fixed with the `setup sims_catUtils -t rbiswas -t b1887` but it turns out it wasn't:
```
pjm@PPA-PC92478 > eups list | grep catUtils
sims_catUtils         sims_2.2.1+1 	current conda b1887 setup
```
