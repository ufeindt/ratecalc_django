from __future__ import unicode_literals

from django.db import models

# Create your models here.

class TransientModels(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=256)
    sncosmo_name = models.CharField(max_length=128)
    sncosmo_version = models.CharField(max_length=16)
    transient_type = models.CharField(max_length=128)
    m_B_max = models.FloatField(default=0)
    sig_m_B_max = models.FloatField(default=0)
    rate = models.FloatField(default=3e-5)
    model_type = models.CharField(max_length=128)
    model_file = models.CharField(max_length=256)
    
    def __unicode__(self): 
        return self.name

    def __str__(self): 
        return self.name