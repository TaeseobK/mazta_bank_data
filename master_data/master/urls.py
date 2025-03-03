from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'master'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),

    #List Page
    path('entity-list/', views.entity_list, name='entity_list'),
    path('branch-list/', views.branch_list, name='branch_list'),
    path('warehouse-list/', views.warehouse_list, name='warehouse_list'),
    path('product-c-list/', views.product_category_list, name='product_c_list'),
    path('product-c-n-list/', views.pcn_list, name='pcn_list'),
    path('product-list/', views.product_list, name='product_list'),
    path('department-list/', views.department_list, name='department_list'),
    path('batch-list/', views.batch_list, name='batch_list'),
    path('job-position-list/', views.job_position_list, name='jb_list'),
    path('shift-list/', views.shift, name='shift_list'),
    path('time-off-list/', views.timeoff_list, name='timeoff_list'),
    path('disciplinary-action-list/', views.disciplinary, name='disc_list'),
    path('deduction-type-list/', views.deduction_list, name='deduc_list'),
    path('work_location-list/', views.work_locations, name='work_location_list'),
    path('grade-clinic-list/', views.gc_list, name='gc_list'),
    path('grade-user-list/', views.gu_list, name='gu_list'),
    path('title-list/', views.title_list, name='title_list'),
    path('salutation-list/', views.salutation_list, name='salutation_list'),
    path('specialists/', views.specialists, name='specialists'),

    #New Page
    path('entity-list/new/', views.new_entity, name='new_entity'),
    path('branch-list/new/', views.new_branch, name='new_branch'),
    path('warehouse-list/new/', views.new_warehouse, name='new_warehouse'),
    path('product-c-list/new/', views.new_product_category, name='new_pc'),
    path('product-c-n-list/new/', views.new_pcn, name='new_pcn'),
    path('product-list/new/', views.new_product, name='new_product'),
    path('department-list/new/', views.new_department, name='new_department'),
    path('batch-list/new/', views.new_batch, name='new_batch'),
    path('job-position-list/new/', views.new_job_position, name='new_jb'),
    path('shift-list/new/', views.new_shift, name='new_shift'),
    path('time-off-list/new/', views.new_timeoff, name='new_timeoff'),
    path('disciplinary-action-list/new/', views.new_disciplinary, name='new_disc'),
    path('deduction-type-list/new/', views.new_deduction, name='new_ded'),
    path('work-location-list/new/', views.new_work_location, name='new_work_location'),
    path('grade-clinic-list/new/', views.new_gc, name='new_gc'),
    path('grade-user-list/new/', views.new_gu, name='new_gu'),
    path('title-list/new/', views.new_title, name='new_title'),
    path('salutation-list/new/', views.new_salutation, name='new_salutation'),
    path('specialists/new/', views.new_specialist, name='new_specialist'),
    
    #Detail Page
    path('branch-list/detail/<int:b_id>/', views.branch_detail, name='detail_branch'),
    path('entity-list/detail/<int:e_id>/', views.detail_entity, name='detail_entity'),
    path('warehouse-list/detail/<int:w_id>/', views.detail_warehouse, name='detail_warehouse'),
    path('product-c-list/detail/<int:pc_id>/', views.detail_pc, name='detail_pc'),
    path('product-c-n-list/detail/<int:pcn_id>/', views.detail_pcn, name='detail_pcn'),
    path('department-list/detail/<int:d_id>/', views.detail_department, name='detail_department'),
    path('product-list/detail/<int:p_id>/', views.detail_product, name='detail_product'),
    path('batch-list/detail/<int:bat_id>/', views.detail_batch, name='detail_batch'),
    path('job-position-list/detail/<int:jb_id>/', views.detail_job_position, name='detail_jb'),
    path('shift-list/detail/<int:sh_id>/', views.detail_shift, name='detail_shift'),
    path('time-off-list/detail/<int:to_id>/', views.detail_timeoff, name='detail_timeoff'),
    path('disciplinary-action-list/detail/<int:disc_id>/', views.detail_disc, name='detail_disc'),
    path('deduction-type-list/detail/<int:ded_id>/', views.detail_deduction, name='detail_deduc'),
    path('work-location-list/detail/<int:dwk_id>/', views.detail_work_location, name='detail_work_location'),
    path('grade-clinic-list/detail/<int:gc_id>/', views.detail_gc, name='detail_gc'),
    path('grade-user-list/detail/<int:gu_id>/', views.detail_gu, name='detail_gu'),
    path('title-list/detail/<int:title_id>/', views.detail_title, name='detail_title'),
    path('salutation-list/detail/<int:sal_id>/', views.detail_salutation, name='detail_salutation'),
    path('specialists/detail/<int:sp_id>/', views.detail_specialist, name='detail_specialist'),
]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)