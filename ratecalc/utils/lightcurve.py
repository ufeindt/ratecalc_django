import numpy as np

from filters import load_filters

def get_lightcurves(model, bands, magsys, npoints=None):
    load_filters()
    
    if npoints is None:
        phase = model._source._phase * (1 + model.get('z'))
    else:
        phase = np.linspace(model.mintime(), model.maxtime(), npoints)

    mags = []
    for b, ms in zip(bands, magsys):    
        mags.append(model.bandmag(b, ms, phase))
    
    return phase, mags