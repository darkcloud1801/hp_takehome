from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from accounts import views

urlpatterns = [
    path("", views.CustomUserListView.as_view(), name="customuser-list"),
    path("<int:pk>/", views.CustomUserDetailView.as_view(), name="customuser-detail"),
    path(
        "create-user/", views.CustomUserCreateView.as_view(), name="customuser-create"
    ),
    path(
        "update-user/<int:pk>/",
        views.CustomUserUpdateView.as_view(),
        name="customuser-update",
    ),
    path(
        "delete-user/<int:pk>/",
        views.CustomUserDeleteView.as_view(),
        name="customuser-delete",
    ),
    path("token/", obtain_auth_token, name="api-token-auth"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
