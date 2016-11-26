import sncosmo

from rates import _cosmo

def _get_built_in_model_(name, M_B_max=None, **kwargs):
    """
    """
    model = sncosmo.Model(source=name)
    if M_B_max is not None:
        model = scale_model(model, mag=M_B_max)
        
    return model

_transient_loaders = {
    'built-in': _get_built_in_model_
    }
    
def get_transient_model(name, model_type='built-in', model_file=None, M_B_max=None):
    """
    """
    return _transient_loaders[model_type](name, model_file=model_file,
                                          M_B_max=M_B_max)

def scale_model(model, mag=None, band='bessellb', magsys='vega'):
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
    
    return model
        