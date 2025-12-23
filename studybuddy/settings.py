"""
Django settings for studybuddy project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages
from decouple import config
import dj_database_url
# from dj_database_url import parse as db_url

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = config("SECRET_KEY")

# DEBUG = os.getenv("DEBUG") == "True"
# DEBUG = True
DEBUG = config("DEBUG", default=False, cast=bool)


# ALLOWED_HOSTS = config(
#     "ALLOWED_HOSTS",
#     default="127.0.0.1,localhost",
#     cast=lambda v: [s.strip() for s in v.split(",")]
# )
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'core.apps.CoreConfig',

    'api',   # chatgpt
    'core',  # our app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'studybuddy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'core' / 'templates' ],  # ensure templates folder is discoverable
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.uploader_status',
            ],
        },
    },
]

WSGI_APPLICATION = 'studybuddy.wsgi.application'


# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DB_NAME"),
#         "USER": os.getenv("DB_USER"),
#         "PASSWORD": os.getenv("DB_PASSWORD"),
#         "HOST": os.getenv("DB_HOST", "localhost"),
#         "PORT": os.getenv("DB_PORT", "5432"),
#     }
# }

DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL")
    )
}

# Use SQLite for development. On PythonAnywhere you'll switch to PostgreSQL as needed.
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Messages styling
MESSAGE_TAGS = {
    messages.SUCCESS: 'alert alert-success',
    messages.ERROR: 'alert alert-danger',
}

# Where to redirect for login_required decorator
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'



# Secure cookies (safe defaults)
# Automatically secure in production.
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG


# Logging (helps debug production crashes)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


if DEBUG:
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
    except:
        pass


import os

if os.environ.get("CREATE_SUPERUSER") == "1":
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
            print("✅ Superuser created")
    except Exception as e:
        print("❌ Superuser creation failed:", e)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"