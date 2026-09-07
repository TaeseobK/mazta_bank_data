from django.contrib import admin


def auto_admin(model, *, list_filter=()):
    """Build a ModelAdmin that introspects the model's fields.

    Shows every field except id/created_at, links on all of them, and searches
    CharFields. Replaces the copy-pasted comprehensions in each app's admin.py.
    """
    fields = [f.name for f in model._meta.get_fields()
              if f.name not in ("id", "created_at")]
    chars = [f.name for f in model._meta.get_fields()
             if getattr(f, "get_internal_type", lambda: "")() == "CharField"]
    return type(f"{model.__name__}Admin", (admin.ModelAdmin,), {
        "list_display": fields,
        "list_display_links": fields,
        "search_fields": chars,
        "list_filter": tuple(list_filter),
    })
