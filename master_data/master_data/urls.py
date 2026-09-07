from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),
    path('', include('human_resource.urls')),
    path('', include('master.urls')),
    path('', include('sales.urls')),
    path('', include('supplier.urls')),
] 

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)