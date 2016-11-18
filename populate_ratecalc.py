import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ratecalc_django.settings')

import django
django.setup()

from ratecalc.models import TransientModels

def populate():
    models = {
        'salt2-2-4': {
            'description': 'SALT2.4 (Betoule et al. 2014)',
            'sncosmo_name': 'salt2',
            'sncosmo_version': '2.4',
            'transient_type': 'SN Ia',
            'm_B_max': -19.3,
            'sig_m_B_max': 0.4,
            'rate': 3e-5,
            'model_type': 'built-in',
        },
        'snana-2007ms': {
            'description':  'SNANA 2004hx (SN IIP)',
            'sncosmo_name': 'snana-2004hx',
            'sncosmo_version': '1.0',
            'transient_type': 'SN IIP',
            'm_B_max': -16.75,
            'sig_m_B_max': 0.98,
            'rate': 1.5e-4,
            'model_type': 'built-in',
        }
    }
    
    for name, kw in models.items():
        add_model(name, **kw)

    # Print out the categories we have added.
    for tm in TransientModels.objects.all():
            print("- {0}".format(str(tm)))

def add_model(name, **kwargs):
    tm = TransientModels.objects.get_or_create(name=name, **kwargs)[0]
    tm.save()


# Start execution here!
if __name__ == '__main__':
    print("Starting Ratecalc population script...") 
    populate()