from django.contrib import admin

from .models import AuditLog


class AuditLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(AuditLog, AuditLogAdmin)
