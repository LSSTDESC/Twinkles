import lsst.daf.persistence as dp
import lsst.afw.image as afw_image
import numpy
from functools import partial
from scipy.optimize import curve_fit
import matplotlib.pylab as plt
from calc_snr import make_invsnr_arr, fit_invsnr

# get a butler
butler = dp.Butler('output_data')
dataId = {'tract':0, 'patch':'0,0'}

bandpass_color_map = {'g':'blue', 'r':'green', 'i':'red'}
bandpass_symbol_map = {'g':'o', 'r':'v', 'i':'s'}

# get ref catalog
ref = butler.get('deepCoadd_ref', dataId=dataId)

visit_map = {'r':[840, 841, 842, 843, 844, 845, 846, 847, 848, 849],
             'i':[870, 871, 872, 873, 874, 875, 876, 877, 878, 879],
             'g':[860, 861, 862, 863, 864, 865, 866, 867, 868, 869]}

scatters = []
for bandpass_name in 'gri':
    # visits to use for lightcurves
    visits = visit_map[bandpass_name]
    dataId = {'raft':'2,2', 'sensor':'1,1', 'filter':bandpass_name, 'tract':0}

    # get the sources and calib objects for each single epoch visit
    forced_srcs = {}
    calibs = {}
    for visit in visits:
        dataId['visit'] = visit
        forced_srcs[visit] = butler.get('forced_src', dataId=dataId)
        calexp = butler.get('calexp', dataId=dataId)
        calibs[visit] = calexp.getCalib()
        del calexp

    # initialize dictionaries to hold lightcurve arrays.  Get extendedness from the coadd catalog.
    lightcurve_fluxes = {}
    extendedness = {}
    for idx, ext in zip(ref.get('id'), ref.get('base_ClassificationExtendedness_value')):
        lightcurve_fluxes[idx] = []
        extendedness[idx] = ext

    # pivot the source tables to assemble lightcurves
    for visit, forced_src in forced_srcs.iteritems():
        calib = calibs[visit]
        for idx, flux in zip(forced_src.get('objectId'), forced_src.get('base_PsfFlux_flux')):
            if extendedness[idx] > 0.5:
                continue
            if flux <= 0.:
                continue
            lightcurve_fluxes[idx].append(afw_image.fluxFromABMag(calib.getMagnitude(flux)))

    # compute aggregate quantities for each object and plot
    med_mags = []
    med_err = []
    for lightcurve in lightcurve_fluxes.values():
        if len(lightcurve) == 10:
            med_mags.append(afw_image.abMagFromFlux(numpy.median(lightcurve)))
            med_err.append(numpy.std(lightcurve)/numpy.median(lightcurve))
    fit_func = partial(fit_invsnr, bandpass_name=bandpass_name)
    minMag=17.
    mid_cut=20.
    maxMag=26.
    med_mags = numpy.array(med_mags)
    med_err = numpy.array(med_err)
    idxs = numpy.where((med_mags<mid_cut)&(med_mags>minMag))
    sys_floor = numpy.median(med_err[idxs])
    idxs = numpy.where((med_mags<maxMag)&(med_mags>mid_cut))
    popt, pcov = curve_fit(fit_invsnr, med_mags[idxs], med_err[idxs], p0=[0.01, 24.5])
    scatter = plt.scatter(med_mags, med_err, alpha=0.3, color=bandpass_color_map[bandpass_name],
                marker=bandpass_symbol_map[bandpass_name],
                label="filter=%s, Floor=%.1f%%, m_5=%0.2f"%(bandpass_name,sys_floor*100.,popt[1]))
    scatters.append(scatter)
    mags, invsnrs = make_invsnr_arr(floor=sys_floor, m5=popt[1])
    plt.plot(mags, invsnrs, color='black', linewidth=3, alpha=0.75)
    print bandpass_name

plt.legend(handles=scatters, scatterpoints=1, loc=2)
plt.xlabel("Calibrated magnitude of median flux")
plt.ylabel("stdev(flux)/median(flux)")
plt.xlim(15.5, 25)
plt.ylim(0., 0.5)
plt.show()