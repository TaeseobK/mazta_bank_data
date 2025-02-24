from django.conf import settings
from django.db import connections
from django.apps import apps

class SalesRouter :

    def db_for_read(self, model, **hints):
    # Jika model berasal dari 'user_profile', arahkan ke database 'profile'
        if model._meta.app_label == 'sales':
            return 'sales'
        return None

    def db_for_write(self, model, **hints):
        # Jika model berasal dari 'user_profile', arahkan ke database 'profile'
        if model._meta.app_label == 'sales':
            return 'sales'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Izinkan relasi antara model dari 'user_profile' dengan 'auth' atau model dalam aplikasi yang sama
        if (
            obj1._meta.app_label == 'sales' and obj2._meta.app_label == 'auth'
        ) or obj1._meta.app_label == obj2._meta.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Izinkan migrasi untuk aplikasi 'user_profile' hanya di database 'profile'
        if app_label == 'sales':
            return db == 'sales'
        return None