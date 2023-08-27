from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-rpo9pmgn%+1kn4n9xtz9l*3u(d-a)8p8pj*nlp3y!=pwwi*h(0'
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-rpo9pmgn%+1kn4n9xtz9l*3u(d-a)8p8pj*nlp3y!=pwwi*h(0",
)

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = os.environ.get("DJANGO_DEBUG", "") != "False"

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "channels",
    "api",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_user_agents",
    "realtime",
    "webapp",
]

SITE_ID = 1

# REST API AUTH
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        # 'rest_framework.authentication.BasicAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cyanase_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "cyanase_api.wsgi.application"
# channels
ASGI_APPLICATION = "cyanase_api.asgi.application"

# EMAIL_HOST = 'mail.cyanase.com'
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "support@cyanase.com"
# EMAIL_HOST_PASSWORD = "support@cyanase"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.cyanase.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "support@cyanase.com"
EMAIL_HOST_PASSWORD = "support@cyanase"


# # Database
# # https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "sql_mode": "traditional",
    }
    # "default": {
    #     "ENGINE": "django.db.backends.mysql",
    #     "OPTIONS": {
    #         "init_command": "ALTER DATABASE cyanase CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci",
    #     },
    #     "NAME": "cyanase",
    #     "USER": "cyanase",
    #     "PASSWORD": "Udbz.xC638L)BiE",
    #     "HOST": "127.0.0.1",
    #     "PORT": "3306",
    # }
}


# Django channels
CHANNEL_LAYERS = {
    "default": {
        # Method 2: Via local Redis
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
#############################
STATIC_ROOT = os.path.join(BASE_DIR, "assests")

STATIC_ROOT_URL = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
CORS_ORIGIN_ALLOW_ALL = True
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:3000",
]
CSRF_COOKIE_SECURE = True
