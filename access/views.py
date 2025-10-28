from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import AnonymousUser

from access.models import AccessRoleRule, Role, BusinessElement
from access.serializers import AccessRuleSerializer, RoleSerializer, BusinessElementSerializer


def _is_admin(request):
    if isinstance(getattr(request, 'user', None), AnonymousUser) or not request.user.is_authenticated:
        return False
    return bool(request.user.role and request.user.role.name == 'admin')


class AccessRuleListView(APIView):
    def get(self, request):
        if not _is_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        rules = AccessRoleRule.objects.all()
        return Response(AccessRuleSerializer(rules, many=True).data)

    def post(self, request):
        if not _is_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        ser = AccessRuleSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if not _is_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        rule_id = request.data.get('id')
        if not rule_id:
            return Response({'detail': 'id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rule = AccessRoleRule.objects.get(id=rule_id)
        except AccessRoleRule.DoesNotExist:
            return Response({'detail': 'Rule not found'}, status=status.HTTP_404_NOT_FOUND)
        ser = AccessRuleSerializer(rule, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleListView(APIView):
    def get(self, request):
        if not _is_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        roles = Role.objects.all()
        return Response(RoleSerializer(roles, many=True).data)

    def post(self, request):
        if not _is_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        ser = RoleSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessElementListView(APIView):
    def get(self, request):
        if not _is_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        els = BusinessElement.objects.all()
        return Response(BusinessElementSerializer(els, many=True).data)

    def post(self, request):
        if not _is_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        ser = BusinessElementSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
