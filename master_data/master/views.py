from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.http import JsonResponse, Http404
from .models import *
from django.urls import reverse
from master_data.local_settings import *
import requests
from django.forms.models import model_to_dict
from functools import wraps
from datetime import datetime
import json

def group_required(group_name) :
    def decorator(view_func) :
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs) :
            user = request.user
            if (user.is_authenticated and user.groups.filter(name=group_name).exists()) or user.is_superuser :
                return view_func(request, *args, **kwargs)
            
            else :
                raise Http404("You don't have permission to access this page.")
            
            return _wrapped_view
        return decorator

def admin_required(view_func) :
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs) :
        detail = request.session.get('detail')

        if not detail or not request.user.is_staff :
            raise Http404("Not Found!")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

@login_required
def home(request) :

    return render(request, 'core/home.html', {
        'title' : 'Dashboard',
        'page_name' : 'Home'
    })

def gu_data(request, gu_id) :

    if not request.user.is_authenticated :
        return redirect('master:login')
    
    grade_user = UserGrade.objects.using('master').get(id=gu_id)

    return JsonResponse(model_to_dict(grade_user), safe=False)

def gc_data(request, gc_id) :
    if not request.user.is_authenticated :
        return redirect('master:login')
    
    grade_clinic = ClinicGrade.objects.using('master').get(id=gc_id)

    return JsonResponse(model_to_dict(grade_clinic), safe=False)

def sal_data(request, sal_id) :
    
    if not request.user.is_authenticated :
        return redirect('master:login')
    
    salutation = Salutation.objects.using('master').get(id=sal_id)

    return JsonResponse(model_to_dict(salutation), safe=False)

def title_data(request, tit_id) :
    
    if not request.user.is_authenticated :
        return redirect('master:login')
    
    title = Title.objects.using('master').get(id=tit_id)

    return JsonResponse(model_to_dict(title), safe=False)

def login_view(request) :
    if request.method == 'POST' :
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        username = request.POST.get('username', '')
        next_url = request.POST.get('next') or request.GET.get('next') or '/'

        response = requests.post(login_url(), data={
            'email' : email,
            'password' : password
        })

        if response.status_code == 200 :
            token = response.json().get('token')
            detail = response.json().get('data')
            request.session['token'] = token
            request.session['detail'] = detail
            
            print(detail.get('email'))

            try :
                user = User.objects.get(email=email)
                
                if user.check_password(password) :
                    group, _ = Group.objects.get_or_create(name="sales")

                    if not user.groups.filter(name="sales").exists() :
                        user.groups.add(group)

                    login(request, user)

                    print(f"User dengan username {user.username} berhasil.")
                    return redirect(next_url)
                
                else :
                    print(f"Error creating user with email {email}.")
                    return redirect('master:login')
                
            except User.DoesNotExist :
                if "admin" in str(detail.get('name')).lower() :
                    staff = True

                else :
                    staff = False

                user_ = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    is_staff=staff
                )

                group_, _1 = Group.objects.get_or_create(name="sales")

                if not user_.groups.filter(name="sales").exists() :
                    user_.groups.add(group_)

                user_.save()

                login(request, user_)
                return redirect(next_url)
            
        else :
            try :
                user = User.objects.get(username=username, email=email)

                if user.check_password(password) :
                    login(request, user)
                    return redirect(next_url)
                
                else :
                    return redirect('master:login')
                
            except User.DoesNotExist :
                raise Http404("Please check your email or password")
            
    return render(request, 'core/login.html', {
        'title' : 'Login',
        'login' : True
    })

@login_required
def logout_view(request) :
    token = request.session.get('token')
    user = request.user

    if token :
        headers = {
            'Authorization' : token
        }
        response = requests.post(logout_url(), headers=headers)

        print(response)

        if response.status_code == 200 :
            request.session.pop('token', None)
            request.session.pop('detail', None)

            request.session.flush()
            logout(request)

            return redirect('master:login')
        else :
            return JsonResponse({'error' : 'Logout Gagal, Coba lagi nanti...'})
    
    else :
        logout(request)
        return redirect('master:login')

