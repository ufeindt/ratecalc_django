from django.conf.urls import url
from ratecalc import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^lightcurve/(?P<tm_name>[\w\-]+)/$',
        views.show_lightcurve, name='show_lightcurve'),
    url(r'^expected/(?P<tm_name>[\w\-]+)/$',
        views.show_expected, name='show_expected'),
    url(r'^redshift/(?P<tm_name>[\w\-]+)/$',
        views.show_redshift, name='show_redshift'),
]