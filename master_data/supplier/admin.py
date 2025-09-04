from django.contrib import admin
from .models import *

# Register your models here.
class VendorAdmin(admin.ModelAdmin) :
    list_display = [field.name for field in Vendor._meta.get_fields() if field.name not in ['id', 'created_at']]
    list_filter = ('name', 'entity',)
    list_display_links = [field.name for field in Vendor._meta.get_fields() if field.name not in ['id', 'created_at']]
    search_fields = [field.name for field in Vendor._meta.get_fields() if field.get_internal_type() == 'CharField']

class PrincipleAdmin(admin.ModelAdmin) :
    list_display = [field.name for field in Principle._meta.get_fields() if field.name not in ['id', 'created_at']]
    list_filter = ('details',)
    list_display_links = [field.name for field in Principle._meta.get_fields() if field.name not in ['id', 'created_at']]
    search_fields = [field.name for field in Principle._meta.get_fields() if field.get_internal_type() == 'CharField']

admin.site.register(Vendor, VendorAdmin)
admin.site.register(Principle, PrincipleAdmin)