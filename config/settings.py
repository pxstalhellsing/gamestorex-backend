
"""
Django settings for GamestoreX project.
Django 5.2 + MongoDB + Django REST Framework
"""

from pathlib import Path
import os
from dotenv import load_dotenv


# --------------------------------------------------
# 1. CONFIGURACIÓN GENERAL
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables del archivo .env
load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# 2. SEGURIDAD
# --------------------------------------------------

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "No se encontró DJANGO_SECRET_KEY en el archivo .env"
    )

DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in (
    "true", "1", "yes"
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]


# --------------------------------------------------
# 3. CONFIGURACIÓN DE MONGODB
# --------------------------------------------------

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError(
        "No se encontró MONGODB_URI en el archivo .env"
    )

DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": MONGODB_URI,
        "NAME": "gamestorex",
    }
}

# Router de MongoDB
DATABASE_ROUTERS = [
    "django_mongodb_backend.routers.MongoRouter"
]


# --------------------------------------------------
# 4. APLICACIONES INSTALADAS
# --------------------------------------------------

INSTALLED_APPS = [

    # Django REST Framework
    "rest_framework",

    # Configuraciones especiales para MongoDB
    "config.apps.MongoAdminConfig",
    "config.apps.MongoAuthConfig",
    "config.apps.MongoContentTypesConfig",

    # Aplicaciones de Django
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Backend de MongoDB
    "django_mongodb_backend",
    'api',

]


# --------------------------------------------------
# 5. MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------------
# 6. CONFIGURACIÓN DE URLS
# --------------------------------------------------

ROOT_URLCONF = "config.urls"


# --------------------------------------------------
# 7. CONFIGURACIÓN DE PLANTILLAS
# --------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# --------------------------------------------------
# 8. SERVIDOR WSGI
# --------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"


# --------------------------------------------------
# 9. CONFIGURACIÓN DE DJANGO REST FRAMEWORK
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}


# --------------------------------------------------
# 10. VALIDACIÓN DE CONTRASEÑAS
# --------------------------------------------------

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


# --------------------------------------------------
# 11. IDIOMA Y ZONA HORARIA
# --------------------------------------------------

LANGUAGE_CODE = "es"

TIME_ZONE = "America/Santiago"

USE_I18N = True

USE_TZ = True


# --------------------------------------------------
# 12. ARCHIVOS ESTÁTICOS
# --------------------------------------------------

STATIC_URL = "static/"


# --------------------------------------------------
# 13. IDENTIFICADORES DE MONGODB
# --------------------------------------------------

DEFAULT_AUTO_FIELD = (
    "django_mongodb_backend.fields.ObjectIdAutoField"
)


# --------------------------------------------------
# 14. MIGRACIONES ESPECIALES DE MONGODB
# --------------------------------------------------

MIGRATION_MODULES = {
    "admin": "mongo_migrations.admin",
    "auth": "mongo_migrations.auth",
    "contenttypes": "mongo_migrations.contenttypes",
}
