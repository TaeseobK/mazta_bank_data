from django.db import models
import json

class Vendor(models.Model) :
    entity = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    npwp = models.CharField(max_length=128, null=True, blank=True)
    pic = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    bank_info = models.TextField(null=True, blank=True)
    classification = models.IntegerField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta :
        app_label = 'supplier'
        db_table = 'vendor'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'supplier'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'supplier'
        super().delete(*args, **kwargs)

class Principle(models.Model) :
    details = models.TextField(null=True, blank=True)
    details_product = models.TextField(null=True, blank=True)
    selection_date = models.DateField(null=True, blank=True)
    bank_info = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pic = models.IntegerField()
    details_product = models.TextField(null=True, blank=True)
    terms_of_payment = models.TextField(null=True, blank=True)
    lead_time = models.TextField(null=True, blank=True)
    contract_aggreement = models.TextField(null=True, blank=True)
    yearly_target = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        app_label = 'supplier'
        db_table = 'principle'
        managed = True
        
    def __str__(self):
        return json.loads(self.details).get('name')
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'supplier'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'supplier'
        super().delete(*args, **kwargs)