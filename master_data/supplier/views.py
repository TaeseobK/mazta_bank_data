from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import *

def vendor_list(request) :
    return render(request, 'supplier_pages/vendor_list.html', {
        'title' : "Vendor List",
        'page_name' : "Vendor List",
        'api' : "False",
        'new_url' : reverse_lazy('supplier:vendor_new')
    })

def new_vendor(request) :
    if request.method == 'POST' :
        metode = request.POST.get('metode', '')

    
    return render(request, 'supplier_new/new_vendor.html', {
        'title' : "New Vendor",
        'page_name' : "New Vendor",
        'api' : "False"
    })