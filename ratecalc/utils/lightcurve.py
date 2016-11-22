import numpy as np

def get_lightcurves(model, bands, magsys, npoints=100):
    if npoints is None:
        phase = model._source._phase * (1 + model.get('z'))
    else:
        phase = np.linspace(model.mintime(), model.maxtime(), npoints)

    mags = []
    for b, ms in zip(bands, magsys):    
        mags.append(model.bandmag(b, ms, phase))
    
    return phase, mags