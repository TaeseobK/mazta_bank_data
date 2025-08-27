from django.db import models

class Employee(models.Model) :
    user = models.IntegerField()
    code = models.CharField(max_length=24)
    full_name = models.CharField(max_length=64)
    entity = models.IntegerField(null=True, blank=True)
    superior = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    branch = models.IntegerField(null=True, blank=True)
    public_information = models.TextField(null=True, blank=True)
    work_information = models.TextField(null=True, blank=True)
    private_information = models.TextField(null=True, blank=True)
    work_loaction = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'human_resource'
        db_table = 'employee'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().delete(*args, **kwargs)

    def get_hierarchy(self) :
        hierarchy = []
        current = self
        while current :
            hierarchy.append(current)
            current = current.parent
        return hierarchy[::-1]

class Attendance(models.Model) :
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.IntegerField()
    check_in = models.DateTimeField()
    location_check_in = models.TextField(null=True, blank=True)
    check_out = models.DateTimeField()
    location_check_out = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'attendance'
        db_table = 'human_resource'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().delete(*args, **kwargs)

class Recruitment(models.Model) :
    full_name = models.CharField(max_length=64)
    entity = models.IntegerField(null=True, blank=True)
    branch = models.IntegerField(null=True, blank=True)
    public_information = models.TextField(null=True, blank=True)
    work_information = models.TextField(null=True, blank=True)
    private_information = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'human_resource'
        db_table = 'recruitment'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().delete(*args, **kwargs)

class Disciplinary(models.Model) :
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    action_type = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'human_resource'
        db_table = 'disciplinary'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().delete(*args, **kwargs)

class Payroll(models.Model) :
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    salary = models.CharField(max_length=64)
    deductions = models.TextField(null=True, blank=True)
    net_salary = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'human_resource'
        db_table = 'payroll'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().delete(*args, **kwargs)

class TimeOff(models.Model) :
    name = models.CharField(max_length=24)
    date = models.DateField()
    time_off_type = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'human_resource'
        db_table = 'time_off'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'human_resource'
        super().delete(*args, **kwargs)