from rest_framework import serializers
from access.models import AccessRoleRule, Role, BusinessElement


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = '__all__'


class AccessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRoleRule
        fields = '__all__'
