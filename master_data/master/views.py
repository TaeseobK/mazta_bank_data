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
        'title' : 'Dashboard'
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
                next_url = request.POST.get('next') or request.GET.get('next') or '/'
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
        'page_obj' : page_obj
    })

@login_required(login_url='/login/')
def new_branch(request) :

    branches = Branch.objects.using('master').filter(sub_branch=False, is_active=True).all()

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

            if parent == None or parent == '' or parent == "" :
                parent = 0
                sub_branch = False

            else :
                parent = Branch.objects.using('master').get(id=int(parent)).pk
                sub_branch = True

            new_branch = Branch.objects.using('master').create(
                name=name,
                address=json.dumps(address),
                parent=parent,
                sub_branch=sub_branch,
                description=desc
            )

            new_branch.save()

            return redirect('master:branch_list')
        
    return render(request, 'master_new/new_branch.html', {
        'title' : 'New Branch',
        'branches' : branches
    })

@login_required(login_url='/login/')
def branch_detail(request, b_id) :
    branch = Branch.objects.using('master').get(id=int(b_id))
    branch.address = json.loads(branch.address)
    branches = Branch.objects.using('master').filter(is_active=True, sub_branch=False).exclude(pk=int(b_id)).all()

    if branch.sub_branch == True :
        branch.parent = Branch.objects.using('master').get(id=int(branch.parent)).pk
    
    else :
        branch.parent = branch.parent

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

            if parent == None or parent == '' or parent == "" :
                parent = 0
                sub_branch = False

            else :
                parent = Branch.objects.using('master').get(id=int(parent))
                sub_branch = True

            branch.name = name
            branch.address = json.dumps(address)
            branch.description = desc
            branch.parent = parent
            branch.sub_branch = sub_branch

            branch.save()

            return redirect('master:branch_list')
        
        elif metode == 'delete' :
            branch.address = json.dumps(branch.address)
            branch.is_active = False
            
            branch.save()

            return redirect('master:branch_list')

    return render(request, 'master_detail/branch_detail.html', {
        'title' : 'Branch Detail',
        'branch' : branch,
        'branches' : branches
    })

@login_required(login_url='/login/')
def entity_list(request) :
    search_query = request.GET.get('search', '')

    entity = Entity.objects.using('master').filter(is_active=True).all().order_by('id')

    data = []

    for d in entity :
        
        if d.sub_entity == True :
            d.parent = Entity.objects.using('master').get(id=int(d.parent))
        
        else :
            d.parent = d.parent

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

        if parent == None or parent == '' :
            parent = 0
            sub_entity = False

        else :
            parent = Entity.objects.using('master').get(id=int(parent)).pk
            sub_entity = True

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
            sub_entity=sub_entity,
            branches=json.dumps(b_id),
            description=description
        )

        new_entity.save()

        return redirect('master:entity_list')

    return render(request, 'master_new/entity_new.html', {
        'title' : 'New Entity',
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

            if parent == None or parent == '' :
                parent = 0
                sub_entity = False

            else :
                parent = Entity.objects.using('master').get(id=int(parent)).pk
                sub_entity = True

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
            entity.sub_entity = sub_entity
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
        'title' : 'New Product Category'
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
        'title' : 'New Product Category Sales'
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
        'pcn' : pcn
    })

@login_required(login_url='/login/')
def department_list(request) :
    search_query = request.GET.get('search', '')

    data = []
    
    deps = Department.objects.using('master').filter(is_active=True).all().order_by('id')

    for d in deps :
        if d.is_sub_department :
            d.parent = Department.objects.using('master').get(id=int(d.parent))
        else :
            d.parent = d.parent
        
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

            if parent == '' or parent == None :
                prt = 0
                sub_department = False
            
            else :
                prt = Department.objects.using('master').get(id=int(parent)).pk
                sub_department = True

            new_dep = Department.objects.using('master').create(
                name=name,
                short_name=short_name,
                is_sub_department=sub_department,
                parent=prt,
                entity=ent.pk,
                description=desc
            )
            
            new_dep.save()

            return redirect('master:department_list')

    return render(request, 'master_new/new_department.html', {
        'title' : 'New Department',
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
    
    if department.is_sub_department :
        department.parent = Department.objects.using('master').get(id=int(department.parent))
    else :
        department.parent = department.parent

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            name = request.POST['department-name']
            short_name = request.POST['short-name']
            desc = request.POST['description']
            ent_id = request.POST['entity']
            parent = request.POST['parent']

            ent = Entity.objects.using('master').get(id=int(ent_id))

            if parent == '' or parent == None :
                prt = 0
                sub_department = False
            
            else :
                prt = Department.objects.using('master').get(id=int(parent)).pk
                sub_department = True
            
            department.name = name
            department.short_name = short_name
            department.description = desc
            department.entity = ent.pk
            department.parent = prt
            department.is_sub_department = sub_department

            department.save()

            return redirect('master:department_list')
        
        elif metode == 'delete' :
            ent_id = Entity.objects.using('master').get(id=int(department.entity.pk)).pk

            if department.is_sub_department == False :
                prt = 0
                sub_department = False
            
            else :
                prt = Department.objects.using('master').get(id=int(parent)).pk
                sub_department = True

            department.entity = ent_id
            department.parent = prt
            department.is_sub_department = sub_department
            department.is_active = False

            department.save()

            return redirect('master:department_list')


    return render(request, 'master_detail/department_detail.html', {
        'title' : 'Department Detail',
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
        'data' : data
    })