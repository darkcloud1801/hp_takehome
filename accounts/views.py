from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from accounts.models import CustomUser
from accounts.serializers import CustomUserSerializer

User = get_user_model()


class CustomUserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        include_all = (
            self.request.query_params.get("include_all", "false").lower() == "true"
        )

        return CustomUser.filtered_objects.specific_to_user(
            self.request.user, include_all
        )


class CustomUserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        audit_log_model = apps.get_model("history", "AuditLog")
        user = serializer.save()

        audit_log_model.objects.create(
            action="create",
            user=self.request.user,
            model_name=user.__class__.__name__,
            object_id=user.id,
        )


class CustomUserDetailView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    lookup_field = "pk"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.filtered_objects.specific_to_user(self.request.user)


class CustomUserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        user = serializer.save()

        audit_log_model = apps.get_model("history", "AuditLog")
        audit_log_model.objects.create(
            action="update",
            user=self.request.user,
            model_name=user.__class__.__name__,
            object_id=user.id,
        )


class CustomUserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    lookup_field = "pk"
    permission_classes = [IsAdminUser]

    def perform_destroy(self, instance):
        audit_log_model = apps.get_model("history", "AuditLog")
        audit_log_model.objects.create(
            action="soft-delete",
            user=self.request.user,
            model_name=instance.__class__.__name__,
            object_id=instance.id,
        )
        instance.soft_deleted = True
        instance.save()

    def destroy(self, request, *args, **kwargs):
        # Perform the deletion
        instance = self.get_object()
        self.perform_destroy(instance)

        # Return a custom response after deletion
        return Response(
            {
                "message": "User successfully soft deleted",
                "id": instance.pk,
            },
            status=status.HTTP_200_OK,
        )
