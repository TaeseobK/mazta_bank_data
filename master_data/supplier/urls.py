from django.urls import path
from .views import *

app_name = 'supplier'

urlpatterns = [
    path('transaction/vendor-list/', vendor_list, name="vendor_list"),

    path('transaction/vendor-new/', new_vendor, name="vendor_new"),

    path('transaction/vendor-detail/<int:vendor_id>/', detail_vendor, name="vendor_detail"),
]