import numpy as np

def get_lightcurve(model, band, magsys, npoints=100):
    if npoints is None:
        phase = model._source._phase * (1 + model.get('z')) + model.get('t0')
    else:
        phase = np.linspace(model.mintime(), model.maxtime(), npoints)
        
    mag = model.bandmag(band, magsys, phase)
    
    return phase, mag