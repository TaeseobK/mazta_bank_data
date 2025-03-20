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
    return redirect('sales:login_2')

def api_login_required(view_func) :
    @wraps(view_func)
    def wrapper(request, *args, **kwargs) :
        if not request.session.get('token') :
            return redirect('sales:login_2')
        
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
            'api' : 'False'
        })

@api_login_required
def doctor_detail(request, user_id, doc_id) :
    id_user = request.session.get('detail').get('id_user')

    if int(id_user) == 7 :
        api_url = f"https://dev-bco.businesscorporateofficer.com/api/master-data-dokter/filter/"

    else :
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

                    if metode == 'post' :
                        """
                        Info
                        """
                        first_name = request.POST['firstname']
                        middle_name = request.POST['middlename']
                        last_name = request.POST['lastname']
                        full_name = request.POST['fullname']
                        salutation_id = request.POST['salutation']
                        title_id = request.POST['title']

                        salutation = Salutation.objects.using('master').get(id=int(salutation_id))
                        title = Title.objects.using('master').get(id=int(title_id))

                        info = {
                            'first_name' : str(first_name).upper().strip(),
                            'middle_name' : str(middle_name).upper().strip(),
                            'last_name' : str(last_name).upper().strip(),
                            'full_name' : str(full_name).upper().strip(),
                            'salutation' : salutation.pk,
                            'title' : title.pk
                        }

                        """
                        Work Information
                        """

                        #Work Location
                        
                        ##Address
                        work_street_1 = request.POST['work-street-1']
                        work_street_2 = request.POST['work-street-2']
                        work_city = request.POST['work-city']
                        work_state = request.POST['work-state']
                        work_country = request.POST['work-country']
                        work_zip = request.POST['work-zip']
                        work_fulladdress = request.POST['work-fulladdress']

                        #Job Information
                        workspace_name = request.POST['workspace-name']
                        job_position = request.POST['job-position']
                        work_phone = request.POST['work-phone']
                        work_mobile = request.POST['work-mobile']
                        work_email = request.POST['work-email']

                        #Sales Information
                        grade_user_id = request.POST['grade-user']
                        grade_clinic_id = request.POST['grade-clinic']
                        priority = request.POST['ispriority']
                        specialist_id = request.POST.get('spec_id')

                        #System Information
                        accurate_code = request.POST['accurate-code']

                        grade_user = UserGrade.objects.using('master').get(id=int(grade_user_id))
                        grade_clinic = ClinicGrade.objects.using('master').get(id=int(grade_clinic_id))
                        specialist = Specialist.objects.using('master').get(id=int(specialist_id))

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
                                'work_email' : str(work_email).upper().strip()
                            },
                            'sales_information' : {
                                'grade_user' : grade_user.pk,
                                'grade_clinic' : grade_clinic.pk,
                                'priority' : int(priority),
                                'specialist_id' : specialist.pk if specialist else None
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
                        private_street_1 = request.POST['private-street-1']
                        private_street_2 = request.POST['private-street-2']
                        private_city = request.POST['private-city']
                        private_state = request.POST['private-state']
                        private_country = request.POST['private-country']
                        private_zip = request.POST['private-zip']

                        private_email = request.POST['private-email']
                        private_phone = request.POST['private-phone']

                        #Citizenship
                        nationality = request.POST['nationality']
                        gender = request.POST['gender']
                        birth_date = request.POST['birthdate']
                        birth_place = request.POST['birthplace']
                        religion = request.POST['religion']

                        #Education
                        certification = request.POST['certification']
                        field_study = request.POST['field-study']
                        school_name = request.POST['school-name']

                        #Family
                        marital_status = request.POST['marital']

                        #Spouse
                        spouse_firstnames = request.POST.getlist('spouse-firstname[]')
                        spouse_middlenames = request.POST.getlist('spouse-middlename[]')
                        spouse_lastnames = request.POST.getlist('spouse-lastname[]')
                        spouse_fullnames = request.POST.getlist('spouse-fullname[]')
                        spouse_birthdates = request.POST.getlist('spouse-birthday[]')
                        spouse_phone = request.POST.getlist('spouse-phone[]')
                        mariage_date = request.POST.getlist('spouse-mariage[]')

                        #Children
                        children_firstnames = request.POST.getlist('children-firstname[]')
                        children_middlenames = request.POST.getlist('children-middlename[]')
                        children_lastnames = request.POST.getlist('children-lastname[]')
                        children_fullnames = request.POST.getlist('children-fullname[]')
                        children_birthdates = request.POST.getlist('children-birthday[]')
                        children_phone = request.POST.getlist('children-phone[]')

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
                                'spouse' : str(spouses).upper().strip(),
                                'children' : str(childrens).upper().strip()
                            }
                        }

                        """
                        Additional Information
                        """
                        #Hobbies
                        category_hobbies = request.POST.getlist('category-hobbies[]')
                        hobbies = request.POST.getlist('hobbies[]')

                        #Interest
                        category_interest = request.POST.getlist('category-interest[]')
                        interests = request.POST.getlist('interest[]')

                        #Social Media
                        category_socmed = request.POST.getlist('category-sosmed[]')
                        socmeds = request.POST.getlist('sosmed[]')

                        hobby_data = []
                        for category_hobby, hobby in zip(category_hobbies, hobbies) :
                            hobby_data.append({
                                'category' : str(category_hobby).upper().strip(),
                                'hobby' : str(hobby).upper().strip()
                            })

                        interest_data = []
                        for category_interest, interest in zip(category_interest, interests) :
                            interest_data.append({
                                'category' : str(category_interest).upper().strip(),
                                'interest' : str(interest).upper().strip()
                            })

                        socmed_data = []
                        for socmed_name, account_name in zip(category_socmed, socmeds) :
                            socmed_data.append({
                                'name' : str(socmed_name).upper().strip(),
                                'account_name' : str(account_name).upper().strip()
                            })

                        additional_information = {
                            'hobbies' : json.dumps(hobby_data),
                            'interests' : json.dumps(interest_data),
                            'social_media' : json.dumps(socmed_data)
                        }

                        """
                        Branch Information
                        """
                        branches_name = request.POST.getlist('branch-name[]')
                        branches_date = request.POST.getlist('established-date[]')
                        branches_address = request.POST.getlist('branch-address[]')

                        branches = []
                        for branch_name, branch_date, branch_address in zip(branches_name, branches_date, branches_address) :
                            branches.append({
                                'branch_name' : branch_name,
                                'branch_established_date' : branch_date,
                                'branch_address' : branch_address
                            })

                        initial_first = str(first_name)[0].upper()
                        initial_last = str(last_name)[0].upper()
                        salutation_code = str(salutation.salutation)[:2].upper()
                        random_number = ''.join(random.choices(string.digits, k=4))
                        code = f"{salutation_code}/{initial_first}/{initial_last}/{random_number}"

                        rayon = {
                            'id' : int(request.session['detail'].get('id_user')),
                            'rayon' : request.session['detail'].get('name')
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