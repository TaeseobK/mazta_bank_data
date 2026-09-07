from django.contrib import admin
from master_data.admin_utils import auto_admin
from .models import *

admin.site.register(Vendor, auto_admin(Vendor, list_filter=('name', 'entity')))
admin.site.register(Principle, auto_admin(Principle, list_filter=('details',)))
