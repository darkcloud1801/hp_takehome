from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

class CustomUserAdmin(UserAdmin):

    def save_model(self, request, obj, form, change):
        if change:
            action = 'updated'
        else:
            action = 'created'

        super().save_model(request, obj, form, change)

        audit_log_model = apps.get_model("history", "AuditLog")
        audit_log_model.objects.create(
            action=action,
            model_name=obj.__class__.__name__,
            object_id=obj.pk,
            user=request.user
        )

    def delete_model(self, request, obj):
        audit_log_model = apps.get_model("history", "AuditLog")
        audit_log_model.objects.create(
            action='deleted',
            model_name=obj.__class__.__name__,
            object_id=obj.pk,
            user=request.user,
        )
        super().delete_model(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)
