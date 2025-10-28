from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser

class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, "user", None)
        return (u is not None) and (not isinstance(u, AnonymousUser)) and getattr(u, "is_active", False) is True
