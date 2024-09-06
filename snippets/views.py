from django.apps import apps
from rest_framework import generics, permissions, renderers
from rest_framework.response import Response

from .models import Snippet
from .permissions import IsOwnerOrReadOnly
from .serializers import SnippetSerializer


class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        audit_log_model = apps.get_model("history", "AuditLog")

        snippet = serializer.save(owner=self.request.user)

        audit_log_model.objects.create(
            action="create",
            user=self.request.user,
            model_name=snippet.__class__.__name__,
            object_id=snippet.id,
        )


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )

    def perform_update(self, serializer):
        snippet = serializer.save()

        audit_log_model = apps.get_model("history", "AuditLog")
        audit_log_model.objects.create(
            action="update",
            user=self.request.user,
            model_name=snippet.__class__.__name__,
            object_id=snippet.id,
        )

    def perform_destroy(self, instance):
        audit_log_model = apps.get_model("history", "AuditLog")
        audit_log_model.objects.create(
            action="delete",
            user=self.request.user,
            model_name=instance.__class__.__name__,
            object_id=instance.id,
        )
        instance.delete()
