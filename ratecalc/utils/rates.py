#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import os
import cPickle
import copy

from scipy.special import erf
from scipy.integrate import romb, romberg
from scipy.interpolate import (InterpolatedUnivariateSpline as Spline1d,
                               RectBivariateSpline as Spline2d,
                               SmoothBivariateSpline as Spline2dSmooth,
                               interp2d)
from scipy.interpolate import interp2d
from scipy.optimize import minimize, newton
from astropy.cosmology import Planck15, FlatLambdaCDM
from astropy.utils.console import ProgressBar

from collections import OrderedDict as odict

import sncosmo
from sncosmo.models import Source

import warnings

#_cosmo = FlatLambdaCDM(Om0=0.3, H0=70.)
_cosmo = Planck15

############################
#                          #
# Main rates class         #
#                          #
############################
class RateCalculator(object):
    """
    """
    __nature__ = "RateCalculator"

    DO_NOT_SAVE = ['model', 'cosmo',
                   'f_mag_z', 'f_z_mag', 'ratefunc']

    def __init__(self, model, band='bessellux',
                 mag_lim=24., magsys='ab',
                 t_above=None,
                 t_before=None,
                 mag_max=None, # should be mag or (mag, band, magsys)
                 mag_disp=None,
                 sigma_cut=3.,
                 cosmo=_cosmo,
                 logz_start=-3.5, logz_step=0.05, 
                 ratefunc=(lambda z: 3e-7),
                 load=False,
                 area=100.,
                 time=365.25):
        """
        """
        self.model = copy.copy(model)
        self.cosmo = cosmo
        self.ratefunc = ratefunc
        self.amp_or_x0 = ('amplitude'
                          if 'amplitude' in model.param_names
                          else 'x0')
 
        if load is False:
            self.band = band
            self.magsys = magsys
            self.mag_disp = mag_disp
            self.sigma_cut = sigma_cut
            self.area = area
            self.time = time

            if mag_disp is None:
                self.mag_lim = mag_lim
            else:
                self.mag_lim = mag_lim + sigma_cut*mag_disp

            if mag_max is not None and type(mag_max) is not tuple:
                self.mag_max = (mag_max, 'bessellb', 'vega')
            else:
                self.mag_max = mag_max
                
            self.t_above = t_above
            self.t_before = t_before
            
            self.logz_start = logz_start
            self.logz_step = logz_step
            self._z_interp = np.array([10**self.logz_start])
            self._m_interp = np.array([self.get_mag(self._z_interp[0])])
            
            self._update_(new=True)
        else:
            self.load(load)
        
    def save(self, filename):
        """
        """
        out = {k: v for k, v in self.__dict__.items()
               if k not in self.DO_NOT_SAVE}
        
        cPickle.dump(out, open(filename, 'w'))

    def load(self, filename):
        """
        """
        loaded = cPickle.load(open(filename))

        for k, v in loaded.items():
            self.__dict__[k] = v

        self._update_(new=True)
        
    def _update_(self, new=False):
        """
        """
        self._set_z_max_()
        self._update_interpolation_(new=new)
        
    def _update_interpolation_(self, new=False):
        """
        """
        if not new:
            warnings.warn("Updating magnitude-redshift  interpolation functions")

        edge = False
        while self._m_interp[-1] < self.mag_lim and not edge:
            z_new = self._z_interp[-1] * 10**self.logz_step
            if z_new < self._z_max:
                self._z_interp = np.append(self._z_interp, z_new)
                self._m_interp = np.append(self._m_interp,
                                           self.get_mag(self._z_interp[-1]))
            else:
                edge = True
            
        self.f_mag_z = Spline1d(self._z_interp, self._m_interp)
        self.f_z_mag = Spline1d(self._m_interp, self._z_interp)

    def _check_mag_lim_(self, mag):
        """
        """
        if self.mag_disp is None:
            if mag > self.mag_lim:
                self.mag_lim = mag
                self._update_()
        else:
            if mag + self.sigma_cut*self.mag_disp > self.mag_lim:
                self.mag_lim = mag + self.sigma_cut*self.mag_disp
                self._update_()

    def _set_z_max_(self):
        """
        """
        b = sncosmo.get_bandpass(self.band)
        self._z_max = b.wave[0] / self.model.minwave() - 1
                
    def get_mag(self, z):
        """
        """
        model = self._scale_model_(z)

        if self.t_above is None:
            if self.t_before is None:
                return find_peak_phase_mag(model, self.band, magsys=self.magsys)[1]
            else:
                p_peak = find_peak_phase_mag(model, self.band, magsys=self.magsys)[0]
                return model.bandmag(self.band, self.magsys, p_peak - self.t_before)
        else:
            return find_mag_t_above(model, self.band, self.t_above,
                                    magsys=self.magsys)
        
    def get_n_expected(self, mag, nbins=100):
        """
        """
        self._check_mag_lim_(mag)

        z_max = self.f_z_mag(mag + (self.sigma_cut*self.mag_disp
                                    if self.mag_disp is not None
                                    else 0))
        sh_rate, z = shell_rate(0., z_max, self.ratefunc, nbins, self.cosmo,
                                time=self.time, area=self.area/100.)

        if self.mag_disp is not None:
            sh_rate *= cdf_gauss(self.mag_lim, self.f_mag_z(z), self.mag_disp)
        
        return np.sum(sh_rate)

    def get_z_dist(self, mag, z_bin=0.01, z_step=1e-3):
        """
        """
        self._check_mag_lim_(mag)

        z_max = self.f_z_mag(self.mag_lim)

        #print  self.mag_lim
        #print z_max
        
        nbins = int(z_max / z_step)
        sh_rate, z = shell_rate(0., nbins*z_step, self.ratefunc, nbins, self.cosmo,
                                time=self.time, area=self.area/100.)
        
        if self.mag_disp is not None:
            sh_rate *= cdf_gauss(mag, self.f_mag_z(z), self.mag_disp)

        z_binedges = np.arange(0, z_max, z_bin)    
        n = np.array([np.sum(sh_rate[(z >= z0) & (z < z1)])
                      for z0, z1 in zip(z_binedges[:-1], z_binedges[1:])])
        
        return 0.5 * (z_binedges[1:] + z_binedges[:-1]), n
            
    def _scale_model_(self, z):
        """Set the model to a certain redshift and adjust its amplitude to
        the luminosity distance. Assumes amplitude = 1 correspond to 10 pc
        """
        model = copy.copy(self.model)
        
        model.set(z=z)
        if self.mag_max is None:
            d_l = self.cosmo.luminosity_distance(z).value * 1e5
            model.set(**{self.amp_or_x0: model.get(self.amp_or_x0)*d_l**-2})
        else:
            model.set_source_peakabsmag(*self.mag_max, cosmo=self.cosmo)

        return model

            
