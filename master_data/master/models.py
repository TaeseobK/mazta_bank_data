from django.db import models
class ClinicGrade(models.Model) :
    name = models.CharField(max_length=64)
    alias = models.CharField(max_length=64)
    range_clinic = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'clinic_grade'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class UserGrade(models.Model) :
    name = models.CharField(max_length=64)
    alias = models.CharField(max_length=64, null=True, blank=True)
    range_user = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'user_grade'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Profile(models.Model) :
    user_id = models.IntegerField()
    about = models.TextField(null=True, blank=True)
    addresses = models.TextField(null=True, blank=True)
    photos = models.ImageField(null=True, blank=True)

    class Meta :
        app_label = 'master'
        db_table = 'profile'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Title(models.Model) :
    name = models.TextField()
    short_name = models.CharField(max_length=64, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
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

class UserConfig(models.Model) :
    user = models.IntegerField()
    groups = models.IntegerField()
    config = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'user_config'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Announcement(models.Model) :
    groups = models.TextField(null=True, blank=True)
    see = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'announcement'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Salutation(models.Model) :
    salutation = models.CharField(max_length=64)
    short_salutation = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'salutation'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Specialist(models.Model) :
    full = models.CharField(max_length=86)
    short_name = models.CharField(max_length=12)
    description = models.TextField(null=True, blank=True)
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

class Pic(models.Model) :
    name = models.CharField(max_length=128)
    position = models.CharField(max_length=64)
    company = models.CharField(max_length=128)
    contact = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    added = models.IntegerField()
    updated = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        app_label = 'master'
        db_table = 'pic'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Classification(models.Model) :
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    created_by = models.IntegerField()
    updated_by = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        app_label = 'master'
        db_table = 'classification'
        managed = True
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)