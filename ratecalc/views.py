# import inspect
import numpy as np

from django.shortcuts     import render
from django.core.urlresolvers import resolve

from ratecalc.models      import TransientModels
from ratecalc.forms       import LightcurveForm, ExpectedForm

from utils.lightcurve     import get_lightcurve
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

def show_lightcurve(request, tm_name):
    tm = TransientModels.objects.get(name=tm_name)
    transient_model = get_transient_model(tm.sncosmo_name)
    form = LightcurveForm(transient_model=transient_model)
    #print form.fields['bandpass'].initial
    
    if request.method == 'POST':
        form = LightcurveForm(request.POST,transient_model=transient_model)

        if not form.is_valid():
            print(form.errors)
 
        transient_model.set(**{k: v for k, v in form.cleaned_data.items()
                               if k in transient_model.param_names})

        band = form.cleaned_data['band']
        magsys = form.cleaned_data['magsys']
    else:
        band = 'bessellux'
        magsys = 'ab'
        
    phase, mag = get_lightcurve(transient_model, band, magsys)
    plot = plot_lightcurve(phase, mag)
        
    return render(request, 'ratecalc/lightcurve.html',
                  {'tm': tm, 'form': form, 'plot': plot,
                   'action': resolve(request.path_info).url_name})

def show_expected(request, tm_name):
    context = get_calc(request, tm_name, band='bessellux', magsys='ab',
                       mag_start=19., mag_lim=24., t_before=0.)

    calc = RateCalculator(*context['calc_args'], **context['calc_kw'])
    
    mag_lim = calc.mag_lim
    if calc.mag_disp is not None:
        mag_lim -= calc.sigma_cut * calc.mag_disp
        
    mag = np.linspace(context['mag_start'], mag_lim, 41)
    n = [calc.get_n_expected(m) for m in mag]
    plot = plot_expected(mag, n)

    context['plot'] = plot
        
    return render(request, 'ratecalc/lightcurve.html', context)

def show_redshift(request, tm_name):
    context = get_calc(request, tm_name, band='bessellux', magsys='ab',
                       mag_lim=24., t_before=0.)

    calc = RateCalculator(*context['calc_args'], **context['calc_kw'])
    
    z, n = calc.get_z_dist(context['calc_kw']['mag_lim'])
    plot = plot_redshift(z, n)

    context['plot'] = plot
        
    return render(request, 'ratecalc/lightcurve.html', context)
    
def get_calc(request, tm_name, mag_start=None, **kw):
    tm = TransientModels.objects.get(name=tm_name)
    transient_model = get_transient_model(tm.sncosmo_name)
    calc_kw = {'mag_max': tm.m_B_max,
               'mag_disp': tm.sig_m_B_max,
               'rate': tm.rate}
    
    form = ExpectedForm(transient_model=transient_model, **calc_kw)
        
    if request.method == 'POST':
        form = ExpectedForm(request.POST, transient_model=transient_model,
                            **calc_kw)

        if not form.is_valid():
            print(form.errors)
 
        transient_model.set(**{k: v for k, v in form.cleaned_data.items()
                               if k in transient_model.param_names})

        if mag_start is not None:
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

# def get_default_args(func):
#     """
#     returns a dictionary of arg_name:default_values for the input function
#     """
#     args, varargs, keywords, defaults = inspect.getargspec(func)
#     return dict(zip(args[-len(defaults):], defaults))

# def get_calc_kw(**kw):
#     """
#     Make dictionary
#     """
#     pass
        