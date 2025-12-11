"""Minimal Django settings for MQTT middleware demo"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-change-me'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'mqttmiddleware',
]

MIDDLEWARE = []

ROOT_URLCONF = 'proj.urls'

TEMPLATES = []

WSGI_APPLICATION = 'proj.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
