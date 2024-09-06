from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from snippets import views

urlpatterns = [
    path("", views.SnippetList.as_view(), name="snippet-list"),
    path("<int:pk>/", views.SnippetDetail.as_view(), name="snippet-detail"),
    path(
        "<int:pk>/highlight/",
        views.SnippetHighlight.as_view(),
        name="snippet-highlight",
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
