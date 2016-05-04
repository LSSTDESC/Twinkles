"""
Tools for examining light curves from Level 2 tables using sncosmo.
"""
from __future__ import absolute_import
import os
import numpy as np
import astropy.table
import astropy.units
import matplotlib.pyplot as plt
import sncosmo
import desc.twinkles.db_table_access as db_table_access

def bandpass(band):
    "LSST band pass name"
    return 'lsst%s' % band

class LightCurve(object):
    "Multiband light curve using sncosmo."
    def __init__(self, lc_dict):
        """
        lc_dict: light curve data from ForcedSourceTable.get_light_curves.
        """
        data = dict([(key, []) for key in
                     'bandpass mjd ra dec flux fluxerr zp zpsys'.split()])
        for band, lc_recarr in lc_dict.items():
            npts = len(lc_recarr)
            data['bandpass'].extend(npts*[bandpass(band)])
            for key in 'mjd ra dec flux fluxerr'.split():
                data[key].extend(lc_recarr[key])
            data['zp'].extend(npts*[25.0])
            data['zpsys'].extend(npts*['ab'])
        self.data = astropy.table.Table(data=data)

    def plot(self, **kwds):
        "Plot the light curve data."
        kwds['data'] = self.data
        fig = sncosmo.plot_lc(**kwds)
        return fig

class LightCurveFactory(object):
    def __init__(self, **db_info):
        "Connect to the ForcedSource db table and fill the sncosmo registry."
        self.forced = db_table_access.ForcedSourceTable(**db_info)
        self._fill_sncosmo_registry()

    def _fill_sncosmo_registry(self, bands='ugrizy'):
        "Fill the sncosmo registry with the LSST bandpass data."
        for band in bands:
            bp_file = os.path.join(os.environ['THROUGHPUTS_DIR'], 'baseline',
                                   'total_%s.dat' % band)
            bp_data = np.genfromtxt(bp_file, names=['wavelen', 'transmission'])
            band = sncosmo.Bandpass(bp_data['wavelen'],
                                    bp_data['transmission'],
                                    name=bandpass(band),
                                    wave_unit=astropy.units.nm)
            sncosmo.registry.register(band, force=True)

    def getObjectIds(self):
        "Get the objectIds in the reference catalog."
        query = 'select objectId from Object order by objectId asc'
        return self.forced.apply(query, lambda curs : [x[0] for x in curs])

    def create(self, objectId):
        "Create a LightCurve object."
        return LightCurve(self.forced.get_light_curves(objectId))

if __name__ == '__main__':
    db_info = dict(db='jc_desc', read_default_file='~/.my.cnf')
    lc_factory = LightCurveFactory(**db_info)
    object_ids = lc_factory.getObjectIds()
    objectId = object_ids[15000]
    lc = lc_factory.create(objectId)
    fig = lc.plot()
    plt.savefig('lcs_%i.png' % objectId)
