#!/usr/bin/env python

import functools
import numpy as np
import matplotlib.pylab as plt
from scipy.optimize import curve_fit
import lsst.daf.persistence as dp
import lsst.afw.image as afw_image
from lsst.afw.fits.fitsLib import FitsError
from desc.twinkles import make_invsnr_arr, fit_invsnr, get_visits

_filter_color = dict(u='blue',
                     g='green',
                     r='red',
                     i='cyan',
                     z='magenta',
                     y='black')
_filter_symbol = dict([(band, 'o') for band in 'ugrizy'])

def make_dataId(options):
    dataId = {}
    if options is None:
        return None
    for item in options:
        key, value = item.split('=')
        try:
            value = int(value)
        except ValueError:
            pass
        dataId[key] = value
    return dataId

class MagStats(object):
    def __init__(self, filter_, med_mags, med_err, minMag=17, mid_cut=20,
                 maxMag=26):
        self.filter = filter_
        self.med_mags = np.array(med_mags)
        self.med_err = np.array(med_err)
        index = np.where((minMag < self.med_mags) & (self.med_mags < mid_cut))
        self.sys_floor = np.median(self.med_err[index])
        index = np.where((mid_cut < self.med_mags) & (self.med_mags < maxMag))
        self.popt = (0.01, 24.5)
        fit_func = functools.partial(fit_invsnr, bandpass_name=filter_)
        self.popt, self.pcov = curve_fit(fit_func, self.med_mags[index],
                                         self.med_err[index], p0=self.popt)
    def plot_fit(self, linewidth=3, alpha=0.75):
        mags, invsnrs = make_invsnr_arr(floor=self.sys_floor, m5=self.popt[1])
        color = _filter_color[self.filter]
        plt.plot(mags, invsnrs, color=color, linewidth=linewidth, alpha=alpha)

def plot_point_mags(output_data, visit_list, dataId, minMag=17, mid_cut=20, 
                    maxMag=26):
    # get a butler
    butler = dp.Butler(output_data)

    # The following value for refcatId is "mandatory, but meaningless",
    # so we won't try to generalize it.
    refcatId = {'tract':0, 'patch':'0,0'}
    ref = butler.get('deepCoadd_ref', dataId=refcatId)

    # get the sources and calib objects for each single epoch visit
    forced_srcs = {}
    calibs = {}
    for visit in visit_list:
        dataId['visit'] = visit
        try:
            my_forced_srcs = butler.get('forced_src', dataId=dataId)
            calexp = butler.get('calexp', dataId=dataId)
            my_calibs = calexp.getCalib()
            del calexp
            forced_srcs[visit] = my_forced_srcs
            calibs[visit] = my_calibs
        except FitsError, eobj:
            print eobj

    # initialize dictionaries to hold lightcurve arrays.  Get
    # extendedness from the coadd catalog.
    lightcurve_fluxes = {}
    extendedness = {}
    for idx, ext in zip(ref.get('id'),
                        ref.get('base_ClassificationExtendedness_value')):
        lightcurve_fluxes[idx] = []
        extendedness[idx] = ext

    # pivot the source tables to assemble lightcurves
    for visit, forced_src in forced_srcs.iteritems():
        calib = calibs[visit]
        for idx, flux in zip(forced_src.get('objectId'),
                             forced_src.get('base_PsfFlux_flux')):
            if extendedness[idx] > 0.5:
                continue
            if flux <= 0.:
                continue
            lightcurve_fluxes[idx].append(afw_image.fluxFromABMag(calib.getMagnitude(flux)))

    # compute aggregate quantities for each object and plot
    band = dataId['filter']
    med_mags = []
    med_err = []
    for lightcurve in lightcurve_fluxes.values():
        if len(lightcurve) == len(visit_list):
            median_flux = np.median(lightcurve)
            med_mags.append(afw_image.abMagFromFlux(median_flux))
            med_err.append(np.std(lightcurve)/median_flux)

    print "number of objects:", len(med_mags)
    mag_stats = MagStats(band, med_mags, med_err)
    scatter = plt.scatter(med_mags, med_err,
                          alpha=0.3, color=_filter_color[band],
                          marker=_filter_symbol[band],
                          label='filter=%s, Floor=%.1f%%, m_5=%0.2f'
                          % (band, mag_stats.sys_floor*100, mag_stats.popt[1]))
    plt.xlabel("Calibrated magnitude of median flux")
    plt.ylabel("stdev(flux)/median(flux)")
    plt.xlim(15.5, 25)
    plt.ylim(0., 0.5)
    return scatter, mag_stats

if __name__ == '__main__':
#    import argparse
#
#    parser = argparse.ArgumentParser(
    data_repo = '/nfs/farm/g/lsst/u1/users/tonyj/work/00/output'
#    data_repo = 'output'
    visits = get_visits(data_repo)
    print '# visits per filter:'
    for filter_ in visits:
        print "  ", filter_, len(visits[filter_])
    dataId = make_dataId('raft=2,2 sensor=1,1 tract=0'.split())
    plots = []
    mag_stats = {}
    for filter_ in visits:
        if len(visits[filter_]) < 2:
            print "skipping %s band: too few visits" % filter_
            continue
        print "plotting filter", filter_
        dataId['filter'] = filter_
        plot, stats = plot_point_mags(data_repo, visits[filter_], dataId=dataId)
        mag_stats[filter_] = stats
    for filter_ in mag_stats:
        mag_stats[filter_].plot_fit()

    outfile = 'mag_stdevs.png'
    plt.legend(handles=plots, scatterpoints=1, loc=2)
    plt.savefig(outfile)