############################
#                          #
# Lightcurve utilities     #
#                          #
############################
def cdf_gauss(x, mu, sig):
    """
    """
    return (1 + erf((x - mu)/(np.sqrt(2) * sig))) / 2
        
def find_peak_phase_mag(model, band, magsys='ab', p_init=None, sampling=1.):
    """Find peak phase and mag for transient for specific band
    and redshift
    
    returns (phase, mag)
    """ 
    
    if p_init is None:
        n_guess = int(np.ceil((model.maxtime()-model.mintime()) / sampling)) + 1
        p_guess = np.linspace(model.mintime(), model.maxtime(), n_guess)
        f_guess = -model.bandflux(band, p_guess, 30, magsys)
        p_init = p_guess[np.where(f_guess == f_guess[~np.isnan(f_guess)].min())[0]]
    
    def _fct_min(p):
        return -model.bandflux(band, p[0], 30, magsys)
         
    res = minimize(_fct_min, [p_init], bounds=[(model.mintime(), model.maxtime())])
        
    return res.x[0], -2.5 * np.log10(-res.fun) + 30
    
def t_above_lim(model, band, limit, magsys='ab', p_peak=None, m_peak=None,
                **kwargs):
    # first check that peak is above limit
    if p_peak is None and m_peak is None:
        p_peak, m_peak = find_peak_phase_mag(model, band, magsys, **kwargs)
    
    if m_peak > limit:
        return 0
    
    def _fct_new(p):
        return model.bandmag(band, magsys, p) - limit
    
    if _fct_new(model.mintime()) < 0:
        p_0 = model.mintime()
        #print 'min time'
    else:
        #p_0 = newton(_fct_new, (model.mintime() + p_peak) / 2)
        p_0 = bisection(_fct_new, model.mintime(), p_peak)
        
    if _fct_new(model.maxtime()) < 0:
        p_1 = model.maxtime()
        #print 'max time'
    else:
        #p_1 = newton(_fct_new, (model.maxtime() + p_peak) / 2)
        p_1 = bisection(_fct_new, p_peak, model.maxtime())
        
    return p_0, p_1

