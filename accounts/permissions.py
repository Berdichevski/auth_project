from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth.models import AnonymousUser

class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, "user", None)
        if (u is None) or isinstance(u, AnonymousUser) or (getattr(u, "is_active", False) is not True):
            # Явно сигнализируем DRF вернуть 401
            raise NotAuthenticated(detail="Unauthorized")
        return True
