from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'sales'

urlpatterns = [
    path('', views.index_sales, name='index'),

    #Pages Sales
    path('transaction/doctor-list/', views.doctor_list, name='doctor_list'),
    
    #Detail
    path('transaction/doctor-list/detail/<int:user_id>/<int:doc_id>/', views.doctor_detail, name='doctor_detail'),
]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)