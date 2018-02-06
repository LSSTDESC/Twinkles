# Installation Notes

The Twinkles package uses the LSST DM Stack's `afw` code, and also the LSST
Sims tools (among other things). Here's how to get everything working.


## 1. Install the LSST DM Stack and Sims Tools

First set up a binary installation of a stack weekly, preferably the one that corresponds to the current sims tag.  Reference: https://pipelines.lsst.io/v/DM-12009/install/newinstall.html
```
curl -OL https://raw.githubusercontent.com/lsst/lsst/14.0/scripts/newinstall.sh
bash newinstall.sh -ct
```

This will install the LSST packages in `${HOME}/miniconda2/pkgs/`. Then you'll need to do:
```
conda install lsst-sims
```

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
