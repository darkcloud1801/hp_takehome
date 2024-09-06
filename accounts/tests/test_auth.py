from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class AuthTestCaseBase(APITestCase):
    fixtures = ["accounts_users"]

    def setUp(self):
        for user in CustomUser.objects.all():
            user.password = make_password(user.password)
            user.save()

        self.staff_user = CustomUser.objects.get(pk=1)
        self.non_staff_user = CustomUser.objects.get(pk=2)
        self.active_user = CustomUser.objects.get(pk=3)
        self.inactive_user = CustomUser.objects.get(pk=4)


class AuthTests(AuthTestCaseBase):
    def test_staff_user_can_use_session_for_endpoint(self):
        self.client.login(username="rubindamian-staff", password="password1234!")
        response = self.client.get(reverse("customuser-list"), {"include_all": "true"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_anonymous_cant_access_endpoint(self):
        response = self.client.get(reverse("customuser-list"), {"include_all": "true"})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_staff_user_can_use_token(self):
        response = self.client.post(
            reverse("api-token-auth"),
            {"username": "rubindamian-staff", "password": "password1234!"},
        )
        self.token = response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(reverse("customuser-list"), {"include_all": "true"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # def test_staff_user_can_see_only_active_users(self):
    #     self.client.force_authenticate(user=self.staff_user)
    #     response = self.client.get(reverse("customuser-list"), {"include_all": "false"})
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertEqual(3, response.data["count"])
    #
    # def test_non_staff_user_can_see_only_active_users(self):
    #     self.client.force_authenticate(user=self.non_staff_user)
    #     response = self.client.get(reverse("customuser-list"))
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertEqual(3, response.data["count"])
    #
    # def test_unauthenticated_user_cannot_access(self):
    #     response = self.client.get(reverse("customuser-list"))
    #     self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
