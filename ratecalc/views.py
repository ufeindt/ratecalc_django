# import inspect
import numpy as np

from django.shortcuts     import render
from django.core.urlresolvers import resolve

from ratecalc.models      import TransientModels
from ratecalc.forms       import TransientForm, _band_dict

from utils.lightcurve     import get_lightcurves
from utils.plot           import plot_lightcurve, plot_expected, plot_redshift
from utils.rates          import RateCalculator
from utils.transientmodel import get_transient_model


# Create your views here.

def index(request):
    tm_list = TransientModels.objects.all()
    context_dict = {'transient_models': tm_list}
    
    return render(request, 'ratecalc/index.html', context=context_dict)

def about(request):
    return render(request, 'ratecalc/about.html', context={})
    
def show_lightcurve(request, tm_name, n_bands=5):
    context = get_calc(request, tm_name,
                       [], n_bands=n_bands,
                       band='bessellux', magsys='ab')

    bands = [context['calc_kw']['band']]
    magsys = [context['calc_kw']['magsys']]
    
    bands.extend([context['calc_kw'].pop('band%i'%k, 'None')
                  for k in range(1, n_bands)])
    magsys.extend([context['calc_kw'].pop('magsys%i'%k, 'ab')
                   for k in range(1, n_bands)])

    magsys = [ms for ms, b in zip(magsys, bands) if b != 'None']
    bands = [b for b in bands if b != 'None']
    labels = [_band_dict[b] for b in bands]

    transient_model = context['calc_args'][0]
    phase, mags = get_lightcurves(transient_model, bands, magsys)
    plot = plot_lightcurve(phase, mags, labels)

    context['plot'] = plot
        
    return render(request, 'ratecalc/form_plot.html', context)
    
def show_expected(request, tm_name, n_bands=5):
    context = get_calc(request, tm_name,
                       ['mag_start', 'mag_lim', 't_before',
                        'rate', 'mag_max', 'mag_disp'],
                       hide_param=['z'], band='bessellux', magsys='ab',
                       mag_start=19., mag_lim=24., t_before=0., n_bands=n_bands)

    add_bands = [context['calc_kw'].pop('band%i'%k, 'None')
                 for k in range(1, n_bands)]
    add_magsys = [context['calc_kw'].pop('magsys%i'%k, 'ab')
                  for k in range(1, n_bands)]
    
    
    calc = RateCalculator(*context['calc_args'], **context['calc_kw'])
    
    mag_lim = calc.mag_lim
    if calc.mag_disp is not None:
        mag_lim -= calc.sigma_cut * calc.mag_disp
        
    mag = np.linspace(context['mag_start'], mag_lim, 41)
    n = [[calc.get_n_expected(m) for m in mag]]
    labels = [_band_dict[calc.band]]

    for b, ms in zip(add_bands, add_magsys):
        if b != 'None':
            context['calc_kw']['band'] = b
            context['calc_kw']['magsys'] = ms
            calc = RateCalculator(*context['calc_args'], **context['calc_kw'])
            
            n.append([calc.get_n_expected(m) for m in mag])
            labels.append(_band_dict[calc.band])
    
    plot = plot_expected(mag, n, labels)

    context['plot'] = plot
        
    return render(request, 'ratecalc/form_plot.html', context)

def show_redshift(request, tm_name):
    context = get_calc(request, tm_name,
                       ['mag_lim', 't_before',
                        'rate', 'mag_max', 'mag_disp'],
                       hide_param=['z'], band='bessellux', magsys='ab',
                       mag_lim=24., t_before=0.)

    calc = RateCalculator(*context['calc_args'], **context['calc_kw'])
    
    z, n = calc.get_z_dist(context['calc_kw']['mag_lim'])
    plot = plot_redshift(z, n)

    context['plot'] = plot
        
    return render(request, 'ratecalc/form_plot.html', context)
    
    
def get_calc(request, tm_name, include_fields, mag_start=None, hide_param=None,
             n_bands=1, **kw):
    if hide_param is None:
        hide_param = []
        
    tm = TransientModels.objects.get(name=tm_name)
    transient_model = get_transient_model(tm.sncosmo_name)
    calc_kw = {'mag_max': tm.m_B_max,
               'mag_disp': tm.sig_m_B_max,
               'rate': tm.rate}
    
    form = TransientForm(transient_model=transient_model, hide_param=hide_param,
                         n_bands=n_bands, include_fields=include_fields, **calc_kw)
        
    if request.method == 'POST':
        form = TransientForm(request.POST, transient_model=transient_model,
                             hide_param=hide_param, n_bands=n_bands,
                             include_fields=include_fields, **calc_kw)

        if not form.is_valid():
            print(form.errors)
 
        transient_model.set(**{k: v for k, v in form.cleaned_data.items()
                               if k in transient_model.param_names})

        #if mag_start is not None:
        mag_start = form.cleaned_data.pop('mag_start', mag_start)
            
        for k, v in form.cleaned_data.items():
            if k not in transient_model.param_names:
                calc_kw[k] = v
    else:
        for k, v in kw.items():
            calc_kw[k] = v

    rate = calc_kw.pop('rate')
    calc_kw['ratefunc'] = lambda z: rate

    context = {'tm': tm, 'form': form, 'mag_start': mag_start,
               'action': resolve(request.path_info).url_name,
               'calc_kw': calc_kw, 'calc_args': (transient_model, )}
    
    return context

        