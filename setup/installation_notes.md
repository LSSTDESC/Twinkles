These notes describe how to install Twinkles and the other packages on
which it depends, assuming that the LSST Stack (including the sims
packages) is already installed in ${LSST_HOME} 

(Here are [instructions for building the LSST Stack from
source](https://confluence.lsstcorp.org/display/LSWUG/Building+the+LSST+Stack+from+Source)
and [instructions for the sims
packages](https://confluence.lsstcorp.org/display/SIM/Catalogs+and+MAF).)

To start, cd to the top level directory where you want Twinkles et
al. to live:
```
$ cd <Twinkles top level directory>
```

Clone the Twinkles, OM10, pipe_tasks, and obs_lsstSim respositories
into that area:
```
$ git clone git@github.com:DarkEnergyScienceCollaboration/Twinkles.git
$ git clone git@github.com:drphilmarshall/OM10.git
$ git clone git@github.com:lsst/pipe_tasks.git
$ git clone git@github.com:lsst/obs_lsstSim.git
```

Set up the LSST Stack and build the needed development branches of
pipe_tasks and obs_lsstSim:
```
$ source ${LSST_HOME}/loadLSST.bash
$ setup obs_lsstSim
$ cd pipe_tasks
$ git checkout tickets/DM-4305
$ scons opt=3
$ cd ../obs_lsstSim
$ git checkout tickets/DM-4302
$ scons opt=3
```

In order to run Twinkles from bash, one need only to source the LSST Stack
and Twinkles set up scripts:
```
$ source ${LSST_HOME}/loadLSST.bash
$ source <Twinkles top level directory>/setup/loadTwinkles.bash
```

To run the catsim code, one needs to be able to access the UW catsim
db server.  Instructions for doing that are at
https://confluence.lsstcorp.org/display/SIM/Accessing+the+UW+CATSIM+Database
