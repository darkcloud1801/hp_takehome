from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from snippets.models import Snippet


class SnippetsTestCaseBase(APITestCase):
    fixtures = ["accounts_users", "snippets_snippets"]

    def setUp(self):
        custom_user_model = apps.get_model("accounts.CustomUser")
        for user in custom_user_model.objects.all():
            user.password = make_password(user.password)
            user.save()

        self.staff_user = CustomUser.objects.get(pk=1)
        self.non_staff_user = CustomUser.objects.get(pk=2)
        self.active_user = CustomUser.objects.get(pk=3)
        self.inactive_user = CustomUser.objects.get(pk=4)


class SnippetsListViewTests(SnippetsTestCaseBase):
    def test_staff_user_can_see_all_snippets(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(reverse("snippet-list"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data["count"])

    def test_non_staff_user_can_see_only_active_users(self):
        self.client.force_authenticate(user=self.non_staff_user)

        response = self.client.get(reverse("snippet-list"))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data["count"])


class SnippetsCreateViewTests(SnippetsTestCaseBase):
    def test_staff_user_can_create_snippets(self):
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
        self.assertEqual(2, Snippet.objects.count())
        self.assertEqual("JustSnippet", Snippet.objects.last().title)

    def test_non_staff_user_can_create_snippet(self):
        self.client.force_authenticate(user=self.non_staff_user)
        snippet_data = {
            "title": "JustSnippet-non-staff",
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
        self.assertEqual(2, Snippet.objects.count())
        self.assertEqual("JustSnippet-non-staff", Snippet.objects.last().title)


class SnippetDetailViewTests(SnippetsTestCaseBase):
    def test_staff_user_can_see_snippet(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(reverse("snippet-detail", kwargs={"pk": 1}))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data["id"])

    def test_non_staff_user_can_see_snippet(self):
        self.client.force_authenticate(user=self.non_staff_user)

        response = self.client.get(reverse("snippet-detail", kwargs={"pk": 1}))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data["id"])


class SnippetUpdateViewTests(SnippetsTestCaseBase):
    def test_only_owner_can_update_snippet(self):
        self.client.force_authenticate(user=self.active_user)

        snippet_data = {"linenos": False}

        response = self.client.patch(
            reverse("snippet-detail", kwargs={"pk": 1}),
            data=snippet_data,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(False, response.data["linenos"])

    def test_staff_user_cannot_update_snippet_when_they_arent_the_owner(self):
        self.client.force_authenticate(user=self.staff_user)

        snippet_data = {"linenos": False}

        response = self.client.patch(
            reverse("snippet-detail", kwargs={"pk": 1}),
            data=snippet_data,
            format="json",
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class CustomUserDeleteViewTests(SnippetsTestCaseBase):
    def test_staff_user_cannot_delete_snippet_they_dont_own(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": 1}))

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_owner_can_delete_snippet(self):
        self.client.force_authenticate(user=self.active_user)

        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": 1}))

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
