import datetime, jwt
from unittest.mock import patch
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from access.models import Role, BusinessElement, AccessRoleRule

class ProductsRBACTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # роли и элемент
        self.role_user = Role.objects.create(name='user')
        self.role_manager = Role.objects.create(name='manager')
        self.role_admin = Role.objects.create(name='admin')
        self.el_products = BusinessElement.objects.create(name='products')

        # пользователи
        self.u1 = User.objects.create_user(email="u1@ex.com", password="p1", first_name="U", last_name="One", role=self.role_user)
        self.u2 = User.objects.create_user(email="u2@ex.com", password="p2", first_name="U", last_name="Two", role=self.role_user)
        self.mgr = User.objects.create_user(email="m@ex.com",  password="p3", first_name="M", last_name="Gr",  role=self.role_manager)

        # правила: user — читать только свои; manager — читать все
        AccessRoleRule.objects.create(role=self.role_user, element=self.el_products, read_permission=True)
        AccessRoleRule.objects.create(role=self.role_manager, element=self.el_products, read_all_permission=True)

    def _token(self, uid, hours=1):
        payload = {"user_id": uid, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=hours)}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def test_401_without_token(self):
        resp = self.client.get('/api/products/')
        self.assertEqual(resp.status_code, 401)

    def test_403_when_no_rule_for_role(self):
        # создаём роль без правил
        role_guest = Role.objects.create(name='guest')
        g = User.objects.create_user(email="g@ex.com", password="pg", first_name="G", last_name="U", role=role_guest)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token(g.id)}")
        resp = self.client.get('/api/products/')
        self.assertEqual(resp.status_code, 403)

    def test_user_sees_only_own_products(self):
        # подменим MOCK_PRODUCTS так, чтобы айди владельца совпадали c u1/u2
        fake_products = [
            {"id": 10, "name": "P10", "owner_id": self.u1.id},
            {"id": 11, "name": "P11", "owner_id": self.u2.id},
            {"id": 12, "name": "P12", "owner_id": self.u1.id},
        ]
        with patch('business.views.MOCK_PRODUCTS', fake_products):
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token(self.u1.id)}")
            resp = self.client.get('/api/products/')
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(all(p['owner_id'] == self.u1.id for p in resp.json()))
            self.assertEqual(len(resp.json()), 2)

    def test_manager_sees_all_products(self):
        fake_products = [
            {"id": 10, "name": "P10", "owner_id": self.u1.id},
            {"id": 11, "name": "P11", "owner_id": self.u2.id},
            {"id": 12, "name": "P12", "owner_id": self.u1.id},
        ]
        with patch('business.views.MOCK_PRODUCTS', fake_products):
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token(self.mgr.id)}")
            resp = self.client.get('/api/products/')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 3)
