from django import forms
#from ratecalc.models import TransientModels

_magsys = (
    ('ab', 'AB'),
    ('vega', 'Vega'),
    )

_bands = (
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

class TransientForm(forms.Form):
    """
    Basic form for setting the transient model parameter
    """
    def __init__(self,*args,**kwargs):
        self.transient_model = kwargs.pop('transient_model')
        super(TransientForm,self).__init__(*args,**kwargs)

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

class LightcurveForm(TransientForm):
    def __init__(self,*args,**kwargs):
        super(LightcurveForm,self).__init__(*args,**kwargs)

        self.fields['bandpass'] = forms.ChoiceField(choices=_bands,
                                                    help_text='Band')
                                                    #, initial='bessellb')
        self.fields['magsys'] = forms.ChoiceField(choices=_magsys,
                                                  help_text='Magsys')


class ExpectedForm(TransientForm):
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

        self.fields['bandpass'] = forms.ChoiceField(choices=_bands,
                                                    help_text='Band')
                                                    #, initial='bessellb')
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
