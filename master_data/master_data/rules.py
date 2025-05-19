from django.contrib import messages
from functools import wraps
from django.shortcuts import redirect

def group_required(*group_names) :
    def decorator(view_func) :
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs) :
            user = request.user
            if (
                    user.is_authenticated and 
                    user.groups.filter(name__in=group_names).exists()
                ) or user.is_superuser :
                    return view_func(request, *args, **kwargs)
            
            else :
                messages.error(request, "You don't have permissions to access this page.")
                return redirect('master:home')
            
        return _wrapped_view
    return decorator

def admin_required(view_func) :
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs) :

        if request.user.is_staff or request.user.is_superuser :
            pass
        
        else :
            messages.error(request, "You Don't have permission to access this page.")
            return redirect('master:home')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def superuser(view_func) :
    @wraps
    def _wrapped_view(request, *args, **kwargs) :

        if request.user.is_superuser :
            pass

        else :
            messages.error(request, "You don't have permission to access this page.")
            return redirect('master:home')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view