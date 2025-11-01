from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from access.models import Role

class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # базовые роли
        self.role_user = Role.objects.create(name='user')
        self.role_admin = Role.objects.create(name='admin')

    def test_register_and_login_and_profile(self):
        # register
        resp = self.client.post('/api/register/', {
            "email": "u1@example.com",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "patronymic": "",
            "password": "pass12345",
            "password2": "pass12345"
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(email="u1@example.com").exists())

        # login
        resp = self.client.post('/api/login/', {
            "email": "u1@example.com",
            "password": "pass12345"
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        token = resp.data['token']
        self.assertTrue(isinstance(token, str) and len(token) > 10)

        # profile (GET)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get('/api/profile/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], "u1@example.com")

        # profile (PUT) — частичное обновление
        resp = self.client.put('/api/profile/', {"first_name": "Petr"}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['first_name'], "Petr")

        # profile (DELETE) — soft delete
        resp = self.client.delete('/api/profile/')
        self.assertEqual(resp.status_code, 204)

        # после удаления — логин невозможен
        resp = self.client.post('/api/login/', {
            "email": "u1@example.com",
            "password": "pass12345"
        }, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_login_invalid_password(self):
        # создаём юзера напрямую (менеджер хэширует пароль через bcrypt)
        User.objects.create_user(
            email="u2@example.com",
            password="goodpass",
            first_name="A",
            last_name="B",
            role=self.role_user
        )
        resp = self.client.post('/api/login/', {
            "email": "u2@example.com",
            "password": "wrongpass"
        }, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_profile_401_without_token(self):
        resp = self.client.get('/api/profile/')
        self.assertEqual(resp.status_code, 401)  # не аутентифицирован
