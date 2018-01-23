from __future__ import absolute_import, division, print_function
import numpy as np
import math
import numbers
import json
import ast
import copy
from scipy.interpolate import interp1d
from lsst.sims.catalogs.decorators import register_class, register_method, compound
from lsst.sims.catUtils.mixins import Variability, ExtraGalacticVariabilityModels, reset_agn_lc_cache
from lsst.sims.catUtils.mixins.VariabilityMixin import _VariabilityPointSources

__all__ = ["TimeDelayVariability", "VariabilityTwinkles"]

_AGN_LC_CACHE = {}

class TimeDelayVariability(Variability):

    @register_method("applyAgnTimeDelay")
    def applyAgnTimeDelay(self, valid_dexes, params, expmjd):

        global _AGN_LC_CACHE

        reset_agn_lc_cache()

        if len(params) == 0:
            return np.array([[],[],[],[],[],[]])

        if isinstance(expmjd, numbers.Number):
            dMags = np.zeros((6, self.num_variable_obj(params)))
            expmjd_arr = [expmjd]
        else:
            dMags = np.zeros((6, self.num_variable_obj(params), len(expmjd)))
            expmjd_arr = expmjd

        t0_arr = params['t0_mjd'].astype(float)
        tDelay_arr = params['t0Delay'].astype(float)
        seed_arr = params['seed']
        tau_arr = params['agn_tau'].astype(float)
        sfu_arr = params['agn_sfu'].astype(float)
        sfg_arr = params['agn_sfg'].astype(float)
        sfr_arr = params['agn_sfr'].astype(float)
        sfi_arr = params['agn_sfi'].astype(float)
        sfz_arr = params['agn_sfz'].astype(float)
        sfy_arr = params['agn_sfy'].astype(float)

        for i_time, expmjd_val in enumerate(expmjd_arr):
            for ix in valid_dexes[0]:
                toff = t0_arr[ix] + tDelay_arr[ix]
                seed = seed_arr[ix]
                tau = tau_arr[ix]

                sfint = {}
                sfint['u'] = sfu_arr[ix]
                sfint['g'] = sfg_arr[ix]
                sfint['r'] = sfr_arr[ix]
                sfint['i'] = sfi_arr[ix]
                sfint['z'] = sfz_arr[ix]
                sfint['y'] = sfy_arr[ix]

                # A string made up of this AGNs variability parameters that ought
                # to uniquely identify it.
                #
                agn_ID = '%d_%.12f_%.12f_%.12f_%.12f_%.12f_%.12f_%.12f_%.12f' \
                %(seed, sfint['u'], sfint['g'], sfint['r'], sfint['i'], sfint['z'],
                  sfint['y'], tau, toff)

                resumption = False

                # Check to see if this AGN has already been simulated.
                # If it has, see if the previously simulated MJD is
                # earlier than the first requested MJD.  If so,
                # use that previous simulation as the starting point.
                #
                if agn_ID in _AGN_LC_CACHE:
                    if _AGN_LC_CACHE[agn_ID]['mjd'] <expmjd_val:
                        resumption = True

                if resumption:
                    rng = copy.deepcopy(_AGN_LC_CACHE[agn_ID]['rng'])
                    start_date = _AGN_LC_CACHE[agn_ID]['mjd']
                    dx_0 = _AGN_LC_CACHE[agn_ID]['dx']
                else:
                    start_date = toff
                    rng = np.random.RandomState(seed)
                    dx_0 = {}
                    for k in sfint:
                        dx_0[k]=0.0

                endepoch = expmjd_val - start_date

                if endepoch < 0:
                    raise RuntimeError("WARNING: Time offset greater than minimum epoch.  " +
                                       "Not applying variability. "+
                                       "expmjd: %e should be > toff: %e  " % (expmjd, toff) +
                                       "in applyAgn variability method")

                dt = tau/100.
                nbins = int(math.ceil(endepoch/dt))

                x1 = (nbins-1)*dt
                x2 = (nbins)*dt

                dt = dt/tau
                es = rng.normal(0., 1., nbins)*math.sqrt(dt)
                dx_cached = {}

                for k, ik in zip(('u', 'g', 'r', 'i', 'z', 'y'), range(6)):
                    dx2 = dx_0[k]
                    for i in range(nbins):
                        #The second term differs from Zeljko's equation by sqrt(2.)
                        #because he assumes stdev = sfint/sqrt(2)
                        dx1 = dx2
                        dx2 = -dx1*dt + sfint[k]*es[i] + dx1

                    dx_cached[k] = dx2
                    dm_val = (endepoch*(dx1-dx2)+dx2*x1-dx1*x2)/(x1-x2)
                    if isinstance(expmjd, numbers.Number):
                        dMags[ik][ix] = dm_val
                    else:
                        dMags[ik][ix][i_time] = dm_val

                # Reset that AGN light curve cache once it contains
                # one million objects (to prevent it from taking up
                # too much memory).
                if len(_AGN_LC_CACHE)>1000000:
                    reset_agn_lc_cache()

                if agn_ID not in _AGN_LC_CACHE:
                    _AGN_LC_CACHE[agn_ID] = {}

                _AGN_LC_CACHE[agn_ID]['mjd'] = start_date+x2
                _AGN_LC_CACHE[agn_ID]['rng'] = copy.deepcopy(rng)
                _AGN_LC_CACHE[agn_ID]['dx'] = dx_cached

        return dMags


class VariabilityTwinkles(_VariabilityPointSources, TimeDelayVariability):

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

#    @compound("delta_lsst_u", "delta_lsst_g", "delta_lsst_r",
#             "delta_lsst_i", "delta_lsst_z", "delta_lsst_y")
#    def get_agn_variability(self):
#        """
#        Getter for the change in magnitudes due to agn
#        variability.  The PhotometryTwinkles mixin is clever enough
#        to automatically add this to the baseline magnitude.
#        """

#        varParams = self.column_by_name("varParamStr")

#        output = numpy.empty((6,len(varParams)))

#        print(varParams)
#        print(output)

#        if len(varParams) > 0:
#            print('here_before')
#            deltaMag = self.applyVariability(varParams)
#            print('here')
#            output = deltaMag

#        for ii, vv in enumerate(varParams):
#            print(vv, type(vv))
#            if vv != numpy.unicode_("None") and \
#               self.obs_metadata is not None and \
#               self.obs_metadata.mjd is not None:

#                deltaMag = self.applyVariability(vv)

#                output[0][ii] = deltaMag["u"]
#                output[1][ii] = deltaMag["g"]
#                output[2][ii] = deltaMag["r"]
#                output[3][ii] = deltaMag["i"]
#                output[4][ii] = deltaMag["z"]
#                output[5][ii] = deltaMag["y"]
#            else:
#                output[0][ii] = 0.0
#                output[1][ii] = 0.0
#                output[2][ii] = 0.0
#                output[3][ii] = 0.0
#                output[4][ii] = 0.0
#                output[5][ii] = 0.0

#        return output
    pass
