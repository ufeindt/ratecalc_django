import sncosmo

def _get_built_in_model_(name, **kwargs):
    """
    """
    return sncosmo.Model(source=name)

_transient_loaders = {
    'built-in': _get_built_in_model_
    }
    
def get_transient_model(name, model_type='built-in', model_file=None):
    """
    """
    return _transient_loaders[model_type](name, model_file=model_file)