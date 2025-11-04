import environ
from pathlib import Path
from datetime import timedelta
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
#If DEBUG:False Django will not serve static files by itself.
DEBUG = env("DEBUG")
#DEBUG = False

ALLOWED_HOSTS = ["*", "http://localhost:3000"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework_simplejwt.token_blacklist",
    "apps.users",
    "apps.social_accounts",
    "apps.coin",
    "apps.transactions",
    "apps.company",
    "apps.complaints_book",
    "apps.blogs",
    "dj_rest_auth.registration",
    "rest_framework.authtoken",
]

SOCIALACCOUNT_PROVIDERS = {
   'google': {
       'APP': {
           'client_id': env('GOOGLE_CLIENT_ID'),
           'secret': env('GOOGLE_CLIENT_SECRET'), 
       }
   }
}

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://braspertransferencias.com",
    "https://www.braspertransferencias.com",
    "http://localhost",
]
CORS_ALLOW_CREDENTIALS = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://braspertransferencias.com",
    "https://www.braspertransferencias.com",
]
ROOT_URLCONF = "backend.urls"

WSGI_APPLICATION = "backend.wsgi.application"

# AUTH_USER_MODEL = 'apps.users.User'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

#-------------------------------------------------
#         Base de datos de Prueba
#-------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'brasper_pro',
        'USER': 'postgres',
        'PASSWORD': '9780ubuntu',
        'HOST': '213.199.44.2',
	    'PORT': '5432',
    }
}

#-------------------------------------------------
#         Base de datos de Produccion
#-------------------------------------------------


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'pruebas',
#         'USER': 'postgres',
#         'PASSWORD': '9780ubuntu',
#         'HOST': '213.199.44.2',
# 	    'PORT': '5432',
#     }
# }


REST_FRAMEWORK = {
    "NON_FIELD_ERRORS_KEY": "error",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    #TODOS LOS ENDPOINTS DEBEN SER AUTENTICADOS
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),


}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]


DOMAIN = "localhost:3000"
SITE_NAME = "Henry Ultimate Authentication Course"

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")
SOCIAL_AUTH_PASSWORD = "jgk348030gjw03"

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

AUTH_USER_MODEL = "users.User"  # reemplaza 'users' con el nombre de tu app

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# AUTH_USER_MODEL = 'apps.users.User'  # Cambia de 'auth.User' a 'users.User'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FRONTEND_URL = 'https://braspertransferencias.com/'  # Cambia esto según tu entorno

# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'  # O el que uses
EMAIL_PORT = 465
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'support@brasper.com'  # Usa variables de entorno en producción
EMAIL_HOST_PASSWORD = 'x+ClH#]r73'  # Usa variables de entorno en producción
DEFAULT_FROM_EMAIL = 'support@brasper.com'
RESEND_SMTP_PORT = 587
RESEND_SMTP_USERNAME = 'resend'
RESEND_SMTP_HOST = 'smtp.resend.com'
RESEND_API_KEY = env('RESEND_API_KEY')
REST_USE_JWT = True 
# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'backend', 'templates'),  # Ruta ajustada para tu estructura
        ],
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

# # Para desarrollo (opcional)
# if DEBUG:
#     EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#     EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'templates/emails')
#     if not os.path.exists(EMAIL_FILE_PATH):
#         os.makedirs(EMAIL_FILE_PATH)

# FILE UPLOADS
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Google OAUTH
# Read sensitive values from environment variables to avoid committing secrets
GOOGLE_OAUTH_CLIENT_ID = env('GOOGLE_OAUTH_CLIENT_ID', default='')
GOOGLE_OAUTH_CLIENT_SECRET = env('GOOGLE_OAUTH_CLIENT_SECRET', default='')
GOOGLE_OAUTH_CALLBACK_URL = env('GOOGLE_OAUTH_CALLBACK_URL', default='http://localhost:8000/api/v1/auth/google/callback/')

# Google OAuth Settings
GOOGLE_OAUTH2_CLIENT_ID = env('GOOGLE_OAUTH2_CLIENT_ID', default='')
GOOGLE_OAUTH2_CLIENT_SECRET = env('GOOGLE_OAUTH2_CLIENT_SECRET', default='')
GOOGLE_OAUTH2_REDIRECT_URI = env('GOOGLE_OAUTH2_REDIRECT_URI', default='')

# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         },
#     },
# }
