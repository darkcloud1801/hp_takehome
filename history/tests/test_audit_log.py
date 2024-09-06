from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class AuditLogTestCaseBase(APITestCase):
    fixtures = ["accounts_users", "snippets_snippets"]

    def setUp(self):
        self.audit_log_model = apps.get_model("history", "AuditLog")

        for user in CustomUser.objects.all():
            user.password = make_password(user.password)
            user.save()

        self.staff_user = CustomUser.objects.get(pk=1)
        self.non_staff_user = CustomUser.objects.get(pk=2)
        self.active_user = CustomUser.objects.get(pk=3)
        self.inactive_user = CustomUser.objects.get(pk=4)


class CustomUserAuditLogListViewTests(AuditLogTestCaseBase):
    def test_staff_user_can_see_all_users(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse("customuser-list"), {"include_all": "true"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(0, self.audit_log_model.objects.count())

    def test_staff_user_can_create_user(self):
        self.client.force_authenticate(user=self.staff_user)
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }
        response = self.client.post(
            reverse("customuser-create"), data=user_data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, self.audit_log_model.objects.count())

        audit_log_entry = self.audit_log_model.objects.first()
        self.assertEqual(self.staff_user.username, audit_log_entry.user.username)
        self.assertEqual("create", audit_log_entry.action)

    def test_staff_user_can_update_user(self):
        self.client.force_authenticate(user=self.staff_user)

        user_data = {
            "email": "updated@example.com",
        }

        response = self.client.patch(
            reverse("customuser-update", kwargs={"pk": 3}),
            data=user_data,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, self.audit_log_model.objects.count())
        audit_log_entry = self.audit_log_model.objects.first()
        self.assertEqual("update", audit_log_entry.action)

    def test_staff_user_can_delete_user(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.delete(reverse("customuser-delete", kwargs={"pk": 3}))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, self.audit_log_model.objects.count())
        audit_log_entry = self.audit_log_model.objects.first()
        self.assertEqual("soft-delete", audit_log_entry.action)


class SnippetAuditLogDeleteViewTests(AuditLogTestCaseBase):
    def test_staff_user_can_see_all_snippets(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse("snippet-list"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(0, self.audit_log_model.objects.count())

    def test_staff_user_can_create_user(self):
        self.client.force_authenticate(user=self.staff_user)
        snippet_data = {
            "title": "JustSnippet",
            "code": "<html><body></body></html>",
            "linenos": True,
            "language": "python",
            "style": "friendly",
            "owner": self.staff_user.pk,
        }

        response = self.client.post(
            reverse("snippet-list"), data=snippet_data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, self.audit_log_model.objects.count())

        audit_log_entry = self.audit_log_model.objects.first()
        self.assertEqual(self.staff_user.username, audit_log_entry.user.username)
        self.assertEqual("create", audit_log_entry.action)

    def test_owner_can_update_snippet(self):
        self.client.force_authenticate(user=self.active_user)

        snippet_data = {"linenos": False}

        response = self.client.patch(
            reverse("snippet-detail", kwargs={"pk": 1}),
            data=snippet_data,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, self.audit_log_model.objects.count())
        audit_log_entry = self.audit_log_model.objects.first()
        self.assertEqual("update", audit_log_entry.action)

    def test_owner_can_delete_snippet(self):
        self.client.force_authenticate(user=self.active_user)

        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": 1}))

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(1, self.audit_log_model.objects.count())
        audit_log_entry = self.audit_log_model.objects.first()
        self.assertEqual("delete", audit_log_entry.action)
