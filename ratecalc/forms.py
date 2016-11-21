import copy

from django import forms
#from ratecalc.models import TransientModels

_magsys = (
    ('ab', 'AB'),
    ('vega', 'Vega'),
)

_bands = (
    ('None', 'None'),
    ('bessellux', 'U'),
    ('bessellb', 'B'),
    ('bessellv', 'V'),
    ('bessellr', 'R'),
    ('besselli', 'I'),
    ('sdssu', 'SDSS u'),
    ('sdssg', 'SDSS g'),
    ('sdssr', 'SDSS r'),
    ('sdssi', 'SDSS i'),
    ('sdssz', 'SDSS z'),
)

_avalaible_fields = {
    'mag_start': forms.FloatField(initial=19, help_text='m_start'),
    'mag_lim': forms.FloatField(initial=24, help_text='m_lim'),        
    't_before': forms.FloatField(initial=0.,help_text='t_before'),        
    'first_band': forms.ChoiceField(choices=_bands[1:],help_text='Band'),
    'band': forms.ChoiceField(choices=_bands,help_text='Band'),
    'magsys': forms.ChoiceField(choices=_magsys, help_text=''),#'Magsys'),
    'mag_max': forms.FloatField(initial=-19.3, help_text='m_B_max (Vega)'),
    'mag_disp': forms.FloatField(initial=0.4, help_text='sig_m_B_max'),
    'rate': forms.FloatField(initial=3e-5, help_text='Rate [Mpc^-3 yr^-1]'),
}

class TransientForm(forms.Form):
    """
    Basic form for setting the transient model parameter
    """
    def __init__(self,*args,**kwargs):
        self.transient_model = kwargs.pop('transient_model')
        self.hide_param = kwargs.pop('hide_param')
        self.n_bands = kwargs.pop('n_bands', 1)
        self.include_fields = kwargs.pop('include_fields')
        
        self.field_defaults = {}
        for k in _available_fields.keys():
            if k in kwargs.keys():
                self.field_defaults[k] = kwargs.pop(k)
        
        super(TransientForm, self).__init__(*args, **kwargs)

        min_max_vals = {
            'z': (0, None),
            'amplitude': (0, None),
            'x0': (0, None)
        }
        self.model_fields = []
        for name, value in zip(self.transient_model.param_names,
                               self.transient_model.parameters):
            if name not in hide_param:
                self.model_fields.append(name)
                min_max = min_max_vals.get(name, (None, None))
                self.fields[name] = forms.FloatField(
                    min_value=min_max[0],
                    max_value=min_max[1],
                    initial=value,
                    help_text=name
                )

        self.field_blocks = []
                
        self.fields['band'] = copy.copy(_avalaible_fields['first_band'])
        self.fields['magsys'] = copy.copy(_avalaible_fields['mag_sys'])        
        if self.n_bands > 1:
            self.field_blocks.append(['band', 'magsys'])
            for k in range(1, self.n_bands):
                self.fields['band%i'%k] = copy.copy(_avalaible_fields['band'])
                self.fields['magsys%i'%k] = copy.copy(_avalaible_fields['mag_sys'])
                self.field_blocks[-1].extend(['band%i'%k, 'magsys%i'%k])

        self.field_blocks.append([])
        for name in self.include_fields:
            self.fields[name] = copy.copy(_avalaible_fields[name])
            self.field_blocks[-1].append(name)

            if name in self.field_defaults.keys():
                self.fields[name].initial = self.field_defaults[name]

    def model_fields_generator(self):
        for name in self.model_fields:
            yield self.fields[name]
        
    def field_blocks_generator(self):
        for block in self.field_blocks:
            yield self.field_block_generator(block)
        
    def field_block_generator(self, block):
        for name in block:
            yield self.fields[name]
                
class TransientFormOld(forms.Form):
    """
    Basic form for setting the transient model parameter
    """
    def __init__(self,*args,**kwargs):
        self.transient_model = kwargs.pop('transient_model')
        super(TransientFormOld,self).__init__(*args,**kwargs)

        min_max_vals = {
            'z': (0, None),
            'amplitude': (0, None),
            'x0': (0, None)
        }
        for name, value in zip(self.transient_model.param_names,
                               self.transient_model.parameters):
            min_max = min_max_vals.get(name, (None, None))
            self.fields[name] = forms.FloatField(
                min_value=min_max[0],
                max_value=min_max[1],
                initial=value,
                help_text=name
            )

class LightcurveForm(TransientFormOld):
    def __init__(self,*args,**kwargs):
        super(LightcurveForm,self).__init__(*args,**kwargs)

        self.fields['band'] = forms.ChoiceField(choices=_bands,
                                                help_text='Band')
        self.fields['magsys'] = forms.ChoiceField(choices=_magsys,
                                                  help_text='Magsys')


class ExpectedForm(TransientFormOld):
    def __init__(self,*args,**kwargs):
        self.mag_max = kwargs.pop('mag_max', -19.3)
        self.mag_disp = kwargs.pop('mag_disp', 0.4)
        self.rate = kwargs.pop('rate', 3e-5)
        
        super(ExpectedForm,self).__init__(*args,**kwargs)

        self.fields['mag_start'] = forms.FloatField(
            initial=19,
            help_text='m_start'
        )        
        self.fields['mag_lim'] = forms.FloatField(
            initial=24,
            help_text='m_lim'
        )        
        self.fields['t_before'] = forms.FloatField(
            initial=0.,
            help_text='t_before'
        )        

        self.fields['band'] = forms.ChoiceField(choices=_bands,
                                                help_text='Band')
        self.fields['magsys'] = forms.ChoiceField(choices=_magsys,
                                                  help_text='Magsys')

        self.fields['mag_max'] = forms.FloatField(
            initial=self.mag_max,
            help_text='m_B_max (Vega)'
        )
        self.fields['mag_disp'] = forms.FloatField(
            initial=self.mag_disp,
            help_text='sig_m_B_max'
        )
        self.fields['rate'] = forms.FloatField(
            initial=self.rate,
            help_text='Rate [Mpc^-3 yr^-1]'
        )
