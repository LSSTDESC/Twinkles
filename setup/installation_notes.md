These notes describe how to install Twinkles and the other packages on
which it depends, assuming that the LSST Stack (including the sims
packages) is already installed in `${LSST_HOME}`.

It's probably best to install the LSST Stack and sims packages using
lsstsw.  Following the instructions
[here](https://confluence.lsstcorp.org/display/LDMDG/The+LSST+Software+Build+Tool),
you'll get the master of every package.  Then in order to
install the sims packages, do
```
$ rebuild lsst_sims
```

Note that v11.0 of the Stack that one obtains by following [these
instructions for building the LSST Stack from
source](https://confluence.lsstcorp.org/display/LSWUG/Building+the+LSST+Stack+from+Source)
or the w.2015.39 version that one obtains by following [these
instructions for the sims
packages](https://confluence.lsstcorp.org/display/SIM/Catalogs+and+MAF)
may have memory issues on rhel6 in the assembleCoadd.py step of the
[cookbook](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/code/twinkles_cookbook.md).

Assuming you have the Stack set up via 
``` 
$ . ${LSST_HOME}/bin/setup.sh
$ setup obs_lsstSims -t bNNNN
```
where `bNNNN` is the most recent tag found in `${LSST_HOME}/stack/ups_db/obs_lsstSim`, cd to the top level directory where you want Twinkles et al. to live:
```
$ cd <Twinkles top level directory>
```

Clone the Twinkles, OM10, and obs_lsstSim respositories into that area:
```
$ git clone git@github.com:DarkEnergyScienceCollaboration/Twinkles.git
$ git clone git@github.com:drphilmarshall/OM10.git
$ git clone git@github.com:lsst/obs_lsstSim.git
```

and build the needed development branch of obs_lsstSim:
```
$ cd obs_lsstSim
$ git checkout tickets/DM-4302
$ scons opt=3
```

In order to run Twinkles from bash, one needs to setup the Stack as
shown above and source the Twinkles set up script:
```
$ source <Twinkles top level directory>/Twinkles/setup/loadTwinkles.bash
```

To run the catsim code, one needs to be able to access the UW catsim
db server.  Instructions for doing that are at
https://confluence.lsstcorp.org/display/SIM/Accessing+the+UW+CATSIM+Database
