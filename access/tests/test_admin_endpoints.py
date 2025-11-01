# access/tests/test_admin_endpoints.py
import datetime, jwt
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from access.models import Role, BusinessElement, AccessRoleRule

class AdminEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role_admin = Role.objects.create(name='admin')
        self.role_user  = Role.objects.create(name='user')

        self.admin = User.objects.create_user(email="admin@ex.com", password="admin123", first_name="A", last_name="D", role=self.role_admin)
        self.user  = User.objects.create_user(email="user@ex.com",  password="user123",  first_name="U", last_name="S", role=self.role_user)

        self.el_products = BusinessElement.objects.create(name='products')

    def _token(self, uid, hours=1):
        payload = {"user_id": uid, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=hours)}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def test_non_admin_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token(self.user.id)}")
        resp = self.client.get('/api/roles/')
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get('/api/elements/')
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get('/api/access-rules/')
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_list_and_create_role_element_rule(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token(self.admin.id)}")

        # list roles (есть хотя бы admin/user)
        r = self.client.get('/api/roles/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()), 2)

        # create role
        r = self.client.post('/api/roles/', {"name": "manager"}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Role.objects.filter(name='manager').exists())

        # list elements
        r = self.client.get('/api/elements/')
        self.assertEqual(r.status_code, 200)

        # create element
        r = self.client.post('/api/elements/', {"name": "orders"}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(BusinessElement.objects.filter(name='orders').exists())

        # create access rule (user -> products, read own)
        rule_payload = {
            "role": self.role_user.id,
            "element": self.el_products.id,
            "read_permission": True,
            "read_all_permission": False,
            "create_permission": False,
            "update_permission": False,
            "update_all_permission": False,
            "delete_permission": False,
            "delete_all_permission": False
        }
        r = self.client.post('/api/access-rules/', rule_payload, format='json')
        self.assertEqual(r.status_code, 201)
        rule_id = r.json()['id']

        # update rule (turn on read_all)
        r = self.client.put('/api/access-rules/', {"id": rule_id, "read_all_permission": True}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(AccessRoleRule.objects.get(id=rule_id).read_all_permission)
