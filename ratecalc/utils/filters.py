import os
import numpy as np
import sncosmo

from ratecalc_django.settings import BASE_DIR

def load_filters():
    filter_dir = os.path.join(BASE_DIR, 'ratecalc/utils/filters')
    for filename in os.listdir(filter_dir):
        data = np.genfromtxt('%s/%s'%(filter_dir, filename))
        name = filename.split('.')[0]
        band = sncosmo.Bandpass(data[:,0], data[:,1], name=name)
        sncosmo.registry.register(band, force=True)