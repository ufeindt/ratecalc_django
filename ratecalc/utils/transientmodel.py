import os
import numpy as np
import sncosmo
from scipy.interpolate import RectBivariateSpline as Spline2d
from scipy.optimize import newton

from rates import _cosmo
from ratecalc_django.settings import BASE_DIR

def _get_built_in_model_(sncosmo_name='salt2', amplitude=None, **kwargs):
    """
    """
    model = sncosmo.Model(source=sncosmo_name)
    if amplitude is not None:
        amp_or_x0 = ('amplitude' if 'amplitude' in model.param_names else 'x0')
        model.set(**{amp_or_x0: amplitude})
        
    return model

def _get_model_from_file_(model_file=None, **kwargs):
    return load_sed_model(os.path.join(BASE_DIR, model_file))

_transient_loaders = {
    'built-in': _get_built_in_model_,
    'load-file': _get_model_from_file_,
    }
    
def get_transient_model(model_type='built-in', **kwargs):
    """
    """
    model = _transient_loaders[model_type](**kwargs)

    if kwargs.get('host_extinction', False):
        model.add_effect(sncosmo.CCM89Dust(), 'host', 'rest')
        model.set(hostr_v=2.)
    model.add_effect(sncosmo.CCM89Dust(), 'mw', 'obs')
        
    return model
                          
def scale_model(model, mag=None, band='bessellb', magsys='vega',
                return_amplitude=False):
    z = model.get('z')
    amp_or_x0 = ('amplitude' if 'amplitude' in model.param_names else 'x0')
    if mag is not None:
        dm = model._source.peakmag(band, magsys) - mag
    else:
        dm = 0
        
    if z > 0:
        d_l = _cosmo.luminosity_distance(z).value * 1e5
    else:
        d_l = 1
        
    model.set(**{amp_or_x0: model.get(amp_or_x0) * 10**(0.4*dm) * d_l**-2})

    if return_amplitude:
        return model.get(amp_or_x0)
    return model

def get_z_from_dist(d_l):
    if d_l == 1e-5:
        return 0.
    z_guess = d_l * _cosmo.H0.value / 3e5

    f_newton = lambda z: _cosmo.luminosity_distance(z).value - d_l

    return np.round(newton(f_newton, z_guess), 7)
    
class TimeSeriesSource(sncosmo.Source):
    """A single-component spectral time series model.
    The spectral flux density of this model is given by
    .. math::
       F(t, \lambda) = A \\times M(t, \lambda)
    where _M_ is the flux defined on a grid in phase and wavelength
    and _A_ (amplitude) is the single free parameter of the model. The
    amplitude _A_ is a simple unitless scaling factor applied to
    whatever flux values are used to initialize the
    ``TimeSeriesSource``. Therefore, the _A_ parameter has no
    intrinsic meaning. It can only be interpreted in conjunction with
    the model values. Thus, it is meaningless to compare the _A_
    parameter between two different ``TimeSeriesSource`` instances with
    different model data.
    Parameters
    ----------
    phase : `~numpy.ndarray`
        Phases in days.
    wave : `~numpy.ndarray`
        Wavelengths in Angstroms.
    flux : `~numpy.ndarray`
        Model spectral flux density in erg / s / cm^2 / Angstrom.
        Must have shape ``(num_phases, num_wave)``.
    zero_before : bool, optional
        If True, flux at phases before minimum phase will be zeroed. The
        default is False, in which case the flux at such phases will be equal
        to the flux at the minimum phase (``flux[0, :]`` in the input array).
    name : str, optional
        Name of the model. Default is `None`.
    version : str, optional
        Version of the model. Default is `None`.
    """

    _param_names = ['amplitude']
    param_names_latex = ['A']

    def __init__(self, phase, wave, flux, zero_before=False, name=None,
                 version=None, kx=2, ky=2):
        self.name = name
        self.version = version
        self._phase = phase
        self._wave = wave
        self._parameters = np.array([1.])
        self._model_flux = Spline2d(phase, wave, flux, kx=kx, ky=ky)
        self._zero_before = zero_before

    def _flux(self, phase, wave):
        f = self._parameters[0] * self._model_flux(phase, wave)
        
        if self._zero_before:
            mask = np.atleast_1d(phase) < self.minphase()
            f[mask, :] = 0.

        return f
    
def load_sed_model(filename, p_min=5e-4, p_max=50, **kwargs):
    """
    """
    # sed = np.genfromtxt(filename)

    # phase = np.unique(sed[:,0])
    # if p_min is not None:
    #     phase = phase[(phase >= p_min)]
    # if p_max is not None:
    #     phase = phase[(phase <= p_max)]
        
    # wave = sed[sed[:,0] == phase[0]][:,1]
    # # Spectral flux density is in [erg s^-1 cm^-3] but need [erg s^-1 cm^-2 Angstrom^-1]
    # # Multiply by 1e-8
    # flux = np.array([sed[sed[:,0] == p,2] for p in phase]) * 1e-8

    phase, wave, flux = sncosmo.read_griddata_ascii(filename)

    k0, k1 = 0, -1
    if p_min is not None:
        if phase[0] < p_min:
            k0 = np.where(phase < p_min)[0][-1] + 1

    if p_max is not None:
        if phase[-1] > p_max:
            k1 = np.where(phase > p_max)[0][0]

    print k0, k1

    source = TimeSeriesSource(phase[k0:k1], wave, flux[k0:k1], **kwargs)

    return sncosmo.Model(source=source)
