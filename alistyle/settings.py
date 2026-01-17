from pathlib import Path
from decouple import config
import os
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = ["siddik-commerce-django.onrender.com", "127.0.0.1"]

# Session timeout setttings
# SESSION_EXPIRE_SECONDS = config("SESSION_EXPIRE_SECONDS", cast=int, default=True)
# SESSION_EXPIRE_AFTER_LAST_ACTIVITY = config(
#    "SESSION_EXPIRE_AFTER_LAST_ACTIVITY", cast=bool, default=True
# )
# SESSION_TIMEOUT_REDIRECT = '/accounts/login'

# Application definition

#SESSION_COOKIE_SAMESITE = 'Lax'  
#SESSION_COOKIE_SECURE = False  

INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "category",
    "store",
    "carts",
    "coupon",
    "orders",
    "payment"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django_session_timeout.middleware.SessionTimeoutMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "alistyle.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.sliders",
                "category.context_processors.menu_links",
                "carts.context_processors.counter",
            ],
        },
    },
]

WSGI_APPLICATION = "alistyle.wsgi.application"
AUTH_USER_MODEL = "accounts.Account"  # appname/modelname

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

#DATABASES = {
#    "default": {
#        "ENGINE": config("DB_ENGINE"),
#        "NAME": BASE_DIR / config("DB_NAME"),
#    }
#}

DATA_BASE_URL = config("DATA_BASE_URL")

if DATA_BASE_URL:
    url = urlparse(DATA_BASE_URL)
    
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
        }
    }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", _("English")),
    ("bn", _("Bangla")),
]

USE_I18N = True
USE_TZ = True
TIME_ZONE = "Asia/Dhaka"
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# ModelTranslation settings
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_LANGUAGES = ("en", "bn")
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    "default": ("en",),
    "bn": ("en",),
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles" # Where collectstatic cmd puts all collected static files (for production)
STATICFILES_DIRS = [] # Additional directories where Django looks for static files during development

if (BASE_DIR / "alistyle/static").exists():
    STATICFILES_DIRS = [
    BASE_DIR / "alistyle/static",
]

# for Render Production version
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MESSAGE_TAGS = {messages.ERROR: "danger", 50: "critical"}

# SMTP configuration
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
