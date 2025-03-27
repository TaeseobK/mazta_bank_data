from django.contrib import admin
from .models import *

class ClinicAdmin(admin.ModelAdmin) :
    list_display = [field.name for field in ClinicGrade._meta.get_fields() if field.name not in ['id', 'created_at']]
    list_filter = ('alias', 'name')
    list_display_links = [field.name for field in ClinicGrade._meta.get_fields() if field.name not in ['id', 'created_at']]
    search_fields = [field.name for field in ClinicGrade._meta.get_fields() if field.get_internal_type() == 'CharField']

class UserAdmin(admin.ModelAdmin) :
    list_display = [field.name for field in UserGrade._meta.get_fields() if field.name not in ['id', 'created_at']]
    list_filter = ('alias', 'name')
    list_display_links = [field.name for field in UserGrade._meta.get_fields() if field.name not in ['id', 'created_at']]
    search_fields = [field.name for field in UserGrade._meta.get_fields() if field.get_internal_type() == 'CharField']

class TitleAdmin(admin.ModelAdmin) :
    list_display = [field.name for field in Title._meta.get_fields() if field.name not in ['id', 'created_at']]
    list_filter = ('name',)
    list_display_links = [field.name for field in Title._meta.get_fields() if field.name not in ['id', 'created_at']]
    search_fields = [field.name for field in Title._meta.get_fields() if field.get_internal_type() == 'CharField']

class SalutationAdmin(admin.ModelAdmin) :
    list_display = [field.name for field in Salutation._meta.get_fields() if field.name not in ['id', 'created_at']]
    list_filter = ('salutation',)
    list_display_links = [field.name for field in Salutation._meta.get_fields() if field.name not in ['id', 'created_at']]
    search_fields = [field.name for field in Salutation._meta.get_fields() if field.get_internal_type() == 'CharField']

class SpecialistAdmin(admin.ModelAdmin) :
    list_display = [field.name for field in Specialist._meta.get_fields() if field.name not in ['id', 'created_at']]
    list_filter = ('short_name',)
    list_display_links = [field.name for field in Specialist._meta.get_fields() if field.name not in ['id', 'created_at']]
    search_fields = [field.name for field in Specialist._meta.get_fields() if field.get_internal_type() == 'CharField']


admin.site.register(Specialist, SpecialistAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(ClinicGrade, ClinicAdmin)
admin.site.register(UserGrade, UserAdmin)
admin.site.register(Salutation, SalutationAdmin)