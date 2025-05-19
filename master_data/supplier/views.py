from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import *
from django.core.paginator import Paginator
from master_data.rules import *
from django.contrib import messages
from master.models import Pic, Classification

@login_required
@group_required('supplier')
def vendor_list(request) :
    search_query = request.GET.get('search', '')

    data = []
    vendors = Vendor.objects.using('supplier').filter(is_active=True).all().order_by('-created_at')

    for vendor in vendors :
        vendor.address = json.loads(vendor.address)
        vendor.bank_info = json.loads(vendor.bank_info)
        vendor.status = json.loads(vendor.status)
        vendor.pic = json.loads(vendor.pic)
        pi = []
        for pic in vendor.pic :
            pics = Pic.objects.using('master').get(id=int(pic))
            pics.contact = json.loads(pics.contact)
            pi.append(pics)
        
        vendor.pic = pi

        data.append(vendor)

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d.name).lower() or
                search_query.lower() in str(d.entity).lower() or
                search_query.lower() in str(d.npwp).lower() or
                search_query.lower() in ' '.join(str(r.name) for r in d.pic) or
                search_query.lower() in ' '.join(str(r.contact.get('email')) for r in d.pic)
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'supplier_pages/vendor_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'supplier_pages/vendor_list.html', {
        'title' : "Vendor List",
        'page_name' : "Vendor List",
        'api' : "False",
        'page_obj' : page_obj,
        'new_url' : reverse('supplier:vendor_new')
    })

@login_required
@group_required('supplier')
def new_vendor(request) :
    pics = Pic.objects.using('master').filter(is_active=True).all()
    classifications = Classification.objects.using('master').filter(is_active=True).all()

    data = [{
        'pics' : pics,
        'class' : classifications
    }]

    if request.method == 'POST' :
        metode = request.POST.get('metode', '')

        if metode == 'post' :
            name = request.POST.get('name', '')
            entity = request.POST.get('entity', '')
            classification = request.POST.get('clss', '')
            npwp = request.POST.get('npwp', '')

            try :
                clss = Classification.objects.using('master').get(id=int(classification))
            except ValueError or Classification.DoesNotExist :
                clss = None

            street_1 = request.POST.get('street-1', '')
            street_2 = request.POST.get('street-2', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            country = request.POST.get('country', '')
            zip_num = request.POST.get('zip', '')
            fll_addrs = request.POST.get('fll-address', '')

            #listing
            banks_name = request.POST.getlist('bank-name[]') or []
            accs_num = request.POST.getlist('acc-num[]') or []
            tlps_num = request.POST.getlist('tlp-num[]') or []
            swts_code = request.POST.getlist('swt-code[]') or []
            banks_addrs = request.POST.getlist('bank-addrs[]') or []

            bank_info = []
            for bank_name, acc_number, tlp_number, swft_code, bank_address in zip(banks_name, accs_num, tlps_num, swts_code, banks_addrs) :
                bank_info.append({
                    'bank_name' : bank_name,
                    'account_number' : acc_number,
                    'bank_tlp_number' : tlp_number,
                    'swift_code' : swft_code,
                    'bank_address' : bank_address
                })

            pics = request.POST.getlist('pic[]', [])

            person = []
            for pic in pics :

                try :
                    pi = Pic.objects.using('master').get(id=int(pic))
                except ValueError or Pic.DoesNotExist :
                    pi = None
                
                person.append(pi.pk if pi else None)

            verif = request.POST.getlist('verif[]', '[]')
            verif_status = request.POST.getlist('verif-sts[]', '[]')

            verification = []
            for ver, ver_sts in zip(verif, verif_status) :

                verification.append({
                    'verification' : ver,
                    'verification_status' : ver_sts
                })

            if Vendor.objects.using('supplier').filter(name__in=name).exists() :
                messages.error(request, f"Object with {name}, already exists.")
                return redirect('supplier:vendor_list')
            
            Vendor.objects.using('supplier').create(
                name=name,
                entity=entity,
                npwp=npwp,
                pic=json.dumps(pics),
                address=json.dumps({
                    'street_1' : street_1,
                    'street_2' : street_2,
                    'city' : city,
                    'state' : state,
                    'country' : country,
                    'zip' : zip_num,
                    'full_address' : fll_addrs
                }),
                bank_info=json.dumps(bank_info),
                classification=clss.pk if clss else None,
                status=json.dumps(verification),
                created_by=request.user.id,
                updated_by=request.user.id
            )

            messages.success(request, f"Object with {name}, successfully created.")
            return redirect('supplier:vendor_list')
    
    return render(request, 'supplier_new/new_vendor.html', {
        'title' : "New Vendor",
        'page_name' : "New Vendor",
        'api' : "False",
        'data' : data
    })