from django import template
from ratecalc.models import TransientModel

register = template.Library()

@register.inclusion_tag('ratecalc/transient_models.html')
def get_tm_list(ttype=None):
    if ttype is None:
        return {'transient_models': TransientModel.objects.all()}
    else:
        return {'transient_models':
                TransientModel.objects.filter(transient_type=ttype)}