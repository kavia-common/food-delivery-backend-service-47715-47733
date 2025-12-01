from rest_framework.test import APITestCase
from django.urls import reverse


class HealthTests(APITestCase):
    def test_health(self):
        url = reverse('Health')  # Make sure the URL is named
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})


class AuthTests(APITestCase):
    def test_signup_and_login(self):
        signup_url = reverse('Signup')
        resp = self.client.post(signup_url, {"username": "alice", "email": "alice@example.com", "password": "S3curePassw0rd!"}, format="json")
        self.assertEqual(resp.status_code, 201)
        login_url = reverse('Login')
        resp2 = self.client.post(login_url, {"username": "alice", "password": "S3curePassw0rd!"}, format="json")
        self.assertEqual(resp2.status_code, 200)
        self.assertIn("username", resp2.data)
