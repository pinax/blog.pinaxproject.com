import os

import dj_database_url

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = PACKAGE_ROOT

SITE_ID = int(os.environ.get("SITE_ID", 1))
DEBUG = SITE_ID == 1

DATABASES = {
    "default": dj_database_url.config(default="postgres://localhost/ppb")
}

ALLOWED_HOSTS = [
    "blog.pinaxproject.com"
]

if os.environ.get("GONDOR_INSTANCE_DOMAIN") is not None:
    ALLOWED_HOSTS.append(
        os.environ["GONDOR_INSTANCE_DOMAIN"]
    )

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "US/Eastern"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

MEDIA_ROOT = os.path.join(
    os.environ.get("GONDOR_DATA_DIR", PACKAGE_ROOT),
    "site_media",
    "media"
)
STATIC_ROOT = os.path.join(
    os.environ.get("GONDOR_DATA_DIR", PACKAGE_ROOT),
    "site_media",
    "static"
)

MEDIA_URL = "/site_media/media/"
STATIC_URL = "/site_media/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static", "dist"),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Make this unique, and don"t share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY", "fake")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PACKAGE_ROOT, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "pinax_theme_bootstrap.context_processors.theme",
                "ppb.context_processors.settings",
            ],
        },
    },
]


MIDDLEWARE_CLASSES = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "opbeat.contrib.django.middleware.OpbeatAPMMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ppb.urls"

# Python dotted path to the WSGI application used by Django"s runserver.
WSGI_APPLICATION = "ppb.wsgi.application"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",

    # theme
    "bootstrapform",
    "pinax_theme_bootstrap",

    # external
    "pinax.blog",
    "pinax.pages",
    "taggit",
    "opbeat.contrib.django",
    "reversion",
    "metron",

    # project
    "ppb",
]

OPBEAT = {
    "ORGANIZATION_ID": os.environ.get("OPBEAT_ORG_ID"),
    "APP_ID": os.environ.get("OPBEAT_APP_ID"),
    "SECRET_TOKEN": os.environ.get("OPBEAT_SECRET_TOKEN")
}

PINAX_BLOG_FEED_TITLE = "The Pinax Project Blog"
PINAX_BLOG_SECTION_FEED_TITLE = "The Pinax Project Blog (%s)"
PINAX_BLOG_SECTIONS = [
    ("release-notes", "Release Notes"),
    ("how-tos", "How Tos"),
    ("design-decisions", "Design Decisions"),
    ("general", "General")
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}

METRON_SETTINGS = {
    "google": {
        2: "UA-2401894-50",
    }
}

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]
PINAX_BLOG_UNPUBLISHED_STATES = ["Raw", "Draft", "Reviewed"]

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "developers@pinaxproject.com"
