import os
from pathlib import Path
from dotenv import load_dotenv

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные из .env (если файл есть)
load_dotenv(BASE_DIR / '.env')

# ----- БАЗА -----
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes', 'on')
# Можно указать несколько хостов через запятую в .env
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',') if h.strip()]

# ----- ПРИЛОЖЕНИЯ -----
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',

    # Наши
    'accounts',
    'access',
    'business',
]

# ----- MIDDLEWARE -----
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Наш кастомный JWT-мидлвар
    'accounts.middleware.JWTMiddleware',
]

ROOT_URLCONF = 'auth_system.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'auth_system.wsgi.application'

# ----- БАЗА ДАННЫХ -----
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'authdb'),
        'USER': os.getenv('DB_USER', 'authuser'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'authpass'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Кастомная модель пользователя
AUTH_USER_MODEL = 'accounts.User'

# ----- ЛОКАЛИ -----
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ----- СТАТИКА -----
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----- DRF -----
# Мы используем свой JWT middleware, поэтому отключаем стандартные аутентификаторы DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}
