import datetime, jwt
from django.conf import settings
from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from django.contrib.auth.models import AnonymousUser
from accounts.middleware import JWTMiddleware
from accounts.permissions import IsAuthenticatedCustom
from accounts.models import User
from access.models import Role
from rest_framework.exceptions import NotAuthenticated

class MiddlewarePermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.role_user = Role.objects.create(name='user')
        self.user = User.objects.create_user(
            email="m1@example.com",
            password="pass12345",
            first_name="M",
            last_name="W",
            role=self.role_user
        )
        self.middleware = JWTMiddleware(get_response=lambda r: r)  # no-op

    def _make_token(self, user_id, exp_delta_hours=1):
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=exp_delta_hours)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def test_middleware_sets_user_on_valid_token(self):
        token = self._make_token(self.user.id)
        req = self.factory.get('/api/profile/', HTTP_AUTHORIZATION=f"Bearer {token}")
        # до мидлвара
        self.assertTrue(isinstance(getattr(req, 'user', AnonymousUser()), AnonymousUser))
        # прогоняем мидлвар
        self.middleware.process_request(req)
        self.assertEqual(getattr(req, '_user', None).id, self.user.id)
        self.assertEqual(getattr(req, 'user', None).id, self.user.id)

    def test_middleware_keeps_anonymous_on_invalid_token(self):
        req = self.factory.get('/api/profile/', HTTP_AUTHORIZATION="Bearer invalid.token.here")
        self.middleware.process_request(req)
        self.assertTrue(isinstance(req.user, AnonymousUser))

    def test_permission_allows_active_user(self):
        token = self._make_token(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        # дергаем защищённый эндпоинт — если permission пропускает, будет 200
        resp = self.client.get('/api/profile/')
        self.assertIn(resp.status_code, (200,))  # сам факт прохождения

    def test_permission_denies_anonymous(self):
        perm = IsAuthenticatedCustom()
        req = self.factory.get('/api/profile/')
        req.user = AnonymousUser()
        with self.assertRaises(NotAuthenticated):
            perm.has_permission(req, view=None)
