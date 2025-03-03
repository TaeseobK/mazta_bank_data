from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import *
from master.models import *
from human_resource.models import *

@login_required(login_url='/login/')
def doctor_list(request) :
    return render(request, 'sales_pages/doctor_list.html', {
        'title' : 'Doctor List',
        'page_name' : 'Doctor Lst'
    })

@login_required(login_url='/login/')
def doctor_new(request) :
    return render(request, 'sales_new/doctor_new.html', {
        'title' : 'New Doctor',
        'page_name' : 'New Doctor'
    })

@login_required(login_url='/login/')
def doctor_detail(request, d_id) :
    return render(request, 'sales_detail/doctor_detail.html', {
        'title' : 'Detail Doctor',
        'page_name' : f'Detail Doctor'
    })