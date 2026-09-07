from django.contrib import admin
from master_data.admin_utils import auto_admin
from .models import *

admin.site.register(Specialist, auto_admin(Specialist, list_filter=('short_name',)))
admin.site.register(Title, auto_admin(Title, list_filter=('name',)))
admin.site.register(ClinicGrade, auto_admin(ClinicGrade, list_filter=('alias', 'name')))
admin.site.register(UserGrade, auto_admin(UserGrade, list_filter=('alias', 'name')))
admin.site.register(Salutation, auto_admin(Salutation, list_filter=('salutation',)))
admin.site.register(Pic, auto_admin(Pic, list_filter=('name',)))
admin.site.register(Classification, auto_admin(Classification, list_filter=('name',)))
