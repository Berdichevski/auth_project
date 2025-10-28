from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import AnonymousUser

from access.models import BusinessElement, AccessRoleRule

# проста́я демо-база «в памяти»
MOCK_PRODUCTS = [
    {"id": 1, "name": "Sneakers", "owner_id": 1},
    {"id": 2, "name": "Backpack", "owner_id": 2},
    {"id": 3, "name": "Cap", "owner_id": 1},
]


class ProductsMockView(APIView):
    element_name = 'products'

    def get(self, request):
        # 401 — если не аутентифицирован
        if isinstance(getattr(request, 'user', None), AnonymousUser) or not request.user.is_authenticated:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            element = BusinessElement.objects.get(name=self.element_name)
            rule = AccessRoleRule.objects.get(role=request.user.role, element=element)
        except (BusinessElement.DoesNotExist, AccessRoleRule.DoesNotExist):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        # чтение списка: read_all → все, read → только свои, иначе 403
        if rule.read_all_permission:
            return Response(MOCK_PRODUCTS)
        if rule.read_permission:
            own = [p for p in MOCK_PRODUCTS if p['owner_id'] == request.user.id]
            return Response(own)
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
