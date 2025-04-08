from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from functools import wraps
import json
import random
import string
import requests
from .models import *
from master.models import *
from human_resource.models import *

API_LOGIN_URL = "https://dev-bco.businesscorporateofficer.com/api/login/"
API_LOGOUT_URL = "https://dev-bco.businesscorporateofficer.com/api/logout/"

def index_sales(request) :
    return redirect('master:login')

def api_login_required(view_func) :
    @wraps(view_func)
    def wrapper(request, *args, **kwargs) :
        if not request.session.get('token') :
            return redirect('master:login')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def remove_duplicates(text) :
    if not text :
        return ''
    
    unique_values = list(set(text.split(', ')))
    return ', '.join(unique_values)

@api_login_required
def doctor_list(request) :
    id_user = request.session.get('detail').get('id_user')

    if int(id_user) == 7 :
        page = request.GET.get('page', '1')
        search = request.GET.get('search', '')

        api_url = f"https://dev-bco.businesscorporateofficer.com/api/master-data-dokter/filter/"

        response = requests.post(api_url, params={'page' : page}, data={'keyword' : search})

        if response.status_code == 200 :
            dt = response.json()

            page_obj = []

            for t in dt.get('data').get('data') :

                old_code = t.get('kode_pelanggan_old')

                if old_code :
                    distinct_old_code = remove_duplicates(old_code)
                    t['kode_pelanggan_old'] = distinct_old_code

                if DoctorDetail.objects.using('sales').filter(jamet_id=int(t.get('id_dokter'))).exists() :
                    dr = DoctorDetail.objects.using('sales').get(jamet_id=int(t.get('id_dokter')))
                    last_update = dr.updated_at
                    rayon = json.loads(dr.rayon)
                    i = json.loads(dr.work_information).get('sales_information').get('priority')

                    if int(i) == 1 :
                        priority = "Priority"

                    else :
                        priority = "Bukan Prioritas"
                    
                else :
                    last_update = "Not Found"
                    priority = "Not Set"
                    rayon = None
                
                page_obj.append({
                    'data' : t,
                    'last_update' : last_update,
                    'priority' : priority,
                    'cover' : rayon
                })

        return render(request, 'sales_pages/doctor_list.html', {
            'title' : 'Doctor List',
            'page_name' : 'Doctor List',
            'page_obj' : page_obj,
            'current_page' : dt.get('data').get('current_page'),
            'last_page' : dt.get('data').get('last_page'),
            'next_page' : dt.get('data').get('next_page_url'),
            'prev_page' : dt.get('data').get('prev_page_url'),
            'api' : "True"
        })

    else :
        api_url = f"https://dev-bco.businesscorporateofficer.com/api/master-data-dokter/{id_user}/"

        response = requests.get(api_url)

        if response.status_code == 200 :
            search_query = request.GET.get('search')

            api_data = response.json()

            data = []

            for d in api_data.get('data') :
                if DoctorDetail.objects.using('sales').filter(jamet_id=d.get('id_dokter')).exists() :
                    dd = DoctorDetail.objects.using('sales').get(jamet_id=d.get('id_dokter'))
                    last_update = dd.updated_at
                    rayon = json.loads(dd.rayon)
                    i = json.loads(dd.work_information).get('sales_information').get('priority')

                    if i == 1 :
                        priority = "Priority"
                    
                    else :
                        priority = "Not Priority"

                else :
                    last_update = "Not Found"
                    priority = "Not Set"
                    rayon = None
                
                data.append({
                    'data' : d,
                    'last_update' : last_update,
                    'priority' : priority,
                    'cover' : rayon
                })

            if search_query :
                data = [                
                    d for d in data
                    if (
                        search_query.lower() in str(d['data'].get('nama_dokter')).lower() or
                        search_query.lower() in str(d['data'].get('kode_pelanggan')).lower() or
                        search_query.lower() in str(d['priority']).lower()
                    )
                ]

            paginator = Paginator(data, 12)

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
                return render(request, 'sales_pages/doctor_list.html', {
                    'page_obj' : page_obj
                })

        return render(request, 'sales_pages/doctor_list.html', {
            'title' : 'Doctor List',
            'page_name' : 'Doctor List',
            'page_obj' : page_obj,
            'api' : "False"
        })

@api_login_required
def doctor_detail(request, user_id, doc_id) :
    id_user = request.session.get('detail').get('id_user')
    api_url = f"https://dev-bco.businesscorporateofficer.com/api/master-data-dokter/{user_id}/"
    
    response = requests.get(api_url)

    if response.status_code == 200 :
        api_data = response.json()

        drs = api_data.get('data')

        dr_detail = next((drr for drr in drs if drr['id_dokter'] == doc_id), None)

        if dr_detail :

            data = []

            grade_users = UserGrade.objects.using('master').filter(is_active=True).all()
            grade_clinics = ClinicGrade.objects.using('master').filter(is_active=True).all()
            salutations = Salutation.objects.using('master').filter(is_active=True).all()
            titles = Title.objects.using('master').filter(is_active=True).all()
            specialists = Specialist.objects.using('master').filter(is_active=True).all()

            if DoctorDetail.objects.using('sales').filter(jamet_id=doc_id).exists() :
                doctor = DoctorDetail.objects.using('sales').get(jamet_id=doc_id)
                doctor.info = json.loads(doctor.info)
                doctor.work_information = json.loads(doctor.work_information)
                doctor.private_information = json.loads(doctor.private_information)
                doctor.branch_information = json.loads(doctor.branch_information)
                doctor.additional_information = json.loads(doctor.additional_information)
                doctor.rayon = json.loads(doctor.rayon)
            
            else :
                doctor = None

            data.append({
                'grade_user' : grade_users,
                'grade_clinic' : grade_clinics,
                'salutations' : salutations,
                'titles' : titles,
                'specialists' : specialists,
                'doctor' : doctor,
                'dr_api' : dr_detail
            })

            if request.method == 'POST' :
                metode = request.POST.get('metode')

                if data[0]['doctor'] :
                    if data[0]['doctor'].rayon.get('id') == request.session.get('detail').get('id_user') :
                        pass

                    else :
                        return redirect('sales:doctor_detail', user_id=user_id, doc_id=doc_id)
                    
                else :
                    pass

                if metode == 'post' :
                    """
                    Info
                    """
                    first_name = request.POST.get('first-name','')
                    middle_name = request.POST.get('middle-name','')
                    last_name = request.POST.get('last-name','')
                    full_name = request.POST.get('full-name','')
                    salutation_id = request.POST.get('sal-num','')
                    title_id = request.POST.get('tit-num','')

                    if salutation_id != '' :
                        salutation = Salutation.objects.using('master').get(id=int(salutation_id)).pk
                    
                    else :
                        salutation = None


                    if title_id != '' :
                        title = Title.objects.using('master').get(id=int(title_id)).pk

                    else :
                        title = None


                    info = {
                        'first_name' : str(first_name).upper().strip(),
                        'middle_name' : str(middle_name).upper().strip(),
                        'last_name' : str(last_name).upper().strip(),
                        'full_name' : str(full_name).upper().strip(),
                        'salutation' : salutation,
                        'title' : title
                    }

                    """
                    Work Information
                    """

                    #Work Location
                    
                    ##Address
                    work_street_1 = request.POST.get('work-street-1','')
                    work_street_2 = request.POST.get('work-street-2','')
                    work_city = request.POST.get('work-city','')
                    work_state = request.POST.get('work-state','')
                    work_country = request.POST.get('work-country','')
                    work_zip = request.POST.get('work-zip','')
                    work_fulladdress = request.POST.get('fll-work-address','')

                    #Job Information
                    workspace_name = request.POST.get('workspace-name','')
                    job_position = request.POST.get('job-position','')
                    work_phone = request.POST.get('work-phone','')
                    work_mobile = request.POST.get('work-mobile','')
                    work_email = request.POST.get('work-email','')

                    #Sales Information
                    grade_user_id = request.POST.get('grade-user','')
                    grade_clinic_id = request.POST.get('grade-clinic','')
                    priority = request.POST.get('priority','')
                    specialist_id = request.POST.get('specialists','')

                    #System Information
                    accurate_code = request.POST.get('accurate-code','')

                    if grade_user_id != '' :
                        grade_user = UserGrade.objects.using('master').get(id=int(grade_user_id)).pk
                    else :
                        grade_user = None

                    if grade_clinic_id != '' :
                        grade_clinic = ClinicGrade.objects.using('master').get(id=int(grade_clinic_id)).pk
                    else :
                        grade_clinic = None

                    if specialist_id != '' :
                        specialist = Specialist.objects.using('master').get(id=int(specialist_id)).pk
                    else :
                        specialist = None

                    work_information = {
                        'address' : {
                            'street_1' : str(work_street_1).upper().strip(),
                            'street_2' : str(work_street_2).upper().strip(),
                            'city' : str(work_city).upper().strip(),
                            'state' : str(work_state).upper().strip(),
                            'country' : str(work_country).upper().strip(),
                            'zip' : str(work_zip).upper().strip(),
                            'fulladdress' : str(work_fulladdress).upper().strip()
                        },
                        'job_information' : {
                            'workspace_name' : str(workspace_name).upper().strip(),
                            'job_position' : str(job_position).upper().strip(),
                            'work_phone' : str(work_phone).upper().strip(),
                            'work_mobile' : str(work_mobile).upper().strip(),
                            'work_email' : str(work_email).strip()
                        },
                        'sales_information' : {
                            'grade_user' : grade_user,
                            'grade_clinic' : grade_clinic,
                            'priority' : int(priority),
                            'specialist_id' : specialist
                        },
                        'system_information' : {
                            'accurate_code' : str(accurate_code).upper().strip() if accurate_code else None
                        }
                    }

                    """
                    Private Information
                    """

                    #Private Contact
                    
                    ##Private Address
                    private_street_1 = request.POST.get('private-street-1','')
                    private_street_2 = request.POST.get('private-street-2','')
                    private_city = request.POST.get('private-city','')
                    private_state = request.POST.get('private-state','')
                    private_country = request.POST.get('private-country','')
                    private_zip = request.POST.get('private-zip','')

                    private_email = request.POST.get('private-email','')
                    private_phone = request.POST.get('private-phone','')

                    #Citizenship
                    nationality = request.POST.get('nationality','')
                    gender = request.POST.get('gender','')
                    birth_date = request.POST.get('birthday','')
                    birth_place = request.POST.get('birthplace','')
                    religion = request.POST.get('religion','')

                    #Education
                    certification = request.POST.get('certification-level','')
                    field_study = request.POST.get('field-study','')
                    school_name = request.POST.get('school-name','')

                    #Family
                    marital_status = request.POST.get('marital-status','')

                    #Spouse
                    spouse_firstnames = request.POST.getlist('spouse_first_name', '')
                    spouse_middlenames = request.POST.getlist('spouse_middle_name', '')
                    spouse_lastnames = request.POST.getlist('spouse_last_name', '')
                    spouse_fullnames = request.POST.getlist('spouse_full_name', '')
                    spouse_birthdates = request.POST.getlist('spouse_birthday', '')
                    spouse_phone = request.POST.getlist('spouse_phone', '')
                    mariage_date = request.POST.getlist('spouse_marriage_date', '')

                    #Children
                    children_firstnames = request.POST.getlist('children_first_name', '')
                    children_middlenames = request.POST.getlist('children_middle_name', '')
                    children_lastnames = request.POST.getlist('children_last_name', '')
                    children_fullnames = request.POST.getlist('children_full_name', '')
                    children_birthdates = request.POST.getlist('children_birthday', '')
                    children_phone = request.POST.getlist('children_phone', '')

                    spouses = []
                    for s_firstname, s_middlename, s_lastname, s_fullname, s_birthdate, s_phone, s_mariage in zip(spouse_firstnames, spouse_middlenames, spouse_lastnames, spouse_fullnames, spouse_birthdates, spouse_phone, mariage_date) :
                        spouses.append({
                            'firstname' : str(s_firstname).upper().strip(),
                            'middlename' : str(s_middlename).upper().strip(),
                            'lastname' : str(s_lastname).upper().strip(),
                            'fullname' : str(s_fullname).upper().strip(),
                            'birthdate' : str(s_birthdate).upper().strip(),
                            'phone' : str(s_phone).upper().strip(),
                            'mariage_date' : str(s_mariage).upper().strip()
                        })

                    childrens = []
                    for c_firstname, c_middlename, c_lastname, c_fullname, c_birthdate, c_phone in zip(children_firstnames, children_middlenames, children_lastnames, children_fullnames, children_birthdates, children_phone) :
                        childrens.append({
                            'firstname' : str(c_firstname).upper().strip(),
                            'middlename' : str(c_middlename).upper().strip(),
                            'lastname' : str(c_lastname).upper().strip(),
                            'fullname' : str(c_fullname).upper().strip(),
                            'birthdate' : str(c_birthdate).upper().strip(),
                            'phone' : str(c_phone).upper().strip()
                        })

                    private_information = {
                        'private_contact' : {
                            'address' : {
                                'street_1' : str(private_street_1).upper().strip(),
                                'street_2' : str(private_street_2).upper().strip(),
                                'city' : str(private_city).upper().strip(),
                                'state' : str(private_state).upper().strip(),
                                'country' : str(private_country).upper().strip(),
                                'zip' : str(private_zip).upper().strip()
                            },
                            'email' : str(private_email).upper().strip(),
                            'phone' : str(private_phone).upper().strip()
                        },
                        'citizenship' : {
                            'nationality' : str(nationality).upper().strip(),
                            'gender' : str(gender).upper().strip(),
                            'birth_date' : str(birth_date).upper().strip(),
                            'birth_place' : str(birth_place).upper().strip(),
                            'religion' : str(religion).upper().strip()
                        },
                        'education' : {
                            'certification' : str(certification).upper().strip(),
                            'field_study' : str(field_study).upper().strip(),
                            'school_name' : str(school_name).upper().strip()
                        },
                        'family' : {
                            'marital_status' : str(marital_status).upper().strip(),
                            'spouse' : spouses,
                            'children' : childrens
                        }
                    }

                    """
                    Additional Information
                    """

                    #Interest
                    category_interest = request.POST.getlist('interest-category', '')
                    interests = request.POST.getlist('interest-name', '')

                    #Social Media
                    category_socmed = request.POST.getlist('socmed-name', '')
                    socmeds = request.POST.getlist('socmed-account-name', '')

                    interest_data = []
                    for category_interest, interest in zip(category_interest, interests) :
                        interest_data.append({
                            'category' : str(category_interest).title().strip(),
                            'interest' : str(interest).title().strip()
                        })

                    socmed_data = []
                    for socmed_name, account_name in zip(category_socmed, socmeds) :
                        socmed_data.append({
                            'name' : str(socmed_name).title().strip(),
                            'account_name' : str(account_name)
                        })

                    additional_information = {
                        'interests' : interest_data,
                        'social_media' : socmed_data
                    }

                    """
                    Branch Information
                    """
                    branches_name = request.POST.getlist('branch-name', '')
                    branches_date = request.POST.getlist('branch-est-date', '')
                    branches_street_1 = request.POST.getlist('branch-street-1', '')
                    branches_street_2 = request.POST.getlist('branch-street-2', '')
                    branches_city = request.POST.getlist('branch-city', '')
                    branches_state = request.POST.getlist('branch-state', '')
                    branches_country = request.POST.getlist('branch-country', '')
                    branches_zip = request.POST.getlist('branch-zip', '')

                    branches = []
                    for (
                            branch_name, 
                            branch_date,
                            branch_street_1,
                            branch_street_2,
                            branch_city,
                            branch_state,
                            branch_country,
                            branch_zip
                        ) in zip(
                            branches_name, 
                            branches_date, 
                            branches_street_1, 
                            branches_street_2,
                            branches_city,
                            branches_state,
                            branches_country,
                            branches_zip
                        ) :
                        branches.append({
                            'branch_name' : branch_name,
                            'branch_established_date' : branch_date,
                            'branch_street_1' : branch_street_1,
                            'branch_street_2' : branch_street_2,
                            'branch_city' : branch_city,
                            'branch_state' : branch_state,
                            'branch_country' : branch_country,
                            'branch_zip' : branch_zip
                        })

                    initial_first = str(first_name)[:3].upper()
                    initial_last = str(last_name)[:3].upper()
                    salutation_code = str(Salutation.objects.using('master').get(id=salutation).salutation)[:2].upper()
                    random_number = ''.join(random.choices(string.digits, k=4))
                    code = f"{salutation_code}/{initial_first}/{initial_last}/{random_number}"

                    rayon = {
                        'id' : int(request.session['detail'].get('id_user')),
                        'rayon' : request.session['detail'].get('kode_rayon')
                    }

                    while DoctorDetail.objects.using('sales').filter(code=code).exists() :
                        random_number = ''.join(random.choices(string.digits, k=4))
                        code = f"{salutation_code}/{initial_first}/{initial_last}/{random_number}"

                    if DoctorDetail.objects.using('sales').filter(jamet_id=int(doc_id)).exists() :
                        dd = DoctorDetail.objects.using('sales').get(jamet_id=int(doc_id))

                        dd.info = json.dumps(info)
                        dd.work_information = json.dumps(work_information)
                        dd.private_information = json.dumps(private_information)
                        dd.additional_information = json.dumps(additional_information)
                        dd.branch_information = json.dumps(branches)

                        dd.save()

                        return redirect('sales:doctor_list')
                    
                    else :
                        dr = DoctorDetail.objects.using('sales').create(
                            code = code,
                            jamet_id = int(doc_id),
                            info = json.dumps(info),
                            work_information = json.dumps(work_information),
                            private_information = json.dumps(private_information),
                            additional_information = json.dumps(additional_information),
                            branch_information = json.dumps(branches),
                            rayon = json.dumps(rayon)
                        )

                        dr.save()

                        return redirect('sales:doctor_list')

            return render(request, 'sales_detail/doctor_detail.html', {
                'title' : 'Detail Doctor',
                'page_name' : 'Detail Doctor',
                'data' : data
            })
        
    else:
        return render(request, 'error.html', {'message': 'Dokter tidak ditemukan'})