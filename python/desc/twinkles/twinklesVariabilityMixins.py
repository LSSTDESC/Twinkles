from __future__ import absolute_import, division, print_function
import numpy as np
import math
import numbers
import json
import ast
import copy
from scipy.interpolate import interp1d
from lsst.sims.catalogs.decorators import register_class, register_method, compound
from lsst.sims.catUtils.mixins import Variability, ExtraGalacticVariabilityModels
from lsst.sims.catUtils.mixins.VariabilityMixin import _VariabilityPointSources

__all__ = ["TimeDelayVariability", "VariabilityTwinkles"]


class TimeDelayVariability(Variability):

    @register_method("applyAgnTimeDelay")
    def applyAgnTimeDelay(self, valid_dexes, params, expmjd,
                          variability_cache=None, redshift=None):

        if redshift is None:
            redshift_arr = self.column_by_name('redshift')
        else:
            redshift_arr = redshift

        if len(params) == 0:
            return np.array([[],[],[],[],[],[]])

        if isinstance(expmjd, numbers.Number):
            dMags = np.zeros((6, self.num_variable_obj(params)))
            expmjd_arr = np.array([expmjd])
        else:
            dMags = np.zeros((6, self.num_variable_obj(params), len(expmjd)))
            expmjd_arr = expmjd

        seed_arr = params['seed']
        t_delay_arr = params['t0Delay'].astype(float)
        tau_arr = params['agn_tau'].astype(float)
        sfu_arr = params['agn_sfu'].astype(float)
        sfg_arr = params['agn_sfg'].astype(float)
        sfr_arr = params['agn_sfr'].astype(float)
        sfi_arr = params['agn_sfi'].astype(float)
        sfz_arr = params['agn_sfz'].astype(float)
        sfy_arr = params['agn_sfy'].astype(float)

        start_date = 58580.0
        duration_observer_frame = expmjd_arr.max() - start_date

        if duration_observer_frame < 0 or expmjd_arr.min() < start_date:
            raise RuntimeError("WARNING: Time offset greater than minimum epoch.  " +
                               "Not applying variability. "+
                               "expmjd: %e should be > start_date: %e  " % (expmjd.min(), start_date) +
                               "in applyAgn variability method")

        for i_obj in valid_dexes[0]:

            seed = seed_arr[i_obj]
            tau = tau_arr[i_obj]
            time_dilation = 1.0+redshift_arr[i_obj]
            t_delay = t_delay_arr[i_obj]

            sfint = {}
            sfint['u'] = sfu_arr[i_obj]
            sfint['g'] = sfg_arr[i_obj]
            sfint['r'] = sfr_arr[i_obj]
            sfint['i'] = sfi_arr[i_obj]
            sfint['z'] = sfz_arr[i_obj]
            sfint['y'] = sfy_arr[i_obj]

            rng = np.random.RandomState(seed)

            dt = tau/100.
            duration_rest_frame = duration_observer_frame/time_dilation
            nbins = int(math.ceil(duration_rest_frame/dt))+1

            time_dexes = np.round((expmjd_arr-start_date-t_delay)/(time_dilation*dt)).astype(int)
            time_dex_map = {}
            ct_dex = 0
            for i_t_dex, t_dex in enumerate(time_dexes):
                if t_dex in time_dex_map:
                    time_dex_map[t_dex].append(i_t_dex)
                else:
                    time_dex_map[t_dex] = [i_t_dex]
            time_dexes = set(time_dexes)

            dx2 = 0.0
            x1 = 0.0
            x2 = 0.0

            dt_over_tau = dt/tau
            es = rng.normal(0., 1., nbins)*math.sqrt(dt_over_tau)
            for i_time in range(nbins):
                #The second term differs from Zeljko's equation by sqrt(2.)
                #because he assumes stdev = sfint/sqrt(2)
                dx1 = dx2
                dx2 = -dx1*dt_over_tau + sfint['u']*es[i_time] + dx1
                x1 = x2
                x2 += dt

                if i_time in time_dexes:
                    if isinstance(expmjd, numbers.Number):
                        dm_val = ((expmjd-start_date)*(dx1-dx2)/time_dilation+dx2*x1-dx1*x2)/(x1-x2)
                        dMags[0][i_obj] = dm_val
                    else:
                        for i_time_out in time_dex_map[i_time]:
                            local_end = (expmjd_arr[i_time_out]-start_date)/time_dilation
                            dm_val = (local_end*(dx1-dx2)+dx2*x1-dx1*x2)/(x1-x2)
                            dMags[0][i_obj][i_time_out] = dm_val

        for i_filter, filter_name in enumerate(('g', 'r', 'i', 'z', 'y')):
            for i_obj in valid_dexes[0]:
                dMags[i_filter+1][i_obj] = dMags[0][i_obj]*params['agn_sf%s' % filter_name][i_obj]/params['agn_sfu'][i_obj]

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

    pass
