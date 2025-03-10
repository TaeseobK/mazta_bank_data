from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'sales'

urlpatterns = [
    #Pages Sales
    path('transaction/doctor-list/', views.doctor_list, name='doctor_list'),
    
    #Detail
    path('transaction/doctor-list/detail/<int:doc_id>/<slug:doc_name>/', views.doctor_detail, name='doctor_detail'),
]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)