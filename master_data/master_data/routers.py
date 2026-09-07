APP_DATABASES = {"human_resource", "master", "sales", "supplier"}


class AppRouter:
    """Route each app's models to a same-named database.

    Replaces the four identical per-app routers. Models whose app_label is not
    in APP_DATABASES fall through to the default database.
    """

    def db_for_read(self, model, **hints):
        label = model._meta.app_label
        return label if label in APP_DATABASES else None

    db_for_write = db_for_read

    def allow_relation(self, obj1, obj2, **hints):
        labels = {obj1._meta.app_label, obj2._meta.app_label}
        if len(labels) == 1:
            return True
        if labels & APP_DATABASES and "auth" in labels:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in APP_DATABASES:
            return db == app_label
        return None
