from __future__ import absolute_import, division, print_function
import numpy
import math
from scipy.interpolate import interp1d
from lsst.sims.catalogs.decorators import register_class, register_method, compound
from lsst.sims.catUtils.mixins import Variability

__all__ = ['TimeDelayVariability', 'VariabilityTwinkles']
@register_class
class TimeDelayVariability(Variability):

    @register_method('applyAgnTimeDelay')
    def applyAgnTimeDelay(self, params, expmjd_in):
        dMags = {}
        expmjd = numpy.asarray(expmjd_in,dtype=float)
        toff = numpy.float(params['t0_mjd']+params['t0Delay'])
        seed = int(params['seed'])
        sfint = {}
        sfint['u'] = params['agn_sfu']
        sfint['g'] = params['agn_sfg']
        sfint['r'] = params['agn_sfr']
        sfint['i'] = params['agn_sfi']
        sfint['z'] = params['agn_sfz']
        sfint['y'] = params['agn_sfy']
        tau = params['agn_tau']
        epochs = expmjd - toff
        if epochs.min() < 0:
            raise RuntimeError("WARNING: Time offset greater than minimum epoch.  " +
                               "Not applying variability. "+
                               "expmjd: %e should be > toff: %e  " % (expmjd, toff) +
                               "in applyAgn variability method")

        endepoch = epochs.max()

        dt = tau/100.
        nbins = int(math.ceil(endepoch/dt))
        dt = (endepoch/nbins)/tau
        sdt = math.sqrt(dt)
        numpy.random.seed(seed=seed)
        es = numpy.random.normal(0., 1., nbins)
        for k in sfint.keys():
            dx = numpy.zeros(nbins+1)
            dx[0] = 0.
            for i in range(nbins):
                #The second term differs from Zeljko's equation by sqrt(2.)
                #because he assumes stdev = sfint/sqrt(2)
                dx[i+1] = -dx[i]*dt + sfint[k]*es[i]*sdt + dx[i]
            x = numpy.linspace(0, endepoch, nbins+1)
            intdx = interp1d(x, dx)
            magoff = intdx(epochs)
            dMags[k] = magoff
        return dMags

class VariabilityTwinkles(TimeDelayVariability):
    """
    This is a mixin which wraps the methods from the class Variability
    into getters for InstanceCatalogs (specifically, InstanceCatalogs
    with AGNs).  Getters in this method should define columns named like
    delta_columnName
    where columnName is the name of the baseline (non-varying) magnitude
    column to which delta_columnName will be added.  The getters in the
    photometry mixins will know to find these columns and add them to
    columnName, provided that the columns here follow this naming convention.
    Thus: merely including VariabilityTwinkles in the inheritance tree of
    an InstanceCatalog daughter class will activate variability for any column
    for which delta_columnName is defined.
    """

    @compound('delta_lsst_u', 'delta_lsst_g', 'delta_lsst_r',
             'delta_lsst_i', 'delta_lsst_z', 'delta_lsst_y')
    def get_agn_variability(self):
        """
        Getter for the change in magnitudes due to agn
        variability.  The PhotometryTwinkles mixin is clever enough
        to automatically add this to the baseline magnitude.
        """

        varParams = self.column_by_name('varParamStr')

        output = numpy.empty((6,len(varParams)))

        for ii, vv in enumerate(varParams):
            if vv != numpy.unicode_("None") and \
               self.obs_metadata is not None and \
               self.obs_metadata.mjd is not None:

                deltaMag = self.applyVariability(vv)

                output[0][ii] = deltaMag['u']
                output[1][ii] = deltaMag['g']
                output[2][ii] = deltaMag['r']
                output[3][ii] = deltaMag['i']
                output[4][ii] = deltaMag['z']
                output[5][ii] = deltaMag['y']
            else:
                output[0][ii] = 0.0
                output[1][ii] = 0.0
                output[2][ii] = 0.0
                output[3][ii] = 0.0
                output[4][ii] = 0.0
                output[5][ii] = 0.0

        return output
