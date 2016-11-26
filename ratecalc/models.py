from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256)
    model_type = models.CharField(max_length=128)
    
    class Meta:
        verbose_name_plural = 'categories'

    def __unicode__(self): 
        return self.name

    def __str__(self): 
        return self.name
    
class TransientType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    m_B_max = models.FloatField(default=0)
    sig_m_B_max = models.FloatField(default=0)
    rate = models.FloatField(default=3e-5)

    def __unicode__(self): 
        return self.name

    def __str__(self): 
        return self.name
    
class TransientModel(models.Model):
    transient_type = models.ForeignKey(TransientType)
    category = models.ForeignKey(Category)
    
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=256)
    sncosmo_name = models.CharField(max_length=128)
    sncosmo_version = models.CharField(max_length=16)
    model_file = models.CharField(max_length=256)
    host_extinction = models.BooleanField(default=True)
    default_amplitude = models.FloatField(default=1)
    
    def __unicode__(self): 
        return self.name

    def __str__(self): 
        return self.name