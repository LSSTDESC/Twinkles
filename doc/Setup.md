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

2) Install `PhoSim`.
```
$> mkdir ~/repos
$> cd ~/repos
$> git clone https://stash.lsstcorp.org/scm/sim/sims_phosim.git
$> setup cfitsio
$> setup fftw
$> ./configure
```
You'll have to point to the correct cfitsio and fftw3 libraries and headers for your system.
```
$> make
```

3) Test `PhoSim`.
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

## Supernova Sprinkling Setup

