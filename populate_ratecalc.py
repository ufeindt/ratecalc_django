import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ratecalc_django.settings')

import django
django.setup()

from ratecalc.models import TransientModel, TransientType, Category
from ratecalc.utils.transientmodel import get_transient_model, scale_model
from collections import OrderedDict as odict

def populate():
    categories = odict()
    categories['sncosmo-built-in'] = {
        'description': 'sncosmo built-in models',
        'model_type': 'built-in'
    }
    categories['mne-rosswog-et-al'] = {
        'description': 'Macronova SEDs from Rosswog et al. (in prep.)',
        'model_type': 'load-file'
    }
    
    types = odict()
    types['SN Ia'] = {'m_B_max': -19.25, 'sig_m_B_max': 0.5, 'rate': 3e-5}
    types['SN Ib'] = {'m_B_max': -17.45, 'sig_m_B_max': 1.12, 'rate': 1e-5}
    types['SN Ic'] = {'m_B_max': -17.66, 'sig_m_B_max': 1.18, 'rate': 1e-5}
    types['SN IIb'] = {'m_B_max': -16.99, 'sig_m_B_max': 0.92, 'rate': 1e-5}
    types['SN IIL'] = {'m_B_max': -17.98, 'sig_m_B_max': 0.86, 'rate': 1e-5}
    types['SN IIP'] = {'m_B_max': -16.75, 'sig_m_B_max': 0.98, 'rate': 1.5e-4}
    types['SN IIn'] = {'m_B_max': -18.53, 'sig_m_B_max': 1.36, 'rate': 1e-5}
    types['Macronova'] = {'m_B_max': -10.0, 'sig_m_B_max': 0., 'rate': 3e-7}
            
    models = odict()
    models['salt2'] = {
        'description': 'SALT2.4',
        'sncosmo_name': 'salt2',
        'sncosmo_version': '2.4',
        'transient_type': 'SN Ia',
        'category': 'sncosmo-built-in',
        'host_extinction': False,
    }

    snana_names = [
        #'2004fe', '2004gq', 'sdss004012', '2006fo', 'sdss014475',
        #'2006lc', '04d1la', '04d4jv', '2004gv', '2006ep',
        #'2007y', '2004ib', '2005hm', '2006jo', '2007nc',
        '2004hx',
        #'2005gi', '2006gq', '2006kn', '2006jl'
    ]
    snana_types = [
        #'SN Ic', 'SN Ic', 'SN Ic', 'SN Ic', 'SN Ic',
        #'SN Ic', 'SN Ic', 'SN Ic', 'SN Ib', 'SN Ib',
        #'SN Ib', 'SN Ib', 'SN Ib', 'SN Ib', 'SN Ib',
        'SN IIP',
        #'SN IIP', 'SN IIP', 'SN IIP', 'SN IIP'
    ]

    for snana_name, snana_type in zip(snana_names, snana_types):
        models['snana-%s'%snana_name] = {
            'description':  'SNANA %s'%snana_name,
            'sncosmo_name': 'snana-%s'%snana_name,
            'sncosmo_version': '1.0',
            'transient_type': snana_type,
            'category': 'sncosmo-built-in',
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
    mn_files = [
        'SED_DZ31_ns12ns12.dat',
        'SED_DZ31_ns13ns13.dat',
        'SED_DZ31_ns14ns14.dat',
        'SED_DZ31_ns12ns14.dat',
        'SED_DZ31_ns14ns18.dat',
        'SED_DZ31_NSBH1.dat',
        'SED_DZ31_NSBH2.dat',
        'SED_DZ31_NSBH3.dat',
        'SED_DZ31_NSBH3_kappa100.dat',
    ]
    mn_names = [
        'mn-ns12n12-dz31',
        'mn-ns13n13-dz31',
        'mn-ns14n14-dz31',
        'mn-ns12n14-dz31',
        'mn-ns14n18-dz31',        
        'mn-nsbh1-dz31',
        'mn-nsbh2-dz31',
        'mn-nsbh3-dz31',
        'mn-nsbh3-dz31-kappa100'
    ]
    mn_descriptions = [
        'ns12ns12 (N1, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'ns13ns13 (N2, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'ns14ns14 (N3, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'ns12ns14 (N4, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'ns14ns18 (N5, MNmodel2, DZ31, kappa = 10 cm^2/g)',        
        'ns14b7 (B1, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'ns14b7 (B2, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'ns12b7 (B3, MNmodel2, DZ31, kappa = 10 cm^2/g)',
        'ns12b7 (B3, MNmodel2, DZ31, kappa = 100 cm^2/g)',
    ]
    for k in xrange(1, 22):
         mn_names.append('mn-wind%i'%k)
         kappa = (10 if k in [11, 12] else 1)
         mn_descriptions.append('wind%i (kappa = %i cm^2/g)'%(k, kappa))
         if kappa == 1:
             mn_files.append('SED_wind%i.dat'%k)
         else:
             mn_files.append('SED_wind%i_kappa10.dat'%k)

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