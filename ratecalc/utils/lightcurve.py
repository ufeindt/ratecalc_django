import numpy as np

from filters import load_filters
from scipy.interpolate import InterpolatedUnivariateSpline as Spline1d

def get_lightcurves(model, bands, magsys, t_range=None, log_t=False, n_points=100):
    load_filters()

    if t_range is None:
        t_range = (model.mintime(), model.maxtime())
    
    p_interp = model._source._phase * (1 + model.get('z'))
    p0 = (p_interp[p_interp <= t_range[0]][-1]
          if np.any(p_interp <= t_range[0])
          else model.mintime()) 
    p1 = (p_interp[p_interp >= t_range[1]][-1]
          if np.any(p_interp >= t_range[1])
          else model.maxtime())
    p_interp = p_interp[(p_interp >= p0) & (p_interp <= p1)]

    if log_t is False:
        phase = np.linspace(t_range[0], t_range[1], n_points)
    else:
        phase = np.logspace(np.log10(t_range[0]), np.log10(t_range[1]), n_points)

    mags = []
    for b, ms in zip(bands, magsys):    
        m_interp = model.bandmag(b, ms, p_interp)
        mask = ~np.isnan(m_interp)
        f_interp = Spline1d(p_interp[mask], m_interp[mask])
        mags.append(f_interp(phase))
        
    return phase, mags