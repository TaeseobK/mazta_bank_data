from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from master.models import *

@login_required(login_url='/login/')
def employee_list(request) :

    return render(request, 'hr_pages/employee_list.html', {
        'title' : 'Employee List',
        'page_name' : 'Employee List'
    })

@login_required(login_url='/login/')
def employee_new(request) :
    data = []

    ent = Entity.objects.using('master').filter(is_active=True).all()
    sup = Employee.objects.using('human_resource').filter(is_active=True).all()
    bra = Branch.objects.using('master').filter(is_active=True).all()

    data.append({
        'entities' : ent,
        'superiors' : sup,
        'branches' : bra
    })
    return render(request, 'hr_new/employee_new.html', {
        'title' : 'New Employee',
        'page_name' : 'New Employee',
        'data' : data
    })

@login_required(login_url='/login/')
def employee_detail(request, e_id) :
    return render(request, 'hr_detail/employee_detail.html', {
        'title' : 'Detail Employee',
        'page_name' : f'Detail - '
    })