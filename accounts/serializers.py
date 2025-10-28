from rest_framework import serializers
from accounts.models import User
from access.models import Role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'patronymic', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords must match')
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        # роль по умолчанию — 'user' (если есть). Если нет — оставим пустой, можно выдать позже.
        role = Role.objects.filter(name='user').first()
        return User.objects.create_user(role=role, **validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'patronymic', 'is_active')
        read_only_fields = ('email', 'is_active')