def find_mag_t_above(model, band, t, magsys='ab', p_peak=None, m_peak=None,
                     **kwargs):
    if p_peak is None and m_peak is None:
        p_peak, m_peak = find_peak_phase_mag(model, band, magsys, **kwargs)
    
    if t == 0.:
        return m_peak
    
    def _fct_new(p):
        return t_above_lim(model, band, p, magsys, p_peak=p_peak,
                           m_peak=m_peak, **kwargs) - t
    
    return newton(_fct_new, m_peak)

# def weighted_t_above_lim(model, z, band, limit, magsys='ab',
#                              sig=1.0, deg_gh=11, **kwargs):
#     x, w = np.polynomial.hermite.hermgauss(deg_gh)
    
#     t = np.array([t_above_lim(model, z, band, l, magsys, **kwargs)
#                   for l in np.sqrt(2) * sig * x + limit])
    
#     return np.sum(w * t / np.sqrt(np.pi))

# def find_z_max(model, band, lim, magsys='ab', sig=None, zmin=None):
#     """
#     """
#     model.set(z=0)
#     zmaxw = min(5., sncosmo.get_bandpass(band).wave[0]/model.minwave() - 1)
        
#     if sig is not None:
#         def _fct_bisect(z):
#             return lim - find_peak_phase_mag(model, z, band, magsys)[1] + 5*sig    
#     else:
#         def _fct_bisect(z):
#             return lim - find_peak_phase_mag(model, z, band, magsys)[1]
    
#     if zmin is not None and _fct_bisect(zmin) < 0:
#         return zmin
#     else:
#         return bisection(_fct_bisect, 1e-3, zmaxw)

def bisection(f, x0, x1, tol=1e-5, nmax=100):
    n = 1
    while n <= nmax:
        x2 = (x0 + x1) / 2.

        if f(x2) == 0 or (x1-x0) / 2. < tol:
            return x2
        else:
            n += 1
            if f(x2) * f(x0) > 0:
                x0 = x2
            else:
                x1 = x2
    return False

def shell_rate(zmin, zmax, ratefunc=(lambda z: 3e-7),
               nbins=100, cosmo=_cosmo, time=365.25, area=1.):
    """
    rate in Mpc^-3 yr^-1
    
    returns shell rate and bin centers
    """
    f = time / 365.25 * area
    z_binedges = np.linspace(zmin, zmax, nbins + 1)
    z_binctrs = 0.5 * (z_binedges[1:] + z_binedges[:-1])
    sphere_vols = cosmo.comoving_volume(z_binedges).value
    shell_vols = sphere_vols[1:] - sphere_vols[:-1]
    
    return (f * shell_vols * ratefunc(z_binctrs) / (1.+z_binctrs),
            z_binctrs)
