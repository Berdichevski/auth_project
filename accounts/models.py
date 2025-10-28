import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email required')
        if not password:
            raise ValueError('Password required')
        email = self.normalize_email(email)
        # bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, password_hash=hashed, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # суперпользователь нам нужен только для удобства (миграции/админка), бизнес-логика на нём не завязана
        extra_fields.setdefault('is_active', True)
        user = self.create_user(email, password, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    # связь с ролью RBAC (наша кастомная)
    role = models.ForeignKey('access.Role', on_delete=models.SET_NULL, null=True, blank=True)

    # храним только bcrypt-хэш
    password_hash = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    # переопределяем проверку пароля под bcrypt
    def check_password(self, raw_password):
        try:
            return bcrypt.checkpw(raw_password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False

    # блокируем базовые механики AbstractBaseUser
    def set_password(self, raw_password):
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.password_hash = hashed
