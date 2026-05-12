from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class LoginAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("login")
        self.username = "alice"
        self.password = "wonderland123"
        self.email = "alice@example.com"
        self.user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )

    def test_login_success_creates_session_and_returns_200(self):
        payload = {"username": self.username, "password": self.password}
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response schema
        self.assertIn("id", response.data)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], self.username)
        self.assertEqual(response.data["email"], self.email)

        # Session cookie should be set by Django login
        # Django sets 'sessionid' cookie by default
        cookies = response.cookies
        self.assertIn("sessionid", cookies, "Expected sessionid cookie to be set on login")
        self.assertTrue(cookies["sessionid"].value, "sessionid cookie should have a value")

    def test_login_invalid_password_returns_400(self):
        payload = {"username": self.username, "password": "wrongpass"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should include non_field_errors with our message
        self.assertIn("non_field_errors", response.data)
        self.assertIn("Invalid username or password.", response.data["non_field_errors"]) 

    def test_login_missing_fields_returns_400(self):
        # Missing username
        response_u = self.client.post(self.url, {"password": self.password}, format="json")
        self.assertEqual(response_u.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response_u.data)

        # Missing password
        response_p = self.client.post(self.url, {"username": self.username}, format="json")
        self.assertEqual(response_p.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response_p.data)
