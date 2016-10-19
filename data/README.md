# Twinkles Data

This folder contains small data files, for use in the examples or
otherwise.

### [`SelectedKrakenVisits.csv`](SelectedKrakenVisits.csv)

`OpSim` output metadata for 1227 visits, from the `kraken_XXXX` database.

### [`kraken_sim.csv`](kraken_sim.csv)

Metadata for 307,900 simulated supernovae.

### [`twinkles_tdc_rung4.fits`](twinkles_tdc_rung4.fits)

FITS binary table of 872 mock lensed quasars, drawn from the OM10 catalog by the TDC Evil Team when making the TDC1 dataset. Extension 2 contains the header listing the columns.

### [`agn_lens_ids.csv`](agn_lens_ids.csv)

CSV file containing the lens galaxy ids for the Twinkles field of view.

### [`twinkles_lenses_v2.fits`](twinkles_lenses_v2.fits)

FITS binary table of mock lensed quasars based on [`twinkles_tdc_rung4.fits`](twinkles_tdc_rung4.fits), but using only systems with lens galaxies matched using the notebook [`MatchingLensGalaxies.ipynb`](../examples/notebooks/MatchingLensGalaxies.ipynb) to CATSIM galaxies and adding properties from those CATSIM galaxies for the REFF and SED Filename columns.

### res.dat  written using
./generatePhosimInput.py --outfile ../data/res.dat --seddir tmp  --opsimDB minion_1016_sqlite.db --OpSimDBDir ~/data/LSST/OpSimData 230
