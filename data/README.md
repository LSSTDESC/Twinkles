# Twinkles Data

This folder contains small data files, for use in the examples or
otherwise.

### [`SelectedKrakenVisits.csv`](SelectedKrakenVisits.csv)

`OpSim` output metadata for 1227 visits, from the `kraken_XXXX` database.

### [`kraken_sim.csv`](kraken_sim.csv)

Metadata for 307,900 simulated supernovae.

### [`twinkles_tdc_rung4.fits`](twinkles_tdc_rung4.fits)

FITS binary table of 872 mock lensed quasars, drawn from the OM10 catalog by the TDC Evil Team when making the TDC1 dataset. Extension 2 contains the header listing the columns.

### [`phosimCatalog.dat`](phosimCatalog.dat)

A phosim instance catalog written out by using the `./bin/generatePhosimInput.py script in the following way (from the ./bin directory)
```
./generatePhosimInput.py --outfile ../data/res.dat --seddir tmp  --opsimDB minion_1016_sqlite.db --OpSimDBDir ~/data/LSST/OpSimData 230
```
(the file `data/res.dat` was copied to `data/phpsimCatalog.dat`)

### [`spectra_files.tgz`](spectra_files.tgz)
The spectra files that were written out were then zipped into a tar archive and moved to this this file