@login_required
@admin_required
def gc_list(request) :
    search_query = request.GET.get('search', '')

    data = []

    grades = ClinicGrade.objects.using('master').filter(is_active=True).all().order_by('id')
    
    for d in grades :
        d.range_clinic = json.loads(d.range_clinic)

        data.append({
            'grade' : d
        })

    if search_query :
        data = [
            g for g in data
            if (
                search_query.lower() in str(g['grade'].description.description).lower() or
                search_query.lower() in str(g['grade'].description.alias).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/gc_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/gc_list.html', {
        'title' : 'Grade Clinic',
        'page_name' : 'Grade Clinic',
        'page_obj' : page_obj,
        'api' : "False",
        'new_url' : reverse('master:new_gc')
    })

@login_required
@admin_required
def new_gc(request) :
    
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST.get('name', '')
            alias = request.POST.get('alias', '')
            max_value = request.POST.get('max-value', '')
            min_value = request.POST.get('min-value', '')
            desc = request.POST.get('description', '')

            range_clinic = {
                'max_value' : int(max_value),
                'min_value' : int(min_value),
            }

            ClinicGrade.objects.using('master').create(
                name=str(name).title(),
                alias=str(alias).title(),
                range_clinic=json.dumps(range_clinic),
                description=desc
            ).save()

            return redirect('master:gc_list')

    return render(request, 'master_new/new_gc.html', {
        'title' : 'New Grade Clinic',
        'page_name' : 'New Grade Clinic'
    })

@login_required
@admin_required
def detail_gc(request, gc_id) :

    grade = ClinicGrade.objects.using('master').get(id=int(gc_id))
    grade.range_clinic = json.loads(grade.range_clinic)

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST.get('name', '')
            alias = request.POST.get('alias', '')
            max_value = request.POST.get('max-value', '')
            min_value = request.POST.get('min-value', '')
            desc = request.POST.get('description', '')

            range_clinic = {
                'max_value' : int(max_value),
                'min_value' : int(min_value),
            }

            grade.name = str(name).title()
            grade.alias = str(alias).title()
            grade.range_clinic = json.dumps(range_clinic)
            grade.description = desc

            grade.save()

            return redirect('master:gc_list')
        
        elif metode == 'delete' :
            grade.range_clinic = json.dumps(grade.range_clinic)
            grade.is_active = False
            
            grade.save()

            return redirect('master:gc_list')

    return render(request, 'master_detail/gc_detail.html', {
        'title' : 'Grade Clinic Detail',
        'page_name' : f"Detail Clinic Grade - {grade.alias}",
        'data' : grade
    })

def convert(value) :
    if value == "Million" :
        measure = "Juta"
    elif value == "BIllion" :
        measure = "Milyar"
    elif  value == "Thousand" :
        measure = "Ribu"
    
    return measure

@login_required
@admin_required
def gu_list(request) :
    search_query = request.GET.get('search', '')

    data = []

    gus = UserGrade.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in gus :
        d.range_user = json.loads(d.range_user)

        data.append(d)
    print(data)

    if search_query :
        data = [
            r for r in data
            if (
                search_query.lower() in str(r['measure'].get('max')).lower() or
                search_query.lower() in str(r['measure'].get('min')).lower() or
                search_query.lower() in str(r['user'].description.get('alias')).lower() or
                search_query.lower() in str(r['user'].description.get('description')).lower() or
                search_query.lower() in str(r['user'].name).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/gu_list.html', {
            'page_obj' : page_obj
        })
        

    return render(request, 'master_pages/gu_list.html', {
        'title' : 'Grade User List',
        'page_name' : 'Grade User List',
        'page_obj' : page_obj,
        'api' : "False",
        'new_url' : reverse('master:new_gu')
    })

@login_required
@admin_required
def new_gu(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST.get('name', '')
            alias = request.POST.get('alias', '')
            max_value = request.POST.get('max-value', '')
            max_measure = request.POST.get('max-measure', '')
            min_value = request.POST.get('min-value', '')
            min_measure = request.POST.get('min-measure', '')
            desc = request.POST.get('description', '')

            range_user = {
                'max' : {
                    'measure' : str(max_measure),
                    'value' : int(max_value)
                },
                'min' : {
                    'measure' : str(min_measure),
                    'value' : int(min_value)
                }
            }

            UserGrade.objects.using('master').create(
                name=str(name).title(),
                alias=str(alias).title(),
                range_user=json.dumps(range_user),
                description=desc
            ).save()

            return redirect('master:gu_list')

    return render(request, 'master_new/new_gu.html', {
        'title' : 'New Grade User',
        'page_name' : 'New Grade User'
    })

@login_required
@admin_required
def detail_gu(request, gu_id) :
    gu = UserGrade.objects.using('master').get(id=int(gu_id))
    gu.range_user = json.loads(gu.range_user)

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST.get('name', '')
            alias = request.POST.get('alias', '')
            max_value = request.POST.get('max-value', '')
            max_measure = request.POST.get('max-measure', '')
            min_value = request.POST.get('min-value', '')
            min_measure = request.POST.get('min-measure', '')
            desc = request.POST.get('description', '')

            range_user = {
                'max' : {
                    'measure' : str(max_measure),
                    'value' : int(max_value)
                },
                'min' : {
                    'measure' : str(min_measure),
                    'value' : int(min_value)
                }
            }

            gu.name=name
            gu.alias=alias
            gu.range_user=json.dumps(range_user)
            gu.description=desc

            gu.save()

            return redirect('master:gu_list')
        
        elif metode == 'delete' :
            gu.range_user = json.dumps(gu.range_user)
            gu.is_active = False

            gu.save()

            return redirect('master:gu_list')

    return render(request, 'master_detail/gu_detail.html', {
        'title' : 'Detail Grade User',
        'page_name' : f"Detail User Grade - {gu.name}",
        'data' : gu
    })

@login_required
@admin_required
def title_list(request) :
    search_query = request.GET.get('search', '')

    titles = Title.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        titles = [
            data for data in titles
            if (
                search_query.lower() in str(data.name).lower() or
                search_query.lower() in str(data.short_name).lower()
            )
        ]

    paginator = Paginator(titles, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/title_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/title_list.html', {
        'title' : 'Title List',
        'page_name' : 'Title List',
        'page_obj' : page_obj,
        'api' : "False",
        'new_url' : reverse('master:new_title')
    })

@login_required
@admin_required
def new_title(request) :

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            short_name = request.POST.get('short-name')
            full_name = request.POST.get('full-name')
            description = request.POST.get('description', '')

            if Title.objects.using('master').filter(name=full_name).exists() or Title.objects.using('master').filter(short_name=short_name).exists() :
                return redirect('master:new_title')
            
            else :

                Title.objects.using('master').create(
                    name=str(full_name).title(),
                    short_name=str(short_name).title(),
                    description=description
                ).save()

                return redirect('master:title_list')
        
    return render(request, 'master_new/new_title.html', {
        'title' : 'New Title',
        'page_name' : 'New Title'
    })

@login_required
@admin_required
def detail_title(request, title_id) :
    title = Title.objects.using('master').get(id=int(title_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            short_name = request.POST.get('short-name')
            full_name = request.POST.get('full-name')
            description = request.POST.get('description', '')

            if Title.objects.using('master').filter(name=full_name).exists() or Title.objects.using('master').filter(short_name=short_name).exists() :
                return redirect('master:new_title')
            
            else :
                title.name = full_name
                title.short_name = short_name
                title.description = description

                title.save()

                return redirect('master:title_list')
        
        elif metode == 'delete' :
            title.is_active = False

            title.save()

            return redirect('master:title_list')

    return render(request, 'master_detail/title_detail.html', {
        'title' : 'Detail Title',
        'page_name' : f"Detail - {title.short_name}",
        'data' : title
    })

@login_required
@admin_required
def salutation_list(request) :
    search_query = request.GET.get('search', '')

    data = []

    salutations = Salutation.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in salutations :

        data.append({
            'salutation' : d
        })

    if search_query :
        data = [
            s for s in data
            if (
                search_query.lower() in str(s['salutation'].description.get('short_name')).lower() or
                search_query.lower() in str(s['salutation'].salutation).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/salutation_list.html', {
            'page_obj' : page_obj
        })
    
    return render(request, 'master_pages/salutation_list.html', {
        'title' : 'Salutations',
        'page_name' : 'Salutations',
        'api' : "False",
        'page_obj' : page_obj,
        'new_url' : reverse('master:new_salutation')
    })

@login_required
@admin_required
def new_salutation(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            full_name = request.POST.get('full-name', '')
            short_name = request.POST.get('short-name', '')
            description = request.POST.get('description', '')

            if Salutation.objects.using('master').filter(short_salutation=short_name).exists() :
                return redirect('master:new_salutation')
            
            else :
                Salutation.objects.using('master').create(
                    salutation=str(full_name).title(),
                    description=description,
                    short_salutation=str(short_name).upper()
                ).save()

                return redirect('master:salutation_list')
            
    return render(request, 'master_new/new_salutation.html', {
        'title' : 'New Salutation',
        'page_name' : 'New Salutation'
    })

@login_required
@admin_required
def detail_salutation(request, sal_id) :

    salutation = Salutation.objects.using('master').get(id=int(sal_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            full_name = request.POST.get('full-name')
            short_name = request.POST.get('short-name')
            description = request.POST.get('description', '')

            if Salutation.objects.using('master').filter(salutation=short_name).exists() :
                return redirect('master:new_salutation')
            
            else :
                salutation.salutation = full_name
                salutation.short_salutation = short_name
                salutation.description = description

                salutation.save()

                return redirect('master:salutation_list')
            
        elif metode == 'delete' :
            salutation.is_active = False

            salutation.save()

            return redirect('master:salutation_list')

    return render(request, 'master_detail/salutation_detail.html', {
        'title' : 'Detail Salutation',
        'page_name' : f"Detail - {salutation.short_salutation}",
        'data' : salutation
    })

@login_required
@admin_required
def specialists(request) :
    search_query = request.GET.get('search', '')

    specialists = Specialist.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        specialists = [
            data for data in specialists
            if (
                search_query.lower() in str(data.full).lower() or
                search_query.lower() in str(data.short_name).lower()
            )
        ]

    paginator = Paginator(specialists, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/specialists.html', {
            'page_obj' : page_obj
        })
    
    return render(request, 'master_pages/specialists.html', {
        'title' : 'Specialists',
        'page_name' : 'Specialists',
        'api' : "False",
        'page_obj' : page_obj,
        'new_url' : reverse('master:new_specialist')
    })

@login_required
@admin_required
def new_specialist(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            full_name = request.POST.get('full-name')
            short_name = request.POST.get('short-name')
            description = request.POST.get('description')

            if Specialist.objects.using('master').filter(short_name=short_name).exists() or Specialist.objects.using('master').filter(full=full_name).exists() :
                return redirect('master:new_specialist')
            
            else :
                Specialist.objects.using('master').create(
                    full=str(full_name).title(),
                    short_name=str(short_name).title(),
                    description=description
                ).save()

                return redirect('master:specialist_list')
            
    return render(request, 'master_new/new_specialist.html', {
        'title' : 'New Specialist',
        'page_name' : 'New Specialist'
    })

@login_required
@admin_required
def detail_specialist(request, sp_id) :

    specialist = Specialist.objects.using('master').get(id=int(sp_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            full_name = request.POST['full']
            short_name = request.POST['short']
            desc = request.POST['desc']

            if Specialist.objects.using('master').filter(short_name=short_name).exclude(id=int(sp_id)).exists() or Specialist.objects.using('master').filter(full=full_name).exclude(id=int(sp_id)).exists() :
                return redirect('master:detail_specialist', sp_id=specialist.pk)
            
            else :
                specialist.full = full_name
                specialist.short_name = short_name
                specialist.description = desc

                specialist.save()

                return redirect('master:specialists')
            
        elif metode == 'delete' :
            specialist.is_active = False

            specialist.save()

            return redirect('master:specialists')

    return render(request, 'master_detail/specialist_detail.html', {
        'title' : 'Detail Specialist',
        'page_name' : f"Detail - {specialist.short_name}",
        'data' : specialist
    })