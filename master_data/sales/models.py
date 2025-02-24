from django.db import models

class SalesReport(models.Model) :
    date = models.DateField()
    entity = models.IntegerField()
    branch = models.IntegerField()
    warehouse = models.IntegerField()
    sp_number = models.TextField(null=True, blank=True)
    sj_number = models.TextField(null=True, blank=True)
    fj_number = models.TextField(null=True, blank=True)
    department = models.IntegerField()
    is_otc = models.BooleanField(null=True, blank=True)
    sales = models.IntegerField()
    customer = models.IntegerField()
    product_detail = models.TextField()
    hna = models.IntegerField(null=True, blank=True)
    detail_sales = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'sales'
        db_table = 'report_sales'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().delete(*args, **kwargs)

class Visits(models.Model) :
    sales = models.IntegerField()
    type_visits = models.IntegerField(null=True, blank=True)
    customer = models.IntegerField(null=True, blank=True)
    products = models.TextField(null=True, blank=True)
    c_in_date = models.DateTimeField(null=True, blank=True)
    c_in_image = models.ImageField(upload_to='media/user_upload_file/sales/', null=True, blank=True)
    c_in_address = models.TextField(null=True, blank=True)
    c_out_date = models.DateTimeField(null=True, blank=True)
    c_out_image = models.ImageField(upload_to='media/user_upload_file/sales/', null=True, blank=True)
    c_out_address = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_sub = models.BooleanField()
    parent = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'sales'
        db_table = 'visits'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().delete(*args, **kwargs)

class Target(models.Model) :
    sales = models.IntegerField(null=True, blank=True)
    target = models.IntegerField(null=True, blank=True)
    is_active =models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'sales'
        db_table = 'target_sales'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().delete(*args, **kwargs)

class Complaints(models.Model) :
    issue = models.TextField()
    type_complaint = models.IntegerField()
    product = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'sales'
        db_table = 'complaints'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'sales'
        super().delete(*args, **kwargs)
