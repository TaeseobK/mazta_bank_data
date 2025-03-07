from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import random
import string
import requests
from .models import *
from master.models import *
from human_resource.models import *

@login_required(login_url='/login/')
def doctor_list(request) :
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    api_url = f"https://dev-bco.businesscorporateofficer.com/api/master-data-dokter?page={page_number}&keyword={search_query}"

    response = requests.get(api_url)

    if response.status_code == 200 :
        api_data = response.json()

        data = []

        for d in api_data.get('data').get('data') :
            if DoctorDetail.objects.using('sales').filter(jamet_id=d.get('id_dokter')).exists() :
                dd = DoctorDetail.objects.using('sales').get(jamet_id=d.get('id_dokter'))
                last_update = dd.updated_at
            else :
                last_update = "Not Found"
            
            data.append({
                'data' : d,
                'last_update' : last_update
            })

        current_page = api_data.get('data').get('current_page')
        last_page = api_data.get('data').get('last_page')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
            return render(request, 'sales_pages/doctor_list.html', {
                'page_obj' : data,
                'current_page' : current_page,
                'last_page' : last_page
            })

    return render(request, 'sales_pages/doctor_list.html', {
        'title' : 'Doctor List',
        'page_name' : 'Doctor List',
        'page_obj' : data,
        'current_page' : current_page,
        'last_page' : last_page
    })

@login_required(login_url='/login/')
def doctor_new(request) :
    return render(request, 'sales_new/doctor_new.html', {
        'title' : 'New Doctor',
        'page_name' : 'New Doctor'
    })

@login_required(login_url='/login/')
def doctor_detail(request, doc_id, doc_name) :
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
        'doc_name' : doc_name,
        'specialists' : specialists,
        'doctor' : doctor
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
                'first_name' : first_name,
                'middle_name' : middle_name,
                'last_name' : last_name,
                'full_name' : full_name,
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
                    'street_1' : work_street_1,
                    'street_2' : work_street_2,
                    'city' : work_city,
                    'state' : work_state,
                    'country' : work_country,
                    'zip' : work_zip,
                    'fulladdress' : work_fulladdress
                },
                'job_information' : {
                    'workspace_name' : workspace_name,
                    'job_position' : job_position,
                    'work_phone' : work_phone,
                    'work_mobile' : work_mobile,
                    'work_email' : work_email
                },
                'sales_information' : {
                    'grade_user' : grade_user.pk,
                    'grade_clinic' : grade_clinic.pk,
                    'priority' : int(priority),
                    'specialist_id' : specialist.pk if specialist else None
                },
                'system_information' : {
                    'accurate_code' : accurate_code
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
                    'firstname' : s_firstname,
                    'middlename' : s_middlename,
                    'lastname' : s_lastname,
                    'fullname' : s_fullname,
                    'birthdate' : s_birthdate,
                    'phone' : s_phone,
                    'mariage_date' : s_mariage
                })

            childrens = []
            for c_firstname, c_middlename, c_lastname, c_fullname, c_birthdate, c_phone in zip(children_firstnames, children_middlenames, children_lastnames, children_fullnames, children_birthdates, children_phone) :
                childrens.append({
                    'firstname' : c_firstname,
                    'middlename' : c_middlename,
                    'lastname' : c_lastname,
                    'fullname' : c_fullname,
                    'birthdate' : c_birthdate,
                    'phone' : c_phone
                })

            private_information = {
                'private_contact' : {
                    'address' : {
                        'street_1' : private_street_1,
                        'street_2' : private_street_2,
                        'city' : private_city,
                        'state' : private_state,
                        'country' : private_country,
                        'zip' : private_zip
                    },
                    'email' : private_email,
                    'phone' : private_phone
                },
                'citizenship' : {
                    'nationality' : nationality,
                    'gender' : gender,
                    'birth_date' : birth_date,
                    'birth_place' : birth_place,
                    'religion' : religion
                },
                'education' : {
                    'certification' : certification,
                    'field_study' : field_study,
                    'school_name' : school_name
                },
                'family' : {
                    'marital_status' : marital_status,
                    'spouse' : spouses,
                    'children' : childrens
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
                    'category' : category_hobby,
                    'hobby' : hobby
                })

            interest_data = []
            for category_interest, interest in zip(category_interest, interests) :
                interest_data.append({
                    'category' : category_interest,
                    'interest' : interest
                })

            socmed_data = []
            for socmed_name, account_name in zip(category_socmed, socmeds) :
                socmed_data.append({
                    'name' : socmed_name,
                    'account_name' : account_name
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
                    branch_information = json.dumps(branches)
                )

                dr.save()

                return redirect('sales:doctor_list')

    return render(request, 'sales_detail/doctor_detail.html', {
        'title' : 'Detail Doctor',
        'page_name' : 'Detail Doctor',
        'data' : data
    })