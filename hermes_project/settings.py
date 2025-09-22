import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('HERMES_SECRET', 'dev-secret')
DEBUG = os.getenv('HERMES_DEBUG', '1') == '1'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'hermes_app',
]

MIDDLEWARE = []

ROOT_URLCONF = 'hermes_project.urls'

TEMPLATES = []

WSGI_APPLICATION = 'hermes_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
