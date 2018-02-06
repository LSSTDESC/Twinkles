# Installation Notes

The Twinkles package uses the LSST DM Stack's `afw` code, and also the LSST
Sims tools (among other things). Here's how to get everything working.


## 1. Install the LSST DM Stack and Sims Tools

First set up a binary installation of a stack weekly i.e. w_2018_03, preferably the one that corresponds to the current sims tag. Then install lsst_sims from source. Reference: https://pipelines.lsst.io/v/DM-12009/install/newinstall.html
```
curl -sSL https://raw.githubusercontent.com/lsst/lsst/master/scripts/newinstall.sh
bash newinstall.sh -cbts
source loadLSST.bash
eups distrib install lsst_distrib -t w_2018_xx lsst_distrib
curl -sSL https://raw.githubusercontent.com/lsst/shebangtron/master/shebangtron | python
eups distrib install lsst_sims -t sims --nolocks
```

This will install the LSST packages in your current working directory. Then you'll need to do:
```
setup lsst_distrib
setup lsst-sims
```

## 3. Get set up to use the LSST code

See the project's notes [here](https://confluence.lsstcorp.org/display/LSWUG/Using+the+LSST+Stack).
LSST packages have to be added to your PATH, etc. before you can use them. This is handled by `eups`.
We need to do:
```
    export LSST_DIR = ${HOME}/miniconda2
    source ${LSST_DIR}/loadLSST.bash
    setup obs_lsstSim
    setup lsst_sims
```
This needs to be done every time you start a new shell - so these lines could be worth adding to your `.bashrc` file or equivalent. Note that c-shell users can use `loadLSST.csh` and use `setenv` in their `.login` file.


## 4. Install python packages

We use several useful python packages that don't come with the DM stack:
```
conda install astropy
conda install pandas
conda install nose
```

## 5. Possible Pitfalls

Here are the problems we've hit when developing the above notes.

1. When running the `examples/notebooks/PostageStampMaker_demo.ipynb` you might see something like the following:
```
ImportError: dlopen(/Users/pjm/miniconda2/opt/lsst/daf_persistence/python/lsst/daf/persistence/_persistenceLib.so, 10): Library not loaded: @rpath/libboost_system.dylib
  Referenced from: /Users/pjm/miniconda2/opt/lsst/boost/lib/libboost_filesystem.dylib
  Reason: image not found
```
