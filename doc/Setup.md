# Twinkles Set-up

To run your own `twinkles` simulations, you will need to have taken the following steps.

## LSST Sims Setup

See [this LSST Sims confluence page](https://confluence.lsstcorp.org/display/SIM/Catalogs+and+MAF) for install instructions. In short:

1) Install the LSST DM software stack, including the `sims` utilities.
```
$> mkdir ~/stack
$> cd ~/stack
$> curl -O https://sw.lsstcorp.org/eupspkg/newinstall.sh
$> chmod 700 newinstall.sh
$> ./newinstall.sh
```
Answer yes to the two questions.
```
$> source loadLSST.bash
$> eups distrib install lsst_sims -t sims
$> setup lsst_sims -t sims
```

2) Enable connection to CatSim databases

For security reasons, the CatSim database are behind a fairly restrictive
firewall.  The two ways to gain access to the database are to get your machine
listed on the whitelist of IP addresses allowed through the firewall, or to
establish an SSH tunnel through a shared account on one of the University of
Washington computers.  Below, we present the instructions for setting up to
connect via the SSH tunnel.  To connect via the whitelist, see the appropriate
section in [this
document](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Cookbook/Sims_Recipe.md).

    #### Instructions to enable connection via the SSH tunnel

    a) Create a directory `$HOME/.lsst/`

    b) Create a file `db-auth.paf` in that directory whose contents are
    ```
    database: {
        authIfno: {
            host: localhost
            port: 51433
            user: <shared username>
            password: <shared password>
        }
    }
    ```

    c) Set the permissions on `$HOME/.lsst/` to 700 using
    `chmod 700 $HOME/.lsst'

    d) Set the permissions on `$HOME/.lsst/db-auth.paf` to 600 using
    `chomd 600 $HOME/.lsst/db-auth.paf`

    c) Email your public ssh key to Scott Daniel (`scottvalscott@gmail.com`).
    He will also give you the shared username and password that belongs in
    `$HOME/.lsst/db-auth.paf`.  If you do not already have an ssh key,
    instructions for creating one can be found
    [here](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/).

3) Install `PhoSim`.
```
$> mkdir ~/repos
$> cd ~/repos
$> git clone https://bitbucket.org/phosim/phosim_release.git
$> setup cfitsio
$> setup fftw
$> ./configure
```
You'll have to point to the correct cfitsio and fftw3 libraries and headers for your system.
```
$> make
```

4) Test `PhoSim`.
```
$> mkdir ~/TwinklesData
$> cd ~/TwinklesData
$> python $SIMS_CATUTILS_DIR/examples/generatePhosimInput.py
```
This produces a file `PhoSim` can run.
```
$> ./phosim ~/TwinklesData/phoSim_example.txt --sensor="R22_S11" -c examples/nobackground
```
Images show up in the "output" directory.


## Gravitational Lens Sprinkling Setup

1) Follow instructions above to setup LSST Sims

2) Install and setup [OM10](https://github.com/drphilmarshall/OM10).

3) Open an SSH tunnel for database connection to UW. See
[here](https://confluence.lsstcorp.org/display/SIM/Accessing+the+UW+CATSIM+Database) for more information.
This is where the objects that will populate the catalog are stored.

4) You'll also need the OpSim sqlite repository from [this page](https://confluence.lsstcorp.org/display/SIM/OpSim+Datasets+for+Cadence+Workshop+LSST2015)

5) Now you're ready to go with:
```
$> python generatePhosimInput.py
```

## Supernova Sprinkling Setup
