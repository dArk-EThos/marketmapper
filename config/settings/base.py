"""
Base Django settings for Market Mapper.
"""

import os
from pathlib import Path

import environ
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths: BASE_DIR is the project root (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

# Application definition
INSTALLED_APPS = [
    # --- Unfold admin theme (must be before django.contrib.admin) ---
    "unfold",
    "unfold.contrib.filters",
    # --- Django core ---
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Third-party
    "django_extensions",
    "django_filters",
    # Local apps
    "apps.opportunities",
    "apps.pages",
    "apps.newsletter",
    "apps.blog",
    "apps.stories",
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

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Winnipeg"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django Unfold Admin Theme Configuration
UNFOLD = {
    "SITE_TITLE": "Market Mapper",
    "SITE_HEADER": "Market Mapper",
    "SITE_URL": "/",
    "SITE_LOGO": lambda request: static("img/MM-logo.svg"),
    "SITE_FAVICON": lambda request: static("img/favicon-32.png"),
    "SITE_SYMBOL": "storefront",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "apps.opportunities.admin.environment_callback",
    "COLORS": {
        "primary": {
            "50": "#e8f4f8",
            "100": "#c5e3ec",
            "200": "#9ecfdd",
            "300": "#74b9cd",
            "400": "#4fa5be",
            "500": "#2d8fa8",
            "600": "#227a92",
            "700": "#1a6479",
            "800": "#175268",
            "900": "#0e3a4b",
            "950": "#072530",
        },
        "warning": {
            "50": "#fff7ed",
            "100": "#ffedd5",
            "200": "#fed7aa",
            "300": "#fdba74",
            "400": "#fb923c",
            "500": "#f97900",
            "600": "#ea6c00",
            "700": "#c25a00",
            "800": "#9a4800",
            "900": "#7c3a00",
            "950": "#431e00",
        },
        "font": {
            "subtle-light": "#4b5563",  # Darker subtle text for better contrast
            "subtle-dark": "#9ca3af", 
            "default-light": "#111827",  # Very dark default text
            "default-dark": "#f9fafb",   # Light text on dark backgrounds
            "important-light": "#000000",  # Pure black for important text
            "important-dark": "#ffffff",   # Pure white for dark mode
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "navigation_expanded": False,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Dashboard"),
                "separator": False,
                "items": [
                    {
                        "title": _("Home"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Markets"),
                "separator": True,
                "items": [
                    {
                        "title": _("Opportunities"),
                        "icon": "event",
                        "link": reverse_lazy("admin:opportunities_opportunity_changelist"),
                    },
                    {
                        "title": _("Regions"),
                        "icon": "map",
                        "link": reverse_lazy("admin:opportunities_region_changelist"),
                    },
                ],
            },
            {
                "title": _("Content"),
                "separator": True,
                "items": [
                    {
                        "title": _("Blog Posts"),
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_blogpost_changelist"),
                    },
                    {
                        "title": _("Vendor Stories"),
                        "icon": "auto_stories",
                        "link": reverse_lazy("admin:stories_vendorstory_changelist"),
                    },
                ],
            },
            {
                "title": _("System"),
                "separator": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
    "STYLES": [
        "admin/css/elegant_admin.css",
        "admin/css/admin-contrast-fix.css",
    ],
}
