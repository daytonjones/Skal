# skal/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"

###
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
###

# Hosts -----------------------------------------------------------------------

raw_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "")
if raw_hosts.strip() == "*":
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [
        h
        for part in raw_hosts.split(",")
        for h in part.split()
        if h
    ]

# CSRF ------------------------------------------------------------------------

# If we're truly allowing all hosts:
if ALLOWED_HOSTS == ["*"]:
    CSRF_TRUSTED_ORIGINS = []
    CSRF_TRUSTED_ORIGIN_REGEXES = [r"^https?://.*$"]
else:
    # Otherwise build explicit list of origins
    origins = []
    for host in ALLOWED_HOSTS:
        if host.startswith("[") or host == "*":
            continue
        origins.append(f"https://{host}")
        origins.append(f"http://{host}")
    CSRF_TRUSTED_ORIGINS = origins
    CSRF_TRUSTED_ORIGIN_REGEXES = []

# Proxy settings -------------------------------------------------------------

# If you sit behind an SSL-terminating proxy (e.g. nginx), let Django honor
# the X-Forwarded headers so that CSRF & request.build_absolute_uri() see the
# correct host and scheme.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Installed apps & middleware ------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
    "apps.recipes",
    "apps.batches",
    "apps.calculators",
    "apps.yeast",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "skal.urls"

# Templates -------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "skal.wsgi.application"

# Database --------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": "skal_db",
        "PORT": 5432,
    }
}

AUTH_USER_MODEL = "accounts.User"

# Static & media files -------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Authentication -------------------------------------------------------------

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "accounts:login"

# Sessions -------------------------------------------------------------------

# 30-day sessions
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Default auto field ---------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

