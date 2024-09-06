from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class CustomUserTestCaseBase(APITestCase):
    fixtures = ["accounts_users"]

    def setUp(self):
        for user in CustomUser.objects.all():
            user.password = make_password(user.password)
            user.save()

        self.staff_user = CustomUser.objects.get(pk=1)
        self.non_staff_user = CustomUser.objects.get(pk=2)
        self.active_user = CustomUser.objects.get(pk=3)
        self.inactive_user = CustomUser.objects.get(pk=4)


class CustomUserListViewTests(CustomUserTestCaseBase):
    def test_staff_user_can_see_all_users(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse("customuser-list"), {"include_all": "true"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(4, response.data["count"])

    def test_staff_user_can_see_only_active_users(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse("customuser-list"), {"include_all": "false"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, response.data["count"])

    def test_non_staff_user_can_see_only_active_users(self):
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.get(reverse("customuser-list"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, response.data["count"])

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(reverse("customuser-list"))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)


class CustomUserDetailViewTests(CustomUserTestCaseBase):
    def test_staff_user_can_see_user(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse("customuser-detail", kwargs={"pk": 2}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data["id"])

    def test_non_staff_user_can_see_active_users(self):
        self.client.force_authenticate(user=self.non_staff_user)

        response = self.client.get(reverse("customuser-detail", kwargs={"pk": 2}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data["id"])

    def test_non_staff_user_cannot_see_active_users(self):
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.get(reverse("customuser-detail", kwargs={"pk": 4}))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(reverse("customuser-detail", kwargs={"pk": 2}))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)


class CustomUserCreateViewTests(CustomUserTestCaseBase):
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
        self.assertEqual("newuser", response.data["username"])
        self.assertIn("id", response.data)

    def test_non_staff_user_cannot_create_user(self):
        self.client.force_authenticate(user=self.non_staff_user)

        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }

        response = self.client.post(
            reverse("customuser-create"), data=user_data, format="json"
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class CustomUserUpdateViewTests(CustomUserTestCaseBase):
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
        self.assertEqual("updated@example.com", response.data["email"])

    def test_non_staff_user_cannot_create_user(self):
        self.client.force_authenticate(user=self.non_staff_user)

        user_data = {
            "email": "updated@example.com",
        }
        response = self.client.patch(
            reverse("customuser-update", kwargs={"pk": 3}),
            data=user_data,
            format="json",
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class CustomUserDeleteViewTests(CustomUserTestCaseBase):
    def test_staff_user_can_delete_user(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.delete(reverse("customuser-delete", kwargs={"pk": 3}))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, response.data["id"])
        self.assertEqual("User successfully soft deleted", response.data["message"])
