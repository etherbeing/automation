"""
Django settings for automation project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import logging
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-k!(e8-d74**!4s$s(t6pk0kqx*gjrt+gi+b*1_jd5j^y3@pbpt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'true') == 'true'


ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("ALLOWED_HOSTS", "").split(",")
]

CSRF_TRUSTED_ORIGINS = [
    *[f"http://{host}" for host in ALLOWED_HOSTS],
    *[f"https://{host}" for host in ALLOWED_HOSTS],
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mozilla_django_oidc',
    'solo',
    'lmd',
    'security'
]

# Provider specific settings
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         # For each OAuth based provider, either add a ``SocialApp``
#         # (``socialaccount`` app) containing the required client
#         # credentials, or list them here:
#         'APP': {
#             'client_id': '123',
#             'secret': '456',
#             'key': ''
#         }
#     }
# }


ENV_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DJANGO_LOG_LEVEL=getattr(logging, ENV_LOG_LEVEL)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": ENV_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": ENV_LOG_LEVEL,
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "formatters": {
        "verbose": {
            "format":
            "{levelname} {asctime} {module} {process:d} {thread:d} {message}\n",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {pathname}:{lineno} {message}\n",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "root": {
        "handlers": ["console", "mail_admins"],
        "level": ENV_LOG_LEVEL,
    },
}

AUTHENTICATION_BACKENDS = [
    'base.oidc.CustomOIDCAB', # Extends from mozilla_django_oidc.auth.OIDCAuthenticationBackend
    'django.contrib.auth.backends.ModelBackend',  # Default
]

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"

LOGIN_REDIRECT_URL = "/admin/"  # Redirect users after login

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware'
]
ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/"templates"],
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

WSGI_APPLICATION = 'base.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


ENV_DATABASE_NAME = os.getenv("DATABASE_NAME", )
ENV_DATABASE_USER = os.getenv("DATABASE_USER", )
ENV_DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", )
ENV_DATABASE_HOST = os.getenv("DATABASE_HOST", )
ENV_DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))

DATABASES = {
    "default": {  # PostgreSQL database
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": ENV_DATABASE_NAME,
        "USER": ENV_DATABASE_USER,
        "PASSWORD": ENV_DATABASE_PASSWORD,
        "HOST": ENV_DATABASE_HOST,
        "PORT": ENV_DATABASE_PORT,
    },
}

AUTH_USER_MODEL = "security.User"

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

LANGUAGES = (
    ["es", "Español"],
    ['en', "English"]
)

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REDIS_HOST = os.getenv('REDIS_HOST', "127.0.0.1")
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH  = BASE_DIR / "assets/emails"
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# For storing media files
STORAGES = {
    "default": {
        "BACKEND": "base.storage.DynamicS3Boto3Storage"
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
    }
}
# Set the URL for static files, if you're serving them from S3
STATIC_URL = f'/assets/'
STATIC_ROOT = BASE_DIR / 'assets/'


WHITENOISE_MANIFEST_STRICT = False

# Set AWS-related settings
ENV_AWS_CLIENT_ID = os.getenv("AWS_CLIENT_ID", )
ENV_AWS_CLIENT_SECRET = os.getenv("AWS_CLIENT_ID",)
ENV_AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
ENV_AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", )
ENV_AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "http://minio:9001")

AWS_ACCESS_KEY_ID = ENV_AWS_CLIENT_ID
AWS_SECRET_ACCESS_KEY = ENV_AWS_CLIENT_SECRET
AWS_STORAGE_BUCKET_NAME = ENV_AWS_STORAGE_BUCKET_NAME
AWS_S3_REGION_NAME = ENV_AWS_S3_REGION_NAME
AWS_S3_ENDPOINT_URL = ENV_AWS_S3_ENDPOINT_URL  # MinIO's S3 API URL
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_S3_USE_SSL = False  # Disable SSL for localhost
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_S3_USE_SSL = False  # Disable SSL for localhost

# Make media URL point to S3
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/media/'


ENV_KEYCLOAK_HOST = os.getenv("KEYCLOAK_HOST", 'http://keycloak:8080')
ENV_KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", 'automation')
ENV_KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", 'automation')
ENV_KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", None)


OIDC_RP_CLIENT_ID = ENV_KEYCLOAK_CLIENT_ID
OIDC_RP_CLIENT_SECRET = ENV_KEYCLOAK_CLIENT_SECRET
OIDC_OP_AUTHORIZATION_ENDPOINT = 'http://localhost:8080/realms/automation/protocol/openid-connect/auth'
OIDC_OP_TOKEN_ENDPOINT = 'http://localhost:8080/realms/automation/protocol/openid-connect/token'
OIDC_OP_USER_ENDPOINT = 'http://localhost:8080/realms/automation/protocol/openid-connect/userinfo'
OIDC_OP_JWKS_ENDPOINT = 'http://localhost:8080/realms/automation/protocol/openid-connect/certs'
OIDC_RP_SIGN_ALGO = 'RS256'  # Adjust if needed


# Celery beat configuration
ENV_RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
ENV_RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
ENV_RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
ENV_RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
ENV_RABBITMQ_PROTO = os.getenv("RABBITMQ_PROTO", "amqp")

# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = f'{ENV_RABBITMQ_PROTO}://{ENV_RABBITMQ_USERNAME}:{ENV_RABBITMQ_PASSWORD}@{ENV_RABBITMQ_HOST}:{ENV_RABBITMQ_PORT}/'
