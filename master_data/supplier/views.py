from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import *
import ast
from django.core.paginator import Paginator
from master_data.rules import *
from django.contrib import messages
from master.models import Pic, Classification
from itertools import zip_longest as zip_lo

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
        vendor.classification = Classification.objects.using('master').get(id=int(vendor.classification)) if vendor.classification else None
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
    classifications = Classification.objects.using('master').filter(is_active=True).all()

    data = [{
        'class' : classifications
    }]

    if request.method == 'POST' :
        metode = request.POST.get('metode', '')

        if metode == 'post' :
            name = request.POST.get('name', '')
            entity = request.POST.get('entity', '')
            classification = request.POST.get('clss', '')
            npwp = request.POST.get('npwp', '')
            pics = request.POST.getlist('pics[]', "")

            if not pics :
                messages.error(request, "PIC is required.")
                return redirect('supplier:vendor_new')
            
            objs = []
            for item in pics :
                data = json.loads(item)

                obj = Pic(
                    name = data.get('name', ''),
                    position = data.get('position', ''),
                    company = data.get('company', ''),
                    contact = json.dumps(data.get('contact', {})),
                    address = json.dumps(data.get('address', {})),
                    added = request.user.id,
                    updated = request.user.id
                )
                objs.append(obj)

            created_obj = Pic.objects.using('master').bulk_create(objs)

            pic_ids = [obj.pk for obj in created_obj]

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
            banks_addrs = request.POST.getlist('bank-add[]') or []

            bank_info = []
            for bank_name, acc_number, tlp_number, swft_code, bank_address in zip_lo(banks_name, accs_num, tlps_num, swts_code, banks_addrs, fillvalue=None) :
                bank_info.append({
                    'bank_name' : bank_name,
                    'account_number' : acc_number,
                    'bank_tlp_number' : tlp_number,
                    'swift_code' : swft_code,
                    'bank_address' : bank_address
                })

            verif = request.POST.getlist('verif[]', '')
            verif_status = request.POST.getlist('verif-sts[]', '')

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
                pic=json.dumps(pic_ids),
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

@login_required
@group_required('supplier')
def detail_vendor(request, vendor_id) :
    classifications = Classification.objects.using('master').filter(is_active=True).all()
    
    vendor = Vendor.objects.using('supplier').get(id=int(vendor_id))
    vendor.address = json.loads(vendor.address)
    vendor.pic = json.loads(vendor.pic)
    vendor.bank_info = json.loads(vendor.bank_info)
    vendor.status = json.loads(vendor.status)
    pics_qs = Pic.objects.using('master').filter(id__in=vendor.pic, is_active=True)

    pics_data = []
    for p in pics_qs:
        pics_data.append({
            "id": p.id,
            "name": p.name,
            "position": p.position,
            "company": p.company,
            "contact": json.loads(p.contact) if p.contact else {},
            "address": json.loads(p.address) if p.address else {},
            "added": p.added,
            "updated": p.updated,
            "is_active": p.is_active,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })

    data = [{
        'pics' : pics_data,
        'class' : classifications,
        'vendor' : vendor
    }]
    
    if request.method == 'POST':
        metode = request.POST.get('metode', '')

        if metode == 'post' :
            name = request.POST.get('name', '')
            entity = request.POST.get('entity', '')
            classification = request.POST.get('clss', '')
            npwp = request.POST.get('npwp', '')

            try :
                clss = Classification.objects.using('master').get(id=int(classification))
            except (ValueError, Classification.DoesNotExist) :
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
            banks_addrs = request.POST.getlist('bank-add[]') or []

            bank_info = []
            for bank_name, acc_number, tlp_number, swft_code, bank_address in zip_lo(banks_name, accs_num, tlps_num, swts_code, banks_addrs, fillvalue=None) :
                bank_info.append({
                    'bank_name' : bank_name,
                    'account_number' : acc_number,
                    'bank_tlp_number' : tlp_number,
                    'swift_code' : swft_code,
                    'bank_address' : bank_address
                })

            pics = request.POST.getlist('pics[]', "")

            if not pics :
                messages.error(request, "PIC is required.")
                return redirect('supplier:vendor_new')
            
            objs = []
            for g in pics:
                try:
                    id = g.get('id', None)
                except AttributeError:
                    id = None

                if id:
                    old_pic = Pic.object.using('master').get(id=int(id))
                    old.pic_name = g.get('name', old_pic.name)
                    old_pic.position = g.get('position', old_pic.position)
                    old_pic.company = g.get('company', old_pic.company)
                    old_pic.contact = json.dumps(g.get('contact', json.loads(old_pic.contact) if old_pic.contact else {}))
                    old_pic.address = json.dumps(g.get('address', json.loads(old_pic.address) if old_pic.address else {}))
                    old_pic.updated = request.user.id
                    old_pic.save()
                    objs.append(old_pic.pk)
                else:
                    try:
                        h = json.loads(g)
                    except (TypeError, json.JSONDecodeError):
                        h = ast.literal_eval(g)

                    obj = Pic(
                        name = h.get('name', ''),
                        position = h.get('position', ''),
                        company = h.get('company', ''),
                        contact = json.dumps(h.get('contact', {})),
                        address = json.dumps(h.get('address', {})),
                        added = request.user.id,
                        updated = request.user.id
                    )
                    obj.save()
                    objs.append(obj.pk)

            verif = request.POST.getlist('verif[]', '')
            verif_status = request.POST.getlist('verif-sts[]', '')

            verification = []
            for ver, ver_sts in zip(verif, verif_status) :

                verification.append({
                    'verification' : ver,
                    'verification_status' : ver_sts
                })

        vendor.pic = objs
        vendor.name = name
        vendor.npwp = npwp
        vendor.entity = entity
        vendor.bank_info = json.dumps(bank_info)
        vendor.address=json.dumps({
                    'street_1' : street_1,
                    'street_2' : street_2,
                    'city' : city,
                    'state' : state,
                    'country' : country,
                    'zip' : zip_num,
                    'full_address' : fll_addrs
                })
        vendor.classification = clss.pk if clss else None
        vendor.status = json.dumps(verification)
        vendor.created_by = request.user.id
        vendor.updated_by = request.user.id
        vendor.save()

        messages.success(request, f"Object with {name}, successfully created.")
        return redirect('supplier:vendor_list')

    return render(request, 'supplier_details/detail_vendor.html', {
        'title' : "Detail Vendor",
        'page_name' : "Detail Vendor",
        'api' : "False",
        'data' : data
    })