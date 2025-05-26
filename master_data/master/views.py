from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, auth, Group
from master_data.rules import *
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from master_data.local_settings import *
from sales.models import DoctorDetail
from collections import defaultdict
from django.contrib import messages
from django.urls import reverse
from .models import *
import requests
import json

@login_required
def datadoctor(request) :
    if request.method == 'POST' and request.user.is_authenticated :
        rayon_name = request.POST.get('rayon_name')

        doctors = DoctorDetail.objects.using('sales').filter(is_active=True).all()

        filtered_doctors = {
            'rayon_name' : rayon_name,
            'doctors' : []
        }

        for doc in doctors :
            try :
                rayon_data = json.loads(doc.rayon)
                if rayon_data.get('rayon') == rayon_name :
                    doc.rayon = json.loads(doc.rayon)
                    doc.info = json.loads(doc.info)

                    filtered_doctors.get('doctors').append({
                        'rayon' : doc.rayon,
                        'info' : doc.info
                    })
            except :
                continue

        return JsonResponse({'doctors' : filtered_doctors})
    return JsonResponse({'error' : 'Invalid Request'}, status=400)

@login_required
def home(request) :

    if request.user.is_staff :
        search_query = request.GET.get('search', '')

        group_count = defaultdict(lambda: {'priority': 0, 'not_priority': 0, 'total_doctor' : 0, 'id' : None})

        doctors = DoctorDetail.objects.using('sales').filter(is_active=True).all()

        prty_doctor = 0
        nt_prty_doctor = 0
        ttl_doctor = 0

        for data in doctors :
            data.rayon = json.loads(data.rayon)
            data.info = json.loads(data.info)
            data.work_information = json.loads(data.work_information)
            data.private_information = json.loads(data.private_information)
            data.additional_information = json.loads(data.additional_information)
            data.branch_information = json.loads(data.branch_information)

            rayon_name = data.rayon.get('rayon')

            sales_info = data.work_information.get('sales_information', {})
            is_priority = sales_info.get('priority', False)

            if is_priority :
                group_count[rayon_name]['priority'] += 1
                prty_doctor += 1
            else :
                group_count[rayon_name]['not_priority'] += 1
                nt_prty_doctor += 1
            
            group_count[rayon_name]['total_doctor'] += 1
            group_count[rayon_name]['id'] = data.pk
            ttl_doctor += 1
        
        group_list = [
            {   
                'id' : data['id'],
                'rayon' : rayon,
                'priority' : data['priority'],
                'not_priority' : data['not_priority'],
                'total_doctor' : data['total_doctor']
            }
            for rayon, data in group_count.items()
        ]

        all_list = {
            'doctor_priority' : prty_doctor,
            'doctor_not_priority' : nt_prty_doctor,
            'total_doctor' : ttl_doctor
        }

        if search_query :
            group_list = [
                r for r in group_list
                if (
                    search_query.lower() in str(r.get('rayon')).lower()
                )
            ]

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
            return render(request, 'core/home.html', {
                'data' : group_list
            })

        return render(request, 'core/home.html', {
            'title' : 'Dashboard',
            'page_name' : 'Home',
            'data' : group_list,
            'total' : all_list
        })
    
    else :
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
    try :
        user = request.user

        if user.is_authenticated :
            return redirect('master:home')
    
    except :
        pass

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

            try :
                token = response.json().get('token')
                detail = response.json().get('data')
                request.session['token'] = token
                request.session['detail'] = detail
            
            except ValueError :
                messages.error(request, f"Email and Password doesn't match any user. Please check your email or password.")
                return redirect('master:login')

            try :
                user = User.objects.get(email=email)
                
                if user.check_password(password) :
                    group, _ = Group.objects.get_or_create(name="sales")

                    if not user.groups.filter(name="sales").exists() :
                        user.groups.add(group)

                    login(request, user)
                    messages.success(request, f"Login Success, Welcome Back {user.username}.")
                    return redirect(next_url)
                
                else :
                    messages.error(request, "Login failed, please check your username, email, or password.")
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

                    if user.groups.filter(name="supplier").exists() and not user.first_name :
                        messages.success(request, f"Welcome back {user.username}, Don't forget to update your data <a href='{reverse('master:profile')}' class='link link-hover'>Here</a>")

                    else :
                        messages.success(request, f"Welcome back {request.user.username}.")
                    
                    return redirect(next_url)
                
                else :
                    messages.error(request, "Login failed, please check your username, email, or password.")
                    return redirect('master:login')
                
            except User.DoesNotExist :
                messages.error(request, f"Username and Password doesn't match any user. If you have entered the right Username and Password, Please contact our support team.")
                return redirect('master:login')
            
    return render(request, 'core/login.html', {
        'title' : 'Login',
        'login' : True
    })

@login_required
@group_required('supplier')
def profile(request) :
    user = request.user

    try :
        profile = Profile.objects.using('master').get(user_id=int(user.id))

        try :
            profile.addresses = json.loads(profile.addresses)
        
        except TypeError :
            profile.addresses = None

    except Profile.DoesNotExist :
        profile = None

    data = {
        'user' : user,
        'profile' : profile
    }

    if request.method == 'POST' :
        metode = request.POST.get('metode', '')
        usr = request.user

        if metode == 'change_usrnm' :
            new_usrnm = request.POST.get('usrnm', '')
            about = request.POST.get('abt', '')

            usr.username = new_usrnm
            usr.save()

            prfl, created = Profile.objects.using('master').get_or_create(
                user_id = int(usr.id)
            )

            if not created :
                prfl.about = about
                prfl.save()

            if created or prfl.about != about :
                prfl.about = about
                prfl.save()

            messages.success(request, f"Username successfully updated.")
            return redirect('master:profile')
        
        if metode == 'profile_update' :
            frst_nm = request.POST.get('nw-frstnm', '')
            lst_nm = request.POST.get('nw-lstnm', '')
            eml = request.POST.get('eml', '')

            country = request.POST.get('ctry', '')
            city = request.POST.get('cty', '')
            state = request.POST.get('stt', '')
            zp = request.POST.get('zp', '')
            flladdrs = request.POST.get('flladdrs', '')

            address = json.dumps({
                'country' : country,
                'city' : city,
                'state' : state,
                'zip' : zp,
                'full_address' : flladdrs
            })

            usr.first_name = frst_nm
            usr.last_name = lst_nm
            usr.email = eml
            usr.save()

            prfl_1, crtd = Profile.objects.using('master').get_or_create(
                user_id=int(usr.id)
            )

            if not crtd :
                prfl_1.addresses = address
                prfl_1.save()
            
            if crtd or prfl_1.addresses != address :
                prfl_1.addresses = address
                prfl_1.save()

            messages.success(request, "Profile update successfully.")
            return redirect('master:profile')
        
        if metode == 'change_pw' :
            old_password = request.POST.get('old-psswrd', '')
            new_password = request.POST.get('nw-psswrd', '')
            cnfrm_pass = request.POST.get('cnfrm-psswrd', '')

            if not check_password(old_password, usr.password) :
                messages.error(request, "Password doesn't match with the old password.")
                return redirect('master:profile')
            
            if new_password != cnfrm_pass :
                messages.error(request, "New password with confirm password doesn't match.")
                return redirect('master:profile')
            
            usr.set_password(new_password)
            usr.save()

            messages.success(request, "Change password success, remember your password. Don't share your password with anyone.")
            return redirect('master:login')

    return render(request, 'core/profile.html', {
        'title' : 'Profile',
        'page_name' : 'Profile Detail',
        'api' : "False",
        'data' : data,
    })

@login_required
def logout_view(request) :
    token = request.session.get('token')
    print(token)
    user = request.user

    if token :
        headers = {
            'Authorization' : f"Bearer {token}"
        }
        response = requests.post(logout_url(), headers=headers)

        print(response)

        if response.status_code == 200 :
            request.session.pop('token', None)
            request.session.pop('detail', None)

            request.session.flush()
            logout(request)

            messages.success(request, f"Log out success, see you next time.")
            return redirect('master:login')
        else :
            messages.error(request, f"Log out failed, please try again later.")
            return redirect('master:home')
    
    else :
        logout(request)
        messages.success(request, f"Log out success, see you next time.")
        return redirect('master:login')

@login_required
@admin_required
@group_required('sales')
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
@group_required('sales')
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
            
            messages.success(request, f"Object with {name}, successfully created.")
            return redirect('master:gc_list')

    return render(request, 'master_new/new_gc.html', {
        'title' : 'New Grade Clinic',
        'page_name' : 'New Grade Clinic'
    })

@login_required
@admin_required
@group_required('sales')
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

            messages.success(request, f"Object with {name} successfully edited.")
            return redirect('master:gc_list')
        
        elif metode == 'delete' :
            grade.range_clinic = json.dumps(grade.range_clinic)
            grade.is_active = False
            
            grade.save()

            messages.success(request, f"Object with {grade.name} successfully deleted.")
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
@group_required('sales')
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
@group_required('sales')
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
            
            messages.success(request, f"Object with {name}, successfully created.")
            return redirect('master:gu_list')

    return render(request, 'master_new/new_gu.html', {
        'title' : 'New Grade User',
        'page_name' : 'New Grade User'
    })

@login_required
@admin_required
@group_required('sales')
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

            messages.success(request, f"Object with {name}, successfully edited.")
            return redirect('master:gu_list')
        
        elif metode == 'delete' :
            gu.range_user = json.dumps(gu.range_user)
            gu.is_active = False

            gu.save()

            messages.success(request, f"Object with {gu.name}, successfully deleted.")
            return redirect('master:gu_list')

    return render(request, 'master_detail/gu_detail.html', {
        'title' : 'Detail Grade User',
        'page_name' : f"Detail User Grade - {gu.name}",
        'data' : gu
    })

@login_required
@admin_required
@group_required('sales')
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
@group_required('sales')
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

                messages.success(request, f"Object with {short_name}, successfully created.")
                return redirect('master:title_list')
        
    return render(request, 'master_new/new_title.html', {
        'title' : 'New Title',
        'page_name' : 'New Title'
    })

@login_required
@admin_required
@group_required('sales')
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

                messages.success(request, f"Object with {title.name}, successfully edited.")
                return redirect('master:title_list')
        
        elif metode == 'delete' :
            title.is_active = False

            title.save()

            messages.success(request, f"Object with {title.name}, successfully deleted.")
            return redirect('master:title_list')

    return render(request, 'master_detail/title_detail.html', {
        'title' : 'Detail Title',
        'page_name' : f"Detail - {title.short_name}",
        'data' : title
    })

@login_required
@admin_required
@group_required('sales')
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
@group_required('sales')
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

                messages.success(request, f"Object with {full_name}, successfully created.")
                return redirect('master:salutation_list')
            
    return render(request, 'master_new/new_salutation.html', {
        'title' : 'New Salutation',
        'page_name' : 'New Salutation'
    })

@login_required
@admin_required
@group_required('sales')
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

                messages.success(request, f"Object with {salutation.salutation}, successfully edited.")
                return redirect('master:salutation_list')
            
        elif metode == 'delete' :
            salutation.is_active = False

            salutation.save()

            messages.success(request, f"Object with {salutation.salutation}, successfully deleted.")
            return redirect('master:salutation_list')

    return render(request, 'master_detail/salutation_detail.html', {
        'title' : 'Detail Salutation',
        'page_name' : f"Detail - {salutation.short_salutation}",
        'data' : salutation
    })

@login_required
@admin_required
@group_required('sales')
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
@group_required('sales')
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

                messages.success(request, f"Object with {full_name}, successfully created.")
                return redirect('master:specialist_list')
            
    return render(request, 'master_new/new_specialist.html', {
        'title' : 'New Specialist',
        'page_name' : 'New Specialist'
    })

@login_required
@admin_required
@group_required('sales')
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

                messages.success(request, f"Object with {specialist.full}, successfully edited.")
                return redirect('master:specialists')
            
        elif metode == 'delete' :
            specialist.is_active = False

            specialist.save()

            messages.success(request, f"Object with {specialist.full}, successfully deleted.")
            return redirect('master:specialists')

    return render(request, 'master_detail/specialist_detail.html', {
        'title' : 'Detail Specialist',
        'page_name' : f"Detail - {specialist.short_name}",
        'data' : specialist
    })

@login_required
@admin_required
@group_required('supplier')
def pic_list(request) :
    search_query = request.GET.get('search', '')

    pics = Pic.objects.using('master').filter(is_active=True).all()

    data = []

    for pic in pics :
        pic.address = json.loads(pic.address)
        pic.contact = json.loads(pic.contact)

        data.append(pic)

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d.name).lower() or
                search_query.lower() in str(d.company).lower() or
                search_query.lower() in str(d.contact.get('email')).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/pic_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/pic_list.html', {
        'title' : "Pic List",
        'page_name' : "Pic List",
        'api' : "False",
        'new_url' : reverse('master:new_pic'),
        'page_obj' : page_obj,
    })

@login_required
@admin_required
@group_required('supplier')
def new_pic(request) :
    if request.method == 'POST' :
        metode = request.POST.get('metode', '')

        if metode == 'post' :
            name = request.POST.get('name', '')
            position = request.POST.get('position', '')
            company = request.POST.get('company', '')

            address = {
                'street_1' : request.POST.get('street-1', ''),
                'street_2' : request.POST.get('street-2', ''),
                'city' : request.POST.get('city', ''),
                'state' : request.POST.get('state', ''),
                'country' : request.POST.get('country', ''),
                'zip' : request.POST.get('zip', ''),
                'fulladdress' : request.POST.get('fll-address', '')
            }

            contact = {
                'telp_num' : request.POST.get('tlp-num', ''),
                'email' : request.POST.get('eml', ''),
                'wa_num' : request.POST.get('wa-num')
            }

            if Pic.objects.using('master').filter(name__in=name).exists() :
                messages.error(request, f"PIC with name {name} exists. Please input the different name.")
                return redirect('master:new_pic')
            
            else :
                Pic.objects.using('master').create(
                    name=str(name).title().strip(),
                    position=str(position).title().strip(),
                    company=str(company).title().strip(),
                    address=json.dumps(address),
                    contact=json.dumps(contact),
                    added=request.user.id,
                    updated=request.user.id
                )

                messages.success(request, f"Object with {name}, successfully created.")
                return redirect('master:pic_list')

    return render(request, 'master_new/new_pic.html', {
        'title' : "New Pic",
        'page_name' : "New Pic",
        'api' : "False"
    })

@login_required
@admin_required
@group_required('supplier')
def detail_pic(request, pic_id) :
    pic = Pic.objects.using('master').get(id=int(pic_id))
    pic.address = json.loads(pic.address)
    pic.contact = json.loads(pic.contact)

    if request.method == 'POST' :
        metode = request.POST.get('metode', '')

        if metode == 'post' :
            pic.name = str(request.POST.get('name', '')).title().strip()
            pic.position = str(request.POST.get('position', '')).title().strip()
            pic.company = str(request.POST.get('company', '')).title().strip()
            pic.contact = json.dumps({
                'telp_num' : request.POST.get('tlp-num', ''),
                'email' : request.POST.get('eml', ''),
                'wa_num' : request.POST.get('wa-num')
            })
            pic.address = json.dumps({
                'street_1' : request.POST.get('street-1', ''),
                'street_2' : request.POST.get('street-2', ''),
                'city' : request.POST.get('city', ''),
                'state' : request.POST.get('state', ''),
                'country' : request.POST.get('country', ''),
                'zip' : request.POST.get('zip', ''),
                'fulladdress' : request.POST.get('fll-address', '')
            })
            pic.updated = request.user.id

            pic.save()
            
            messages.success(request, f"Object with {pic.name}, successfully edited.")
            return redirect('master:pic_list')
        
        elif metode == 'delete' :
            pic.address = json.dumps(pic.address)
            pic.contact = json.dumps(pic.contact)
            pic.is_active = False
            pic.save()

            messages.success(request, f"Object with {pic.name}, successfully deleted.")
            return redirect('master:pic_list')

    return render(request, 'master_detail/pic_detail.html', {
        'title' : "Detail Pic",
        'page_name' : f"Detail Pic {pic.name}",
        'api' : "False",
        'data' : pic
    })      

@login_required
@admin_required
@group_required('supplier')
def classfication_list(request) :
    search_query = request.GET.get('search', '')

    classes = Classification.objects.using('master').filter(is_active=True).order_by('-updated_at')

    if search_query :
        classes = [
            data for data in classes
            if (
                search_query.lower() in str(data.name).lower()
            )
        ]

    paginator = Paginator(classes, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/classification_list.html', {
            'page_obj' : page_obj
        })
    
    return render(request, 'master_pages/classification_list.html', {
        'title' : "Classification List",
        'page_name' : "Classification List",
        'api' : "False",
        'page_obj' : page_obj,
        'new_url' : reverse('master:new_classification')
    })

@login_required
@admin_required
@group_required('supplier')
def new_classification(request) :
    if request.method == 'POST' :
        metode = request.POST.get('metode', '')

        if metode == 'post' :
            class_name = request.POST.get('class-name', '')
            description = request.POST.get('description', '')

            if Classification.objects.using('master').filter(name__in=class_name).exists() :
                messages.error(request, f"Object with {class_name} already exists.")
                return redirect('master:classification_list')
            
            Classification.objects.using('master').create(
                name=str(class_name).strip(),
                description=description,
                created_by=request.user.id,
                updated_by=request.user.id
            )

            messages.success(request, f"Object with {class_name}, Successfully added.")
            return redirect('master:classification_list')

    return render(request, 'master_new/new_classification.html', {
        'title' : "New Classification",
        'page_name' : "New Classification",
        'api' : "False"
    })

@login_required
@admin_required
@group_required('supplier')
def detail_classification(request, class_id) :
    classif = Classification.objects.using('master').get(id=int(class_id))

    if request.method == 'POST' :
        metode = request.POST.get('metode', '')

        if metode == 'post' :
            name = request.POST.get('class-name', '')
            description = request.POST.get('description', '')

            classif.name = str(name).strip()
            classif.description = description
            classif.updated_by = request.user.id

            classif.save()

            messages.success(request, f"Object with {classif.name} successfully updated.")
            return redirect('master:classification_list')
        
        elif metode == 'delete' :
            classif.is_active=False
            classif.save()

            messages.success(request, f"Object with {classif.name}, successfully deleted.")
            return redirect('master:classification_list')

    return render(request, 'master_detail/classification_detail.html', {
        'title' : "Detail Classification",
        'page_name' : "Detail Classification",
        'api' : "False",
        'data' : classif
    })