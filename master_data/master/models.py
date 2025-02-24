from django.db import models

class Entity(models.Model) :
    name = models.CharField(max_length=64)
    established_date = models.DateField(null=True, blank=True)
    parent = models.IntegerField(default=0)
    website = models.URLField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    sub_entity = models.BooleanField(default=False)
    branches = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'entity'
        managed = True

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)


class Branch(models.Model) :
    name = models.CharField(max_length=64)
    address = models.TextField()
    sub_branch = models.BooleanField(default=False)
    parent = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'branch'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Warehouse(models.Model) :
    name = models.CharField(max_length=124)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'warehouse'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class ProductCategory(models.Model) :
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'product_category'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class ProductCategorySales(models.Model) :
    name = models.CharField(max_length=64, null=True, blank=True)
    short_name = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'product_category_sales'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Product(models.Model) :
    sku = models.TextField(null=True, blank=True)
    code_accurate = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=64)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    category_sales = models.ForeignKey(ProductCategorySales, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)                                              #Beberapa product tidak dijual pada entitas tertentu
    department = models.IntegerField(null=True, blank=True)                                        #Beberapa product tidak dijual pada department tertentu
    price = models.IntegerField(blank=True, null=True)
    cost = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'product'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Batch(models.Model) :
    batch = models.CharField(max_length=64)
    exp_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'batch_product'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

"""
    This is Master Data for Employee or Human Resource
    ==================================================
"""

class Department(models.Model) :
    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=5, null=True, blank=True)
    is_sub_department = models.BooleanField(default=False)
    parent = models.IntegerField(null=True, blank=True)
    entity = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'department'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class JobPosition(models.Model) :
    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=12, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'job_position'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class ShiftSchedule(models.Model) :
    shift = models.CharField(max_length=24)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'shift_schedule'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class TimeOffType(models.Model) :
    name = models.CharField(max_length=24)
    is_absent = models.BooleanField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'time_off_type'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class DisciplinaryAction(models.Model) :
    name = models.CharField(max_length=24)
    duration = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'disciplinary_action'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class DeductionType(models.Model) :
    name = models.CharField(max_length=24)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'deduction_type'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class WorkLocation(models.Model) :
    name = models.CharField(max_length=24)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'work_location'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class DoctorInformation(models.Model) :
    full_name = models.CharField(max_length=255)
    code = models.TextField(null=True, blank=True)
    is_individual = models.BooleanField(default=True)
    is_focused = models.BooleanField(default=False)
    private_information = models.TextField(null=True, blank=True)
    public_information = models.TextField(null=True, blank=True)
    work_information = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'doctor_information'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class SalesRole(models.Model) :
    name = models.CharField(max_length=64)
    parent = models.IntegerField()
    sub_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'sales_role'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Specialist(models.Model) :
    short_name = models.CharField(max_length=12, null=True, blank=True)
    name = models.CharField(max_length=86, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'specialist'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Title(models.Model) :
    name = models.CharField(max_length=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'title'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class TypeVisits(models.Model) :
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'type_visits'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class TypeComplaint(models.Model) :
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'type_complaint'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)