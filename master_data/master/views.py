from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from datetime import datetime
import json

@login_required(login_url='/login/')
def home(request) :

    return render(request, 'core/home.html', {
        'title' : 'Dashboard',
        'page_name' : 'Home'
    })

def login_view(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)

            if user is not None :
                auth.login(request, user)
                messages.success(request, f"Login Successfull, Welcome Back {user.username}...")
                next_url = request.POST.get('next') or request.GET.get('next') or '/master/'
                return redirect(next_url)
            
            else :
                messages.error(request, f"Invalid Login Credential With {username}, Please Check your username and password.")
                return redirect('master:login')
            
    return render(request, 'core/login.html', {
        'title' : 'Login'
    })

@login_required(login_url='/login/')
def logout(request) :
    auth.logout(request)
    messages.success(request, f"Logout Successfully. Have a Great Day {request.user.username}")
    return redirect('master:login')

@login_required(login_url='/login/')
def branch_list(request) :
    search_query = request.GET.get('search', '')

    branches = Branch.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        branches = [
            data for data in branches
            if (
                search_query.lower() in str(data.name).lower()
            )
        ]

    paginator = Paginator(branches, 12)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/branch_list.html', {
            'page_obj' : page_obj
        })
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    return render(request, 'master_pages/branch_list.html', {
        'title' : 'Branches',
        'page_name' : 'Branches',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_branch(request) :

    branches = Branch.objects.using('master').filter(is_active=True).all()

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['branch-name']
            street_1 = request.POST['street-1']
            street_2 = request.POST['street-2']
            state = request.POST['state']
            city = request.POST['city']
            country = request.POST['country']
            desc = request.POST['description']
            parent = request.POST['parent']

            address = {
                'street_1' : street_1,
                'street_2' : street_2,
                'state' : state,
                'city' : city,
                'country' : country
            }

            parent = Branch.objects.using('master').get(id=int(parent)) if parent else None

            new_branch = Branch.objects.using('master').create(
                name=name,
                address=json.dumps(address),
                parent=parent,
                description=desc
            )

            new_branch.save()

            return redirect('master:branch_list')
        
    return render(request, 'master_new/new_branch.html', {
        'title' : 'New Branch',
        'page_name' : 'New Branch',
        'branches' : branches
    })

@login_required(login_url='/login/')
def branch_detail(request, b_id) :
    branch = Branch.objects.using('master').get(id=int(b_id))
    branch.address = json.loads(branch.address)
    branches = Branch.objects.using('master').filter(is_active=True).exclude(pk=int(b_id)).all()

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['branch-name']
            street_1 = request.POST['street-1']
            street_2 = request.POST['street-2']
            state = request.POST['state']
            city = request.POST['city']
            country = request.POST['country']
            desc = request.POST['description']
            parent = request.POST['parent']


            address = {
                'street_1' : street_1,
                'street_2' : street_2,
                'state' : state,
                'city' : city,
                'country' : country
            }

            parent = Branch.objects.using('master').get(id=int(parent)) if parent else None

            branch.name = name
            branch.address = json.dumps(address)
            branch.description = desc
            branch.parent = parent

            branch.save()

            return redirect('master:branch_list')
        
        elif metode == 'delete' :
            branch.address = json.dumps(branch.address)
            branch.is_active = False
            
            branch.save()

            return redirect('master:branch_list')

    return render(request, 'master_detail/branch_detail.html', {
        'title' : 'Branch Detail',
        'page_name' : f'Branch - {branch.name}',
        'branch' : branch,
        'branches' : branches
    })

@login_required(login_url='/login/')
def entity_list(request) :
    search_query = request.GET.get('search', '')

    entity = Entity.objects.using('master').filter(is_active=True).all().order_by('id')

    data = []

    for d in entity :
        branch_data = []

        for r in json.loads(d.branches) :
            branch = Branch.objects.using('master').get(id=int(r['pk']))
            branch_data.append({
                'branch' : branch
            })
            
        data.append({
            'entity' : d,
            'branches' : branch_data[:3]
        })

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d['entity'].name).lower() or
                search_query.lower() in str(d['entity'].parent).lower() or
                search_query.lower() in str(d['entity'].established_date).lower()
            )
        ]
    
    paginator = Paginator(data, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/entity_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/entity_list.html', {
        'title' : 'Entity Data',
        'page_name' : 'Entities',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_entity(request) :
    branches = Branch.objects.using('master').filter(is_active=True).all()
    parents = Entity.objects.using('master').filter(is_active=True).all()

    if request.method == 'POST' :
        name = request.POST['entity-name']
        establish_date = request.POST['established-date']
        website = request.POST['website']
        description = request.POST['description']
        parent = request.POST['parent']
        street_1 = request.POST['street-1']
        street_2 = request.POST['street-2']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        branches_name = request.POST.getlist('branches-name')

        address = {
            'street_1' : street_1,
            'street_2' : street_2,
            'city' : city,
            'state' : state,
            'country' : country
        }

        parent = Entity.objects.using('master').get(id=int(parent)) if parent else None

        b_id = []

        for d in branches_name :
            branch_id = Branch.objects.using('master').get(id=int(d))
            b_id.append({
                'pk' : branch_id.pk,
                'name' : branch_id.name
            })

        new_entity = Entity.objects.using('master').create(
            name=name,
            established_date=establish_date,
            parent=parent,
            website=website,
            address=json.dumps(address),
            branches=json.dumps(b_id),
            description=description
        )

        new_entity.save()

        return redirect('master:entity_list')

    return render(request, 'master_new/entity_new.html', {
        'title' : 'New Entity',
        'page_name' : 'New Entity',
        'branches' : branches,
        'parents' : parents
    })

@login_required(login_url='/login/')
def detail_entity(request, e_id) :

    entity = Entity.objects.using('master').get(id=int(e_id))

    branches = Branch.objects.using('master').filter(is_active=True).all()
    parents = Entity.objects.using('master').filter(is_active=True).exclude(id=int(e_id)).all()

    branch = []

    for d in json.loads(entity.branches) :
        branch_i = Branch.objects.using('master').get(id=int(d['pk']))
        branch.append({
            'branch' : branch_i
        })

    entity.address = json.loads(entity.address)
    entity.established_date = datetime.strftime(entity.established_date, '%Y-%m-%d')

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['entity-name']
            establish_date = request.POST['established-date']
            website = request.POST['website']
            description = request.POST['description']
            parent = request.POST['parent']
            street_1 = request.POST['street-1']
            street_2 = request.POST['street-2']
            city = request.POST['city']
            state = request.POST['state']
            country = request.POST['country']
            branches_name = request.POST.getlist('branches-name')

            address = {
                'street_1' : street_1,
                'street_2' : street_2,
                'city' : city,
                'state' : state,
                'country' : country
            }

            parent = Entity.objects.using('master').get(id=int(parent)) if parent else None

            b_id = []

            for d in branches_name :
                branch_id = Branch.objects.using('master').get(id=int(d))
                b_id.append({
                    'pk' : branch_id.pk,
                    'name' : branch_id.name
                })
            
            entity.name = name
            entity.established_date = establish_date
            entity.website = website
            entity.description = description
            entity.address = json.dumps(address)
            entity.branches = json.dumps(b_id)
            entity.parent = parent

            entity.save()

            return redirect('master:entity_list')
        
        if metode == 'delete' :
            entity.address = json.dumps(entity.address)
            entity.is_active = False

            entity.save()

            return redirect('master:entity_list')
    
    return render(request, 'master_detail/entity_detail.html', {
        'title' : 'Entity Detail',
        'page_name' : f'Detail - {entity.name}',
        'entity' : entity,
        'branch' : branch,
        'branches' : branches,
        'parents' : parents
    })

@login_required(login_url='/login/')
def warehouse_list(request) :
    search_query = request.GET.get('search', '')

    warehouses = Warehouse.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        warehouses = [
            data for data in warehouses
            if (
                search_query.lower() in str(data.name).lower() or
                search_query.lower() in str(data.entity.name).lower() or
                search_query.lower() in str(data.branch.name).lower()
            )
        ]

    paginator = Paginator(warehouses, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/warehouse_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/warehouse_list.html', {
        'title' : 'Warehouse List',
        'page_name' : 'Warehouses',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_warehouse(request) :
    data = []

    branches = Branch.objects.using('master').filter(is_active=True).all()
    entities = Entity.objects.using('master').filter(is_active=True).all()

    data.append({
        'branches' : branches,
        'entities' : entities
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['warehouse-name']
            street_1 = request.POST['street-1']
            street_2 = request.POST['street-2']
            state = request.POST['state']
            city = request.POST['city']
            country  = request.POST['country']
            description = request.POST['description']
            entity = request.POST['entity']
            branch = request.POST['branch']

            entity_id = Entity.objects.using('master').get(id=int(entity))
            branch_id = Branch.objects.using('master').get(id=int(branch))

            address = {
                'street_1' : street_1,
                'street_2' : street_2,
                'state' : state,
                'city' : city,
                'country' : country
            }

            new_warehouse = Warehouse.objects.using('master').create(
                name=name,
                entity=entity_id,
                branch=branch_id,
                address=json.dumps(address),
                description=description
            )

            new_warehouse.save()

            return redirect('master:warehouse_list')
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        obj = []

        entity_obj_id = request.GET.get('entity_obj_id')
        entity_obj = Entity.objects.using('master').get(id=int(entity_obj_id))

        for d in json.loads(entity_obj.branches) :
            branch = Branch.objects.using('master').get(id=int(d['pk']))
            obj.append({
                'pk' : branch.pk,
                'branch' : branch.name
            })

        return JsonResponse(obj, safe=False)

    return render(request, 'master_new/new_warehouse.html', {
        'title' : 'New Warehouse',
        'page_name' : 'New Warehouse',
        'data' : data
    })

@login_required(login_url='/login/')
def detail_warehouse(request, w_id) :
    data = []
    warehouse = Warehouse.objects.using('master').get(id=int(w_id))
    warehouse.address = json.loads(warehouse.address)

    entities = Entity.objects.using('master').filter(is_active=True).all()

    data.append({
        'warehouse' : warehouse,
        'entities' : entities
    })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        metode = request.GET.get('metode')

        if metode == 'get_after' :

            obj = []

            entity_obj_id = request.GET.get('entity_obj_id')
            entity_obj = Entity.objects.using('master').get(id=int(entity_obj_id))

            for d in json.loads(entity_obj.branches) :
                branch = Branch.objects.using('master').get(id=int(d['pk']))
                obj.append({
                    'pk' : branch.pk,
                    'branch' : branch.name
                })

            return JsonResponse(obj, safe=False)

        elif metode == 'get_default' :
            dat = []
            entity_id = request.GET.get('selected_entity_id')
            entity = Entity.objects.using('master').get(id=int(entity_id))

            for d in json.loads(entity.branches) :
                branch = Branch.objects.using('master').get(id=int(d['pk']))
                dat.append({
                    'pk' : branch.pk,
                    'branch' : branch.name
                })

            return JsonResponse(dat, safe=False)
    
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['warehouse-name']
            street_1 = request.POST['street-1']
            street_2 = request.POST['street-2']
            state = request.POST['state']
            city = request.POST['city']
            country  = request.POST['country']
            description = request.POST['description']
            entity = request.POST['entity']
            branch = request.POST['branch']

            entity_id = Entity.objects.using('master').get(id=int(entity))
            branch_id = Branch.objects.using('master').get(id=int(branch))

            address = {
                'street_1' : street_1,
                'street_2' : street_2,
                'state' : state,
                'city' : city,
                'country' : country
            }

            warehouse.name = name
            warehouse.entity = entity_id
            warehouse.branch = branch_id
            warehouse.address = json.dumps(address)
            warehouse.description = description

            warehouse.save()

            return redirect('master:warehouse_list')
        
        elif metode == 'delete' :
            warehouse.address = json.dumps(warehouse.address)
            warehouse.is_active = False

            warehouse.save()

            return redirect('master:warehouse_list')

    return render(request, 'master_detail/warehouse_detail.html', {
        'title' : 'Detail Warehouse',
        'page_name' : f'Detail - {warehouse.name}',
        'data' : data
    })

@login_required(login_url='/login/')
def product_category_list(request) :
    search_query = request.GET.get('search', '')

    pc_list = ProductCategory.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        pc_list = [
            data for data in pc_list
            if (
                search_query.lower() in data.name.lower()
            )
        ]

    paginator = Paginator(pc_list, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/pc_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/pc_list.html', {
        'title' : 'Product Category List',
        'page_name' : 'Prod Cat List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_product_category(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['category-name']

            new_category = ProductCategory.objects.using('master').create(
                name=name
            )

            new_category.save()

            return redirect('master:product_c_list')

    return render(request, 'master_new/new_pc.html', {
        'title' : 'New Product Category',
        'page_name' : 'New Prod Cat'
    })

@login_required(login_url='/login/')
def detail_pc(request, pc_id) :
    pc = ProductCategory.objects.using('master').get(id=int(pc_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['category-name']

            pc.name = name

            pc.save()

            return redirect('master:product_c_list')
        
        elif metode == 'delete' :

            pc.is_active = False

            pc.save()

            return redirect('master:product_c_list')

    return render(request, 'master_detail/pc_detail.html', {
        'title' : 'Detail Product Category',
        'page_name' : f'Detail {pc.name}',
        'data' : pc
    })

@login_required(login_url='/login/')
def pcn_list(request) :
    search_query = request.GET.get('search', '')
    pcn_list = ProductCategorySales.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        pcn_list = [
            data for data in pcn_list
            if (
                search_query.lower() in pcn_list.name.lower()
            )
        ]

    paginator = Paginator(pcn_list, 12)\
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/pcn_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/pcn_list.html', {
        'title' : 'Product Category Sales List',
        'page_name' : 'Prod Cat Sales',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_pcn(request) :

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['category-name']
            short_name = request.POST['short-name']

            new_pcn = ProductCategorySales.objects.using('master').create(
                name=name,
                short_name=short_name
            )

            new_pcn.save()

            return redirect('master:pcn_list')

    return render(request, 'master_new/new_pcn.html', {
        'title' : 'New Product Category Sales',
        'page_name' : 'New Prod Cat Sales'
    })

@login_required(login_url='/login/')
def detail_pcn(request, pcn_id) :
    pcn = ProductCategorySales.objects.using('master').get(id=int(pcn_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['category-name']
            short_name = request.POST['short-name']

            pcn.name = name
            pcn.short_name = short_name

            pcn .save()

            return redirect('master:pcn_list')
        
        elif metode == 'delete' :
            pcn.is_active = False

            pcn.save()

            return redirect('master:pcn_list')

    return render(request, 'master_detail/pcn_detail.html', {
        'title' : 'Product Category Sales Detail',
        'page_name' : f'Detail - {pcn.short_name}',
        'pcn' : pcn
    })

@login_required(login_url='/login/')
def department_list(request) :
    search_query = request.GET.get('search', '')

    data = []
    
    deps = Department.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in deps :
        entity = Entity.objects.using('master').get(id=int(d.entity)).name

        words = entity.split()

        if len(words) == 1 :
            d.entity = d.entity
        else :
            d.entity = ''.join([w[0] for w in words[:3]])

        data.append({
            'department' : d
        })

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d['department'].short_name).lower() or
                search_query.lower() in str(d['department'].entity).lower() or
                search_query.lower() in str(d['department'].name).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/department_list.html', {
            'page_obj' : page_obj
        })
    
    return render(request, 'master_pages/department_list.html', {
        'title' : 'Department List',
        'page_name' : 'Department List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_department(request) :
    data = []

    entities = Entity.objects.using('master').filter(is_active=True).all()
    deps = Department.objects.using('master').filter(is_active=True).all()

    data.append({
        'entities' : entities,
        'parent' : deps
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['department-name']
            short_name = request.POST['short-name']
            desc = request.POST['description']
            ent_id = request.POST['entity']
            parent = request.POST['parent']

            ent = Entity.objects.using('master').get(id=int(ent_id))

            prt = Department.objects.using('master').get(id=int(parent)) if parent else None

            new_dep = Department.objects.using('master').create(
                name=name,
                short_name=short_name,
                parent=prt,
                entity=ent.pk,
                description=desc
            )
            
            new_dep.save()

            return redirect('master:department_list')

    return render(request, 'master_new/new_department.html', {
        'title' : 'New Department',
        'page_name' : 'New Department',
        'data' : data
    })

@login_required(login_url='/login/')
def detail_department(request, d_id) :
    data = []

    entities = Entity.objects.using('master').filter(is_active=True).all()
    parents = Department.objects.using('master').filter(is_active=True).exclude(id=int(d_id)).all()

    data.append({
        'entities' : entities,
        'parents' : parents
    })

    department = Department.objects.using('master').get(id=int(d_id))
    department.entity = Entity.objects.using('master').get(id=int(department.entity))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['department-name']
            short_name = request.POST['short-name']
            desc = request.POST['description']
            ent_id = request.POST['entity']
            parent = request.POST['parent']

            ent = Entity.objects.using('master').get(id=int(ent_id))

            prt = Department.objects.using('master').get(id=int(parent)) if parent else None
            
            department.name = name
            department.short_name = short_name
            department.description = desc
            department.entity = ent.pk
            department.parent = prt

            department.save()

            return redirect('master:department_list')
        
        elif metode == 'delete' :
            department.entity = department.entity.pk
            department.is_active = False

            department.save()

            return redirect('master:department_list')


    return render(request, 'master_detail/department_detail.html', {
        'title' : 'Department Detail',
        'page_name' : f'Detail - {department.short_name}',
        'department' : department,
        'data' : data
    })

@login_required(login_url='/login/')
def product_list(request) :
    search_query = request.GET.get('search', '')

    data = []

    products = Product.objects.using('master').filter(is_active=True).all()

    for d in products :
        d.department = Department.objects.using('master').get(id=int(d.department))

        words = d.entity.name.split()

        if len(words) == 1 :
            d.entity.name = d.entity.name
        else :
            d.entity.name = ''.join([w[0] for w in words[:3]])

        data.append({
            'product' : d
        })

    if search_query :
        data = [
            p for p in data
            if (
                search_query.lower() in str(p['product'].entity.name).lower() or
                search_query.lower() in str(p['product'].category.name).lower() or
                search_query.lower() in str(p['product'].category_sales.name).lower() or
                search_query.lower() in str(p['product'].name).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/product_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/product_list.html', {
        'title' : 'Product List',
        'page_name' : 'Product List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_product(request) :
    data = []

    cat_dist = ProductCategory.objects.using('master').filter(is_active=True).all()
    cat_sales = ProductCategorySales.objects.using('master').filter(is_active=True).all()
    dep = Department.objects.using('master').filter(is_active=True).all()
    ent = Entity.objects.using('master').filter(is_active=True).all()

    data.append({
        'cat_dist' : cat_dist,
        'cat_sales' : cat_sales,
        'dep' : dep,
        'ent' : ent
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['product-name']
            cat_dst = request.POST['category']
            cat_sls = request.POST['category-sales']
            description = request.POST['description']
            entity_id = request.POST['entity']
            dep_id = request.POST['department']
            code_accurate = request.POST['accurate']
            prc = request.POST['price']
            cst = request.POST['cost']

            dst = ProductCategory.objects.using('master').get(id=int(cat_dst))
            sls = ProductCategorySales.objects.using('master').get(id=int(cat_sls))

            entity = Entity.objects.using('master').get(id=int(entity_id))
            dept = Department.objects.using('master').get(id=int(dep_id))

            ents = entity.name.split()

            if len(ents) == 1 :
                ent_c = ents
            else :
                ent_c = ''.join([w[0] for w in ents[:3]])

            year_now = datetime.now().strftime('%Y')

            la_p = Product.objects.using('master').filter(
                entity=entity.pk,
                department=dept.pk
            ).count()

            if la_p == 0 :
                la_p = 1

            new_code = f"{ent_c}-{dept.short_name}-{dst.pk}-{sls.pk}-{year_now}-{la_p:03d}"

            while Product.objects.using('master').filter(sku=new_code).exists() :
                la_p += 1
                new_code = f"{ent_c}-{year_now}-{dst.pk}-{sls.pk}-{year_now}-{la_p:03d}"

            new_product = Product.objects.using('master').create(
                sku=new_code,
                code_accurate=code_accurate,
                name=name,
                category=dst,
                category_sales=sls,
                entity=entity,
                department=dept.pk,
                price=int(prc),
                cost=int(cst),
                description=description
            )

            new_product.save()

            return redirect('master:product_list')

    return render(request, 'master_new/new_product.html', {
        'title' : 'New Product',
        'page_name' : 'New Product',
        'data' : data
    })

@login_required(login_url='/login/')
def detail_product(request, p_id) :
    data = []

    product = Product.objects.using('master').get(id=int(p_id))
    cat_dist = ProductCategory.objects.using('master').filter(is_active=True).all()
    cat_sales = ProductCategorySales.objects.using('master').filter(is_active=True).all()
    dep = Department.objects.using('master').filter(is_active=True).all()
    ent = Entity.objects.using('master').filter(is_active=True).all()

    data.append({
        'cat_dist' : cat_dist,
        'cat_sales' : cat_sales,
        'dep' : dep,
        'ent' : ent,
        'product' : product
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['product-name']
            cat_dst = request.POST['category']
            cat_sls = request.POST['category-sales']
            description = request.POST['description']
            entity_id = request.POST['entity']
            dep_id = request.POST['department']
            code_accurate = request.POST['accurate']
            prc = request.POST['price']
            cst = request.POST['cost']

            dst = ProductCategory.objects.using('master').get(id=int(cat_dst))
            sls = ProductCategorySales.objects.using('master').get(id=int(cat_sls))

            entity = Entity.objects.using('master').get(id=int(entity_id))
            dept = Department.objects.using('master').get(id=int(dep_id))

            product.name = name
            product.category = dst
            product.category_sales = sls
            product.code_accurate = code_accurate
            product.entity = entity
            product.department = dept.pk
            product.description = description
            product.price = int(prc)
            product.cost = int(cst)

            product.save()

            return redirect('master:product_list')
        
        elif metode == 'delete' :
            product.is_active=False

            product.save()

            return redirect('master:product_list')

    return render(request, 'master_detail/product_detail.html', {
        'title' : 'Detail Product',
        'page_name' : f'Detail - {product.sku}',
        'data' : data
    })

@login_required(login_url='/login/')
def batch_list(request) :
    search_query = request.GET.get('search', '')
    data = []

    batches = Batch.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in batches :
        data.append({
            'batch' : d
        })

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d['batch'].product.name).lower() or
                search_query.lower() in str(d['batch'].batch).lower() or
                search_query.lower() in str(d['batch'].exp_date).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/batch_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/batch_list.html', {
        'title' : 'Batch List',
        'page_name' : 'Batch List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_batch(request) :
    data = []

    products = Product.objects.using('master').filter(is_active=True).all()

    data.append({
        'products' : products
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            code = request.POST['batch-code']
            p_id = request.POST['product']
            exp = request.POST['exp-date']
            desc = request.POST['desc']

            product = Product.objects.using('master').get(id=int(p_id))

            new_code = Batch.objects.using('master').create(
                batch=code,
                exp_date = exp,
                product=product,
                description=desc
            )

            new_code.save()

            return redirect('master:batch_list')

    return render(request, 'master_new/new_batch.html', {
        'title' : 'New Batch',
        'page_name' : 'New Batch',
        'data' : data
    })

@login_required(login_url='/login/')
def detail_batch(request, bat_id) :
    data = []

    batch = Batch.objects.using('master').get(id=int(bat_id))
    batch.exp_date = batch.exp_date.strftime('%Y-%m-%d')
    products = Product.objects.using('master').filter(is_active=True).all()

    data.append({
        'batch' : batch,
        'products' : products
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            code = request.POST['batch-code']
            p_id = request.POST['product']
            exp = request.POST['exp-date']
            desc = request.POST['desc']

            product = Product.objects.using('master').get(id=int(p_id))

            batch.exp_date = exp
            batch.batch = code
            batch.product = product
            batch.description = desc

            batch.save()

            return redirect('master:batch_list')
        
        elif metode == 'delete' :
            batch.is_active = False

            batch.save()

            return redirect('master:batch_list')

    return render(request, 'master_detail/batch_detail.html', {
        'title' : 'Detail Batch',
        'page_name' : f'Detail - {batch.batch}',
        'data' : data
    })

@login_required(login_url='/login/')
def job_position_list(request) :
    search_query = request.GET.get('search', '')

    data = JobPosition.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d.name).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/jb_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/jb_list.html', {
        'title' : 'Job Position List',
        'page_name' : 'Job Position',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_job_position(request) :
    data = []

    departments = Department.objects.using('master').filter(is_active=True).all()

    data.append({
        'departments' : departments
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['job-position']
            desc = request.POST['desc']

            new_jb = JobPosition.objects.using('master').create(
                name=name,
                description=desc
            )

            new_jb.save()

            return redirect('master:jb_list')

    return render(request, 'master_new/new_jb.html', {
        'title' : 'New Job Position',
        'page_name' : 'New Job Position',
        'data' : data
    })

@login_required(login_url='/login/')
def detail_job_position(request, jb_id) :

    jb = JobPosition.objects.using('master').get(id=int(jb_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['job-position']
            desc = request.POST['desc']

            jb.name = name
            jb.description = desc

            jb.save()

            return redirect('master:jb_list')
        
        elif metode == 'delete' :
            jb.is_active = False

            jb.save()

            return redirect('master:jb_list')

    return render(request, 'master_detail/jb_detail.html', {
        'title' : 'Detail Job Position',
        'page_name' : f'Detail - {jb.name}',
        'data' : jb
    })

@login_required(login_url='/login/')
def shift(request) :
    search_query = request.GET.get('search', '')

    shifts = ShiftSchedule.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        shifts = [
            data for data in shifts
            if (
                search_query.lower() in str(data.shift).lower()
            )
        ]

    paginator = Paginator(shifts, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/shift_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/shift_list.html', {
        'title' : 'Shift',
        'page_name' : 'Shift List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_shift(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['job-position']
            start_time = request.POST['start-time']
            end_time = request.POST['end-time']
            desc = request.POST['desc']

            new_shift = ShiftSchedule.objects.using('master').create(
                shift=name,
                start_time=start_time,
                end_time=end_time,
                description=desc
            )

            new_shift.save()

            return redirect('master:shift_list')

    return render(request, 'master_new/new_shift.html', {
        'title' : 'New Shift',
        'page_name' : 'New Shift'
    })

@login_required(login_url='/login/')
def detail_shift(request, sh_id) :

    shift = ShiftSchedule.objects.using('master').get(id=int(sh_id))
    shift.start_time = shift.start_time.strftime('%H:%M')
    shift.end_time = shift.end_time.strftime('%H:%M')

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['job-position']
            start_time = request.POST['start-time']
            end_time = request.POST['end-time']
            desc = request.POST['desc']

            shift.shift = name
            shift.start_time = start_time
            shift.end_time = end_time
            shift.description = desc

            shift.save()

            return redirect('master:shift_list')
        
        elif metode == 'delete' :
            
            shift.is_active = False

            shift.save()

            return redirect('master:shift_list')

    return render(request, 'master_detail/shift_detail.html', {
        'title' : 'Shift Detail',
        'page_name' : f'Detail - Shift {shift.shift}',
        'data' : shift
    })

@login_required(login_url='/login/')
def timeoff_list(request) :
    search_query = request.GET.get('search', '')

    timeoffs = []

    timeoff = TimeOffType.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in timeoff :
        if d.is_absent == False :
            d.is_absent = "Dihitung Masuk"
        else :
            d.is_absent = "Tidak Dihitung Masuk"

        timeoffs.append({
            'timeoff' : d
        })
        

    if search_query :
        timeoffs = [
            data for data in timeoffs
            if (
                search_query.lower() in str(data['timeoff'].name).lower() or
                search_query.lower() in str(data['timeoff'].is_absent).lower()
            )
        ]

    paginator = Paginator(timeoffs, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/timeoff_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/timeoff_list.html', {
        'title' : 'Time Off',
        'page_name' : 'Time Off',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_timeoff(request) :

    if request.method == 'POST' :
        name = request.POST['timeoff']
        attendance = request.POST['attendance']

        if int(attendance) == 0 :
            att = True
        else :
            att = False

        new_timeoff = TimeOffType.objects.using('master').create(
            name=name,
            is_absent=att
        )

        new_timeoff.save()

        return redirect('master:timeoff_list')

    return render(request, 'master_new/new_timeoff.html', {
        'title' : 'New Time Off',
        'page_name' : 'New Time Off'
    })

@login_required(login_url='/login/')
def detail_timeoff(request, to_id) :

    timeoff = TimeOffType.objects.using('master').get(id=int(to_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['timeoff']
            attendance = request.POST['attendance']

            if int(attendance) == 0 :
                att = True
            else :
                att = False

            timeoff.name = name
            timeoff.is_absent = att

            timeoff.save()

            return redirect('master:timeoff_list')
        
        elif metode == 'delete' :
            timeoff.is_active = False

            timeoff.save()

            return redirect('master:timeoff_list')

    return render(request, 'master_detail/timeoff_detail.html', {
        'title' : 'Time Off',
        'page_name' : f'Time Off - {timeoff.name}',
        'data' : timeoff
    })

@login_required(login_url='/login/')
def disciplinary(request) :
    search_query = request.GET.get('search', '')

    data = []

    discs = DisciplinaryAction.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in discs :

        if d.duration_measure == "D" :
            d.duration_measure = "Days"
        elif d.duration_measure == "M" :
            d.duration_measure = "Months"
        elif d.duration_measure == "Y" :
            d.duration_measure = "Years"

        data.append({
            'disciplinary' : d
        })

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d['disciplinary'].name).lower() or
                search_query.lower() in str(d['disciplinary'].duration_measure).lower() or
                search_query.lower() in str(d['disciplinary'].duration).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/disc_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/disc_list.html', {
        'title' : 'Disciplinary List',
        'page_name' : 'Disciplinary Type List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_disciplinary(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['disciplinary-name']
            duraton = request.POST['duration']
            measure = request.POST['measure']

            new_disc = DisciplinaryAction.objects.using('master').create(
                name=name,
                duration=int(duraton),
                duration_measure=measure
            )

            new_disc.save()

            return redirect('master:disc_list')

    return render(request, 'master_new/new_disc.html', {
        'title' : 'New Disciplinary',
        'page_name' : 'New Disciplinary Type'
    })

@login_required(login_url='/login/')
def detail_disc(request, disc_id) :
    disc = DisciplinaryAction.objects.using('master').get(id=int(disc_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['disciplinary-name']
            duraton = request.POST['duration']
            measure = request.POST['measure']

            disc.name = name
            disc.duration = duraton
            disc.duration_measure = measure

            disc.save()

            return redirect('master:disc_list')
        
        elif metode == 'delete' :
            disc.is_active = False

            disc.save()

            return redirect('master:disc_list')

    return render(request, 'master_detail/disc_detail.html', {
        'title' : 'Detail Disciplinary Action',
        'page_name' : f'Detail - {disc.name}',
        'data' : disc
    })

@login_required(login_url='/login/')
def deduction_list(request) :
    search_query = request.GET.get('page')

    deducs = DeductionType.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        deducs = [
            data for data in deducs
            if (
                search_query.lower() in str(data.name).lower()
            )
        ]

    paginator = Paginator(deducs, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/deduction_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/deduction_list.html', {
        'title' : 'Deduction List',
        'page_name' : 'Deduction Type List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_deduction(request) :

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['deduction-name']

            new_ded = DeductionType.objects.using('master').create(
                name=name
            )

            new_ded.save()

            return redirect('master:deduc_list')

    return render(request, 'master_new/new_deduction.html', {
        'title' : 'New Deduction Type',
        'page_name' : 'New Deduction Type'
    })

@login_required(login_url='/login/')
def detail_deduction(request, ded_id) :
    deduction = DeductionType.objects.using('master').get(id=int(ded_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['deduction-name']

            deduction.name = name

            deduction.save()

            return redirect('master:deduc_list')
        
        elif metode == 'delete' :
            deduction.is_active = False

            deduction.save()

            return redirect('master:deduc_list')

    return render(request, 'master_detail/deduction_detail.html', {
        'title' : 'Detail Deduction',
        'page_name' : f'Detail',
        'data' : deduction
    })

@login_required(login_url='/login/')
def work_locations(request) :
    search_query = request.GET.get('search', '')

    wls = WorkLocation.objects.using('master').filter(is_active=True).all().order_by('id')

    if search_query :
        wls = [
            data for data in wls
            if (
                search_query.lower() in str(data.name).lower()
            )
        ]

    paginator = Paginator(wls, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'master_pages/work_location_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'master_pages/work_location_list.html', {
        'title' : 'Work Location List',
        'page_name' : 'Work Location List',
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_work_location(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['location-name']
            street_1 = request.POST['street-1']
            street_2 = request.POST['street-2']
            state = request.POST['state']
            city = request.POST['city']
            country = request.POST['country']

            address = {
                'street_1' : street_1,
                'street_2' : street_2,
                'state' : state,
                'city' : city,
                'country' : country
            }

            new_wl = WorkLocation.objects.using('master').create(
                name=name,
                address=json.dumps(address)
            )

            new_wl.save()

            return redirect('master:work_location_list')

    return render(request, 'master_new/new_work_location.html', {
        'title' : 'New Work Location',
        'page_name' : 'New Work Location'
    })

@login_required(login_url='/login/')
def detail_work_location(request, dwk_id) :

    wl = WorkLocation.objects.using('master').get(id=int(dwk_id))
    wl.address = json.loads(wl.address)

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['location-name']
            street_1 = request.POST['street-1']
            street_2 = request.POST['street-2']
            state = request.POST['state']
            city = request.POST['city']
            country = request.POST['country']

            address_1 = {
                'street_1' : street_1,
                'street_2' : street_2,
                'state' : state,
                'city' : city,
                'country' : country
            }

            wl.name = name
            wl.address = json.dumps(address_1)

            wl.save()

            return redirect('master:work_location_list')
        
        if metode == 'delete' :
            wl.address = json.dumps(wl.address)
            wl.is_active = False

            wl.save()

            return redirect('master:work_location_list')

    return render(request, 'master_detail/detail_work_location.html', {
        'title' : 'Detail Work Location',
        'page_name' : f'Detail - {wl.name}',
        'data' : wl
    })

@login_required(login_url='/login/')
def gc_list(request) :
    search_query = request.GET.get('search', '')

    data = []

    grades = ClinicGrade.objects.using('master').filter(is_active=True).all().order_by('id')
    
    for d in grades :
        d.description = json.loads(d.description)
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
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_gc(request) :
    
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['name']
            alias = request.POST['alias']
            min_v = request.POST['min']
            max_v = request.POST['max']
            desc = request.POST['desc']

            range = {
                'min' : int(min_v),
                'max' : int(max_v)
            }

            descrip = {
                'alias' : alias,
                'description' : desc
            }

            new_clinic = ClinicGrade.objects.using('master').create(
                name=name,
                range_clinic=json.dumps(range),
                description = json.dumps(descrip)
            )

            new_clinic.save()

            return redirect('master:gc_list')

    return render(request, 'master_new/new_gc.html', {
        'title' : 'New Grade Clinic',
        'page_name' : 'New Grade Clinic'
    })

@login_required(login_url='/login/')
def detail_gc(request, gc_id) :

    grade = ClinicGrade.objects.using('master').get(id=int(gc_id))
    grade.range_clinic = json.loads(grade.range_clinic)
    grade.description = json.loads(grade.description)

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['name']
            alias = request.POST['alias']
            min_v = request.POST['min']
            max_v = request.POST['max']
            desc = request.POST['desc']

            range = {
                'min' : int(min_v),
                'max' : int(max_v)
            }

            descrip = {
                'alias' : alias,
                'description' : desc
            }

            grade.name = name
            grade.range_clinic = json.dumps(range)
            grade.description = json.dumps(descrip)

            grade.save()

            return redirect('master:gc_list')
        
        elif metode == 'delete' :
            grade.range_clinic = json.dumps(grade.range_clinic)
            grade.description = json.dumps(grade.description)
            grade.is_active = False
            
            grade.save()

            return redirect('master:gc_list')

    return render(request, 'master_detail/gc_detail.html', {
        'title' : 'Grade Clinic Detail',
        'page_name' : f'Detail Clinic Grade - {grade.description.get('alias')}',
        'data' : grade
    })

def convert(value) :
    if value == "M" :
        measure = "Juta"
    elif value == "B" :
        measure = "Milyar"
    elif  value == "T" :
        measure = "Ribu"
    
    return measure

@login_required(login_url='/login/')
def gu_list(request) :
    search_query = request.GET.get('search', '')

    data = []

    gus = UserGrade.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in gus :
        d.description = json.loads(d.description)
        d.range_user = json.loads(d.range_user)
        measure_max = convert(d.range_user.get('max').get('measure'))
        measure_min = convert(d.range_user.get('min').get('measure'))

        data.append({
            'user' : d,
            'measure' : {
                'max' : measure_max,
                'min' : measure_min
            }
        })

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
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_gu(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['name']
            alias = request.POST['alias']
            min_v = request.POST['min']
            max_v = request.POST['max']
            desc = request.POST['desc']
            min_m = request.POST['min-measure']
            max_m = request.POST['max-measure']

            range = {
                'min' : {
                    'value' : int(min_v),
                    'measure' : min_m
                },
                'max' : {
                    'value' : int(max_v),
                    'measure' : max_m
                }
            }

            descp = {
                'alias' : alias,
                'description' : desc
            }

            gu_new = UserGrade.objects.using('master').create(
                name=name,
                range_user=json.dumps(range),
                description=json.dumps(descp)
            )

            gu_new.save()

            return redirect('master:gu_list')

    return render(request, 'master_new/new_gu.html', {
        'title' : 'New Grade User',
        'page_name' : 'New Grade User'
    })

@login_required(login_url='/login/')
def detail_gu(request, gu_id) :
    gu = UserGrade.objects.using('master').get(id=int(gu_id))
    gu.description = json.loads(gu.description)
    gu.range_user = json.loads(gu.range_user)

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['name']
            alias = request.POST['alias']
            min_v = request.POST['min']
            max_v = request.POST['max']
            desc = request.POST['desc']
            min_m = request.POST['min-measure']
            max_m = request.POST['max-measure']

            range = {
                'min' : {
                    'value' : int(min_v),
                    'measure' : min_m
                },
                'max' : {
                    'value' : int(max_v),
                    'measure' : max_m
                }
            }

            descp = {
                'alias' : alias,
                'description' : desc
            }

            gu.name=name
            gu.range_user=json.dumps(range)
            gu.description=json.dumps(descp)

            gu.save()

            return redirect('master:gu_list')
        
        elif metode == 'delete' :
            gu.range_user = json.dumps(gu.range_user)
            gu.description = json.dumps(gu.description)
            gu.is_active = False

            gu.save()

            return redirect('master:gu_list')

    return render(request, 'master_detail/gu_detail.html', {
        'title' : 'Detail Grade User',
        'page_name' : f'Detail User Grade - {gu.name}',
        'data' : gu
    })

@login_required(login_url='/login/')
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
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_title(request) :

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            short_name = request.POST['short']
            full_name = request.POST['full']
            desc = request.POST['desc']

            if Title.objects.using('master').filter(name=full_name).exists() or Title.objects.using('master').filter(short_name=short_name).exists() :
                return redirect('master:new_title')
            
            else :

                new_title = Title.objects.using('master').create(
                    name=full_name,
                    short_name=short_name,
                    description=desc
                )

                new_title.save()

                return redirect('master:title_list')
        
    return render(request, 'master_new/new_title.html', {
        'title' : 'New Title',
        'page_name' : 'New Title'
    })

@login_required(login_url='/login/')
def detail_title(request, title_id) :
    title = Title.objects.using('master').get(id=int(title_id))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            short_name = request.POST['short']
            full_name = request.POST['full']
            desc = request.POST['desc']

            if Title.objects.using('master').filter(name=full_name).exclude(id=int(title_id)).exists() or Title.objects.using('master').filter(short_name=short_name).exclude(id=int(title_id)).exists() :
                return redirect('master:detail_title', title_id=title.pk)
            
            else :
                title.name = full_name
                title.short_name = short_name
                title.description = desc

                title.save()

                return redirect('master:title_list')
        
        elif metode == 'delete' :
            title.is_active = False

            title.save()

            return redirect('master:title_list')

    return render(request, 'master_detail/title_detail.html', {
        'title' : 'Detail Title',
        'page_name' : f'Detail - {title.short_name}',
        'data' : title
    })

@login_required(login_url='/login/')
def salutation_list(request) :
    search_query = request.GET.get('search', '')

    data = []

    salutations = Salutation.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in salutations :
        d.description = json.loads(d.description)

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
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_salutation(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            full_name = request.POST['full']
            short_name = request.POST['short']
            desc = request.POST['desc']

            descr = {
                'short_name' : short_name,
                'description' : desc
            }

            if Salutation.objects.using('master').filter(salutation=short_name).exists() :
                return redirect('master:new_salutation')
            
            else :
                new_salutation = Salutation.objects.using('master').create(
                    salutation=full_name,
                    description=json.dumps(descr)
                )

                new_salutation.save()

                return redirect('master:salutation_list')
            
    return render(request, 'master_new/new_salutation.html', {
        'title' : 'New Salutation',
        'page_name' : 'New Salutation'
    })

@login_required(login_url='/login/')
def detail_salutation(request, sal_id) :

    salutation = Salutation.objects.using('master').get(id=int(sal_id))
    salutation.description = json.loads(salutation.description)

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            full_name = request.POST['full']
            short_name = request.POST['short']
            desc = request.POST['desc']

            descr = {
                'short_name' : short_name,
                'description' : desc
            }

            if Salutation.objects.using('master').filter(salutation=short_name).exclude(id=int(sal_id)).exists() :
                return redirect('master:new_salutation')
            
            else :
                salutation.salutation = full_name
                salutation.description = json.dumps(descr)

                salutation.save()

                return redirect('master:salutation_list')
            
        elif metode == 'delete' :
            salutation.description = json.dumps(salutation.description)
            salutation.is_active = False

            salutation.save()

            return redirect('master:salutation_list')

    return render(request, 'master_detail/salutation_detail.html', {
        'title' : 'Detail Salutation',
        'page_name' : f'Detail - {salutation.description.get('short_name')}',
        'data' : salutation
    })

@login_required(login_url='/login/')
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
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_specialist(request) :
    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            full_name = request.POST['full']
            short_name = request.POST['short']
            desc = request.POST['desc']

            if Specialist.objects.using('master').filter(short_name=short_name).exists() or Specialist.objects.using('master').filter(full=full_name).exists() :
                return redirect('master:new_specialist')
            
            else :
                new_specialist = Specialist.objects.using('master').create(
                    full=full_name,
                    short_name=short_name,
                    description=desc
                )

                new_specialist.save()

                return redirect('master:specialists')
            
    return render(request, 'master_new/new_specialist.html', {
        'title' : 'New Specialist',
        'page_name' : 'New Specialist'
    })

@login_required(login_url='/login/')
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
        'page_name' : f'Detail - {specialist.short_name}',
        'data' : specialist
    })