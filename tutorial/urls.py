from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from tutorial.views import api_root

urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("snippets/", include("snippets.urls")),
    path("accounts/", include("accounts.urls")),
]
