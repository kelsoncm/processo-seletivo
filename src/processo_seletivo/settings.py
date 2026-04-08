"""
Django settings for processo_seletivo project.
"""

from pathlib import Path
from decouple import config
import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-(p@kx2s3m2lvk8a50-jp^$uxehb=ij*5pud&7$g--%a(oks67v')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition

LOCAL_APPS = [
    'accounts',
    'processos',
    'inscricoes',
    'formularios',
    'avaliacoes',
    'recursos',
    'resultados',
    'auditoria',
    'tema',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'dsgovbr',
]

if config('DEBUG', default=True, cast=bool):
    THIRD_PARTY_APPS += ['django_extensions']


INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + [
        # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditoria.middleware.AuditMiddleware',
    'accounts.middlewares.CustomAnonymousUserMiddleware',
]

ROOT_URLCONF = 'processo_seletivo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "dsgovbr.context_processors.layout_settings",
            ],
        },
    },
]

WSGI_APPLICATION = 'processo_seletivo.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom user model
AUTH_USER_MODEL = 'accounts.Usuario'

# Internationalization
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = config('TIME_ZONE', default='America/Sao_Paulo')

USE_I18N = True

USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload limits (default 2 MB per document)
DEFAULT_MAX_UPLOAD_SIZE_MB = 2
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB total form data

# Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_TIMEZONE = TIME_ZONE

# Sentry
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)

# gov.br OAuth2 settings
GOVBR_CLIENT_ID = config('GOVBR_CLIENT_ID', default='')
GOVBR_CLIENT_SECRET = config('GOVBR_CLIENT_SECRET', default='')
GOVBR_AUTHORIZATION_URL = config(
    'GOVBR_AUTHORIZATION_URL',
    default='https://sso.staging.acesso.gov.br/authorize',
)
GOVBR_TOKEN_URL = config(
    'GOVBR_TOKEN_URL',
    default='https://sso.staging.acesso.gov.br/token',
)
GOVBR_USERINFO_URL = config(
    'GOVBR_USERINFO_URL',
    default='https://sso.staging.acesso.gov.br/userinfo',
)
GOVBR_REDIRECT_URI = config('GOVBR_REDIRECT_URI', default='http://localhost:8000/accounts/govbr/callback/')

# Email
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@example.gov.br')

# SUAP integration
SUAP_BASE_URL = config('SUAP_BASE_URL', default='')
SUAP_API_TOKEN = config('SUAP_API_TOKEN', default='')

# SUAP OAuth2 settings
SUAP_OAUTH_CLIENT_ID = config('SUAP_OAUTH_CLIENT_ID', default='')
SUAP_OAUTH_CLIENT_SECRET = config('SUAP_OAUTH_CLIENT_SECRET', default='')
SUAP_OAUTH_AUTHORIZATION_URL = config('SUAP_OAUTH_AUTHORIZATION_URL', default='https://suap.ifrn.edu.br/o/authorize/')
SUAP_OAUTH_TOKEN_URL = config('SUAP_OAUTH_TOKEN_URL', default='https://suap.ifrn.edu.br/o/token/')
SUAP_OAUTH_USERINFO_URL = config('SUAP_OAUTH_USERINFO_URL', default='https://suap.ifrn.edu.br/api/rh/eu/')
SUAP_OAUTH_REDIRECT_URI = config('SUAP_OAUTH_REDIRECT_URI', default='http://localhost:8000/accounts/suap/callback/')

# Login URL
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'



PROJECT_COMPANY = config("PROJECT_COMPANY", "KelsonCM")
PROJECT_TITLE = config("PROJECT_TITLE", "Seleção Simplificada")
PROJECT_SUBTITLE = config("PROJECT_SUBTITLE", "Processo seletivo simplificado")
PROJECT_VERSION = config("PROJECT_VERSION", "1.0.2")
PROJECT_LAST_STARTUP = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)
PROJECT_COPYRIGHT = config("PROJECT_COPYRIGHT", "🄯2026 KelsonCM")
PROJECT_LICENSE = config("PROJECT_LICENSE", "Licença MIT")
PROJECT_LICENSE_URL = config("PROJECT_LICENSE_URL", "https://opensource.org/license/mit")

