#!/usr/bin/env python

import lsst.daf.persistence as dp
import lsst.afw.image as afw_image
import numpy
import matplotlib.pylab as plt
from calc_snr import make_invsnr_arr

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

def plot_point_mags(output_data, visits, outfile, dataId):
    # get a butler
    butler = dp.Butler(output_data)

    # The following value for refcatId is "mandatory, but meaningless",
    # so we won't try to generalize it.
    refcatId = {'tract':0, 'patch':'0,0'}
    ref = butler.get('deepCoadd_ref', dataId=refcatId)

    # visits to use for lightcurves
    visit_list = [int(x) for x in visits.split('^')]

    # get the sources and calib objects for each single epoch visit
    forced_srcs = {}
    calibs = {}
    for visit in visit_list:
        dataId['visit'] = visit
        forced_srcs[visit] = butler.get('forced_src', dataId=dataId)
        calexp = butler.get('calexp', dataId=dataId)
        calibs[visit] = calexp.getCalib()
        del calexp

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
    for lightcurve in lightcurve_fluxes.values():
        if len(lightcurve) == len(visit_list):
            plt.scatter(afw_image.abMagFromFlux(numpy.median(lightcurve)), 
                        numpy.std(lightcurve)/numpy.median(lightcurve), 
                        alpha=0.5)
    mags, invsnrs = make_invsnr_arr()
    plt.plot(mags, invsnrs, color='red', linewidth=2, alpha=0.75)
    plt.xlabel("Calibrated magnitude of median flux")
    plt.ylabel("stdev(flux)/median(flux)")
    plt.xlim(15.5, 25)
    plt.ylim(0., 0.5)
    plt.savefig(outfile)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="For a set of visits, make a plot of fractional stdev vs median flux for the forced sources in the Twinkles cookbook example.")
    parser.add_argument('output_data', help='Output directory for the cookbook pipeline')
    parser.add_argument('outfile', help='Filename of the output png file with the plot')
    parser.add_argument('--visits', type=str, help='list of visits to process')
    parser.add_argument('--id', nargs='+', type=str, help='dataId of datasets to process', default="raft=2,2 sensor=1,1 filter=r tract=0".split())
    args = parser.parse_args()

    plot_point_mags(args.output_data, args.visits, args.outfile,
                    dataId=make_dataId(args.id))
