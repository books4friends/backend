from project.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vk_books',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
STATIC_ROOT = os.path.join(BASE_DIR, "../staticfiles/")
MEDIA_ROOT = os.path.join(BASE_DIR, "../media/")