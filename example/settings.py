"""
Django settings for example project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

from os.path import abspath, basename, dirname, join, normpath, exists
from sys import path
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't*gnl6m_ybc$)oaue(=f4i0pi-i$=twoyhd$3z)-+u=k7e_m0@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'example',    
    'arcade',    
    
    # 3rd party    
    'compressor',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'example.urls'

WSGI_APPLICATION = 'example.wsgi.application'


### PATH ###
# Absolute filesystem path to the Django project directory:
ROOT = dirname(dirname(abspath(__file__)))


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


### STATIC FILE ###
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
#STATIC_ROOT = normpath(join(ROOT, 'static/'))

STATICFILES_DIRS = (
  os.path.join(ROOT, 'static/'),
  os.path.join(ROOT, 'arcade/static/'),
  os.path.join(ROOT, 'games/playpolitics/static/'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# this tells arcade where to look for gamd dirs.

ARCADE_DIR = os.path.join(ROOT, 'games/')


# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_FINDERS
# Warning: Do not put more entries here without talking to Brant.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',    

    'arcade.finders.ArcadeDirectoriesFinder',

    # Django Compressor
    'compressor.finders.CompressorFinder',

 
)

### DJANGO COMPRESSOR ###
# See: http://django_compressor.readthedocs.org/en/latest/settings/
COMPRESS_PRECOMPILERS = (
    ('text/sass', 'example.processors.SassFilter'),
)



