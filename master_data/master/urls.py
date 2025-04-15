from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'master'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('api/grade-user/<int:gu_id>/', views.gu_data, name='api_gu'),
    path('api/grade-clinic/<int:gc_id>/', views.gc_data, name='api_gc'),
    path('api/salutation/<int:sal_id>/', views.sal_data, name='api_salutation'),
    path('api/title/<int:tit_id>/', views.title_data, name='api_title'),

    #List Page
    path('grade-clinic-list/', views.gc_list, name='gc_list'),
    path('grade-user-list/', views.gu_list, name='gu_list'),
    path('title-list/', views.title_list, name='title_list'),
    path('salutation-list/', views.salutation_list, name='salutation_list'),
    path('specialists/', views.specialists, name='specialist_list'),

    #New Page
    path('grade-clinic-list/new/', views.new_gc, name='new_gc'),
    path('grade-user-list/new/', views.new_gu, name='new_gu'),
    path('title-list/new/', views.new_title, name='new_title'),
    path('salutation-list/new/', views.new_salutation, name='new_salutation'),
    path('specialists/new/', views.new_specialist, name='new_specialist'),
    
    #Detail Page
    path('grade-clinic-list/detail/<int:gc_id>/', views.detail_gc, name='detail_gc'),
    path('grade-user-list/detail/<int:gu_id>/', views.detail_gu, name='detail_gu'),
    path('title-list/detail/<int:title_id>/', views.detail_title, name='detail_title'),
    path('salutation-list/detail/<int:sal_id>/', views.detail_salutation, name='detail_salutation'),
    path('specialists/detail/<int:sp_id>/', views.detail_specialist, name='detail_specialist'),
]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)