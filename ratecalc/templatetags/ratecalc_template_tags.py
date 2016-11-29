from django import template
from ratecalc.models import TransientModel, Category

register = template.Library()

@register.inclusion_tag('ratecalc/transient_models.html')
def get_tm_list(ttype, cat):
    tm_list = TransientModel.objects.filter(transient_type=ttype, category=cat)
    if len(tm_list) > 0:
        return {'transient_models': tm_list, 'category': cat}
    else:
        return {'transient_models': None, 'category': cat}
