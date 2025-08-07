from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'sales'

urlpatterns = [
    path('', views.index_sales, name='index'),

    #Pages Sales
    path('transaction/doctor-list/', views.doctor_list, name='doctor_list'),
    # path('transaction/dctr-list/', views.dctr_adm, name="doctor_admin"),
    
    #Detail
    path('transaction/doctor-list/detail/<int:user_id>/<int:doc_id>/', views.doctor_detail, name='doctor_detail_sales'),
    path('transaction/doctor-list/detail/<int:dr_id>/', views.adm_doctor_detail, name='doctor_detail_admin'),
    path('transaction/doctor-list/switch/', views.switch_rayon, name='switch_rayon'),

    path('download/fhajkghj/fdsahjk/gdsajjghtei/3242afa/', views.download_doctor_data, name="download_doctor_data"),
]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)