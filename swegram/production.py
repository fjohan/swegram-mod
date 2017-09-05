import os

DEBUG = False

PRODUCTION = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = "/local/swegram/django/static"
STATIC_URL = '/swegramstatic/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'swegram_main/static'),)

ALLOWED_HOSTS = ['stp.lingfil.uu.se']

MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'swegram_main/uploads')

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': "swegram",
        'USER': 'jena0545',
	    'PASSWORD': 'secret',
        'HOST': "localhost",
        'PORT': "5432"
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
