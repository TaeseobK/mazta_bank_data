from django.urls import path, include
from .views import *

app_name = 'apis'

urlpatterns = [
    path('doctor-detail/', DoctorDetail.as_view(), name="all_doctors"),
]