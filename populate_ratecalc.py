import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ratecalc_django.settings')

import django
django.setup()

from ratecalc.models import TransientModel, TransientType, Category
from ratecalc.utils.transientmodel import get_transient_model, scale_model
from collections import OrderedDict as odict

def populate():
    categories = {
        'sncosmo-built-in': {
            'description': 'sncosmo built-in models',
            'model_type': 'built-in'
        },
        'mne-rosswog-et-al': {
            'description': 'Macronova SEDs from Rosswog et al. (in prep.)',
            'model_type': 'load-file'
        },
    }
    
    types = {
        'SN Ia': {
            'm_B_max': -19.3,
            'sig_m_B_max': 0.4,
            'rate': 3e-5,        
        },
        'SN IIP': {
            'm_B_max': -16.75,
            'sig_m_B_max': 0.98,
            'rate': 1.5e-4,
        },
        'Macronova': {
            'm_B_max': -10.0,
            'sig_m_B_max': 0.,
            'rate': 3e-7,
        },
    }
            
    models = {
        'salt2': {
            'description': 'SALT2.4',
            'sncosmo_name': 'salt2',
            'sncosmo_version': '2.4',
            'transient_type': 'SN Ia',
            'category': 'sncosmo-built-in',
            'host_extinction': False,
        },
        'snana-2004hx': {
            'description':  'SNANA 2004hx',
            'sncosmo_name': 'snana-2004hx',
            'sncosmo_version': '1.0',
            'transient_type': 'SN IIP',
            'category': 'sncosmo-built-in',
        }
    }

    c = {}
    for name, kw in categories.items():
        c[name] = add_category(name, **kw)

    t = {}
    for name, kw in types.items():
        t[name] = add_type(name, **kw)
    
    for name, kw in models.items():
        add_model(name, c[kw.pop('category')], t[kw.pop('transient_type')], **kw)

    mn_dir = 'ratecalc/utils/macronova'
    mn_files = ['SED_DZ31_NSBH3.dat', 'SED_wind20.dat']
    mn_names = ['mn-nsbh3-dz31', 'mn-wind20']
    mn_descriptions = [
        'ns12b7 (B3, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'wind20 (kappa = 1 cm^2/g)'
    ]
    for mn_file, mn_name, mn_description in zip(mn_files, mn_names, mn_descriptions):
        add_model(mn_name, c['mne-rosswog-et-al'], t['Macronova'],
                  description=mn_description, default_amplitude=1.,
                  model_file='%s/%s'%(mn_dir, mn_file))
        
    # Print out the categories we have added.
    for tm in TransientModel.objects.all():
            print("- {0}".format(str(tm)))

def add_category(name, **kwargs):
    c = Category.objects.get_or_create(name=name, **kwargs)[0]
    c.save()

    return c
    
def add_type(name, **kwargs):
    t = TransientType.objects.get_or_create(name=name, **kwargs)[0]
    t.save()

    return t
    
def add_model(name, c, t, **kwargs):
    if 'default_amplitude' not in kwargs.keys():
        model = get_transient_model(sncosmo_name=kwargs.get('sncosmo_name', None),
                                    model_file=kwargs.get('model_file', None),
                                    model_type=c.model_type)
        kwargs['default_amplitude'] = scale_model(model, mag=t.m_B_max,
                                                  return_amplitude=True)
        
    tm = TransientModel.objects.get_or_create(name=name, category=c,
                                              transient_type=t, **kwargs)[0]
    tm.save()

# Start execution here!
if __name__ == '__main__':
    print("Starting Ratecalc population script...") 
    populate()