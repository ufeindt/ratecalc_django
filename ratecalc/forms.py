import copy

from django import forms
from django.utils.safestring import mark_safe
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

_band_dict = {k: v for k, v in _bands}

_scaling_choices = (
    ('z', 'by redshift'),
    ('abs_mag', 'to M_peak'),
)

_available_fields = {
    'mag_start': forms.FloatField(initial=19, help_text='m_start'),
    'mag_lim': forms.FloatField(initial=24, help_text='m_lim'),        
    't_before': forms.FloatField(initial=0.,help_text='t_before [days]'),        
    'first_band': forms.ChoiceField(choices=_bands[1:],help_text=''),#'Band'),
    'band': forms.ChoiceField(choices=_bands,help_text=''),#'Band'),
    'magsys': forms.ChoiceField(choices=_magsys, help_text=''),#'Magsys'),
    'mag_max': forms.FloatField(initial=-19.3, help_text=''),#'M_peak'),
    'mag_disp': forms.FloatField(initial=0.4, help_text='M_peak dispersion'),
    'rate': forms.FloatField(initial=3e-5, help_text='Rate [Mpc^-3 yr^-1]'),
    'scale_amplitude': forms.BooleanField(required=False, initial=True,
                                          help_text='Scale amplitude/x0'),
    'scaling_mode': forms.ChoiceField(required=False,
                                      choices=_scaling_choices,
                                      initial='z',
                                      widget=forms.RadioSelect()),
    'area': forms.FloatField(initial=100.,  min_value=0.,
                             max_value=100., help_text='Area [% of sky]'),
    'time': forms.FloatField(initial=365.25, help_text='Time [days]'),
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
        self.scale_mode = kwargs.pop('scale_mode', 'lc')

        
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
        self.form_blocks = [['Model parameters']]
        for name, value in zip(self.transient_model.param_names,
                               self.transient_model.parameters):
            if name not in self.hide_param and name != 't0':
                self.form_blocks[-1].append(['f:%s'%name])
                min_max = min_max_vals.get(name, (None, None))
                self.fields[name] = forms.FloatField(
                    min_value=min_max[0],
                    max_value=min_max[1],
                    initial=value,
                    help_text=name
                )

        self.fields['band'] = copy.copy(_available_fields['first_band'])
        self.fields['magsys'] = copy.copy(_available_fields['magsys'])        
        if self.n_bands > 1:
            band_block = ['Bands', ['f:band', 'f:magsys']]
            for k in range(1, self.n_bands):
                self.fields['band%i'%k] = copy.copy(_available_fields['band'])
                self.fields['magsys%i'%k] = copy.copy(_available_fields['magsys'])
                band_block.append(['f:band%i'%k,'f:magsys%i'%k])
        else:
            self.form_blocks[-1].append(['Band','f:band', 'f:magsys'])

        if self.scale_mode in ['lc', 'rate']:
            self.fields['scale_amplitude'] = copy.copy(
                _available_fields['scale_amplitude']
            )
            self.form_blocks[-1].append(['f:scale_amplitude'])

        if self.scale_mode == 'lc':
            self.fields['scaling_mode'] = copy.copy(
                _available_fields['scaling_mode']
            )
            self.form_blocks[-1].append(['f:scaling_mode'])
            
        if self.scale_mode in ['lc', 'rate']:
            self.fields['mag_max'] = copy.copy(_available_fields['mag_max'])
            self.fields['band_max'] = copy.copy(_available_fields['first_band'])
            self.fields['magsys_max'] = copy.copy(_available_fields['magsys'])
            self.form_blocks[-1].append(['M_peak', 'f:mag_max'])
            self.form_blocks[-1].append(['f:band_max', 'f:magsys_max'])
            
        if self.n_bands > 1:
            self.form_blocks.append(band_block)
            
        if len(self.include_fields) > 0:
            self.form_blocks.append(['Survey parameters'])
            for name in self.include_fields:
                self.fields[name] = copy.copy(_available_fields[name])
                self.form_blocks[-1].append(['f:%s'%name])

                if name in self.field_defaults.keys():
                    self.fields[name].initial = self.field_defaults[name]

    def headers(self):
        for block in self.form_blocks:
            yield block[0]
            
    def rows(self):
        k_max = max([len(block) for block in self.form_blocks])
        for k in range(1, k_max):
            yield self.yield_blocks(k)

    def yield_blocks(self, k):
        for l in range(len(self.form_blocks)):
            if k < len(self.form_blocks[l]):
                block = self.prep_block(self.form_blocks[l][k])
                yield block
            else:
                yield []
            
    def prep_block(self, block):
        out = []
        for name in block:
            if name.startswith('f:'):
                name = name[2:]
                if 'errors' in self.fields[name].__dict__.keys():
                    out.append(self.fields[name].errors)
                out.extend([self.fields[name].help_text,
                            self[name]])
            else:
                out.append(name)

        return out

    def yield_block(self, block):
        for field in block:
            yield field