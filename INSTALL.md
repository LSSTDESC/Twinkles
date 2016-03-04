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
This installs miniconda into `${HOME}/miniconda2`. You should now pre-pend your `PATH` with `${HOME}/miniconda2/bin` so that
this is becomes your default version of python.


## 2. Install the LSST DM Stack and Sims Tools

First you need to add the LSST "channel:"
```
conda config --add channels http://research.majuric.org/conda/stable
```
Now do:
```
conda install lsst-distrib
```
and find something else to do for half an hour. This will install the LSST packages in `${HOME}/miniconda2/pkgs/`. Then you'll need to do:
```
conda install lsst-sims
```
This will upgrade some packages and downgrade others.

## 3. Get set up to use the LSST code

See the project's notes [here](https://confluence.lsstcorp.org/display/LSWUG/Using+the+LSST+Stack).
LSST packages have to be added to your PATH, etc. before you can use them. This is handled by `eups`.
We need to do:
```
    export LSST_DIR = ${HOME}/miniconda2
    set path = (${LSST_DIR}/bin $path)
    source ${LSST_DIR}/bin/eups-setups.sh
    setup obs_lsstSim
    setup lsst_sims
```
This needs to be done every time you start a new shell - so these lines could be worth adding to your `.bashrc` file or equivalent. Note that c-shell users can use `eups_setup.csh` and use `setenv` in their `.login` file.


## 4. Install python packages

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
