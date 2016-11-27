from django import template
from ratecalc.models import TransientModel

register = template.Library()

@register.inclusion_tag('ratecalc/transient_models.html')
def get_tm_list(ttype=None):
    if ttype is None:
        print 'none'
        print {'transient_models': TransientModel.objects.all()}
        return {'transient_models': TransientModel.objects.all()}
    else:
        print 'not none'
        return {'transient_models':
                TransientModel.objects.filter(transient_type=ttype)}