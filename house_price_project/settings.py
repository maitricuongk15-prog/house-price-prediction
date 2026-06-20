"""
Django settings cho NhàAI – House Price Prediction
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-nha-ai-change-this-in-production-2025'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'daphne',          # ← PHẢI đứng đầu tiên để runserver chạy ASGI
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'predictor',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'house_price_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ── ASGI thay cho WSGI (bắt buộc cho Channels) ─────────────
ASGI_APPLICATION = 'house_price_project.asgi.application'

# Giữ lại WSGI để tương thích (không xoá)
WSGI_APPLICATION = 'house_price_project.wsgi.application'

# ── Channel Layers (In-Memory – đơn giản, không cần cài Redis) ──
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Nếu sau này cần Redis (production, nhiều server/process), đổi lại thành:
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
#     },
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE     = 'Asia/Ho_Chi_Minh'
USE_I18N      = True
USE_TZ        = True

# Static files
STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT      = BASE_DIR / 'staticfiles'

# Media (ảnh upload)
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirect sau login/logout
LOGIN_URL           = '/dang-nhap/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'

# Messages tags
from django.contrib.messages import constants as messages_constants
MESSAGE_TAGS = {
    messages_constants.DEBUG:   'debug',
    messages_constants.INFO:    'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR:   'error',
}