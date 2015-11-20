import lsst.daf.persistence as dp
import lsst.afw.image as afw_image
import numpy
import matplotlib.pylab as plt

# get a butler
butler = dp.Butler('output_data')
dataId = {'tract':0, 'patch':'0,0'}

# get ref catalog
ref = butler.get('deepCoadd_ref', dataId=dataId)
dataId = {'raft':'2,2', 'sensor':'1,1', 'filter':'r', 'tract':0}

# visits to use for lightcurves
visits = [840, 841, 842, 843, 844, 845, 846, 847, 848]

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
for lightcurve in lightcurve_fluxes.values():
    if len(lightcurve) == 9:
        plt.scatter(afw_image.abMagFromFlux(numpy.median(lightcurve)), 
                    numpy.std(lightcurve)/numpy.median(lightcurve))
plt.xlabel("Calibrated magnitude of median flux")
plt.ylabel("stdev(flux)/median(flux)")
plt.show()
