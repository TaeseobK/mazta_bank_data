from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'master'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('api/grade-user/<int:gu_id>/', views.gu_data, name='api_gu'),
    path('api/grade-clinic/<int:gc_id>/', views.gc_data, name='api_gc'),
    path('api/salutation/<int:sal_id>/', views.sal_data, name='api_salutation'),
    path('api/title/<int:tit_id>/', views.title_data, name='api_title'),
    path('api/dr-detail/', views.datadoctor, name='dr_detail'),

    #List Page
    path('grade-clinics/', views.gc_list, name='gc_list'),
    path('grade-users/', views.gu_list, name='gu_list'),
    path('titles/', views.title_list, name='title_list'),
    path('salutations/', views.salutation_list, name='salutation_list'),
    path('specialists/', views.specialists, name='specialist_list'),
    path('pics/', views.pic_list, name='pic_list'),
    path('classifications/', views.classfication_list, name='classification_list'),

    #New Page
    path('grade-clinics/new/', views.new_gc, name='new_gc'),
    path('grade-users/new/', views.new_gu, name='new_gu'),
    path('titles/new/', views.new_title, name='new_title'),
    path('salutations/new/', views.new_salutation, name='new_salutation'),
    path('specialists/new/', views.new_specialist, name='new_specialist'),
    path('pics/new/', views.new_pic, name='new_pic'),
    path('classifications/new/', views.new_classification, name='new_classification'),
    
    #Detail Page
    path('grade-clinics/detail/<int:gc_id>/', views.detail_gc, name='detail_gc'),
    path('grade-users/detail/<int:gu_id>/', views.detail_gu, name='detail_gu'),
    path('titles/detail/<int:title_id>/', views.detail_title, name='detail_title'),
    path('salutations/detail/<int:sal_id>/', views.detail_salutation, name='detail_salutation'),
    path('specialists/detail/<int:sp_id>/', views.detail_specialist, name='detail_specialist'),
    path('pics/detail/<int:pic_id>/', views.detail_pic, name='detail_pic'),
    path('classifications/<int:class_id>/', views.detail_classification, name='detail_classification'),
]

if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)