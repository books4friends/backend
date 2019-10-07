from project.settings.base import *

ALLOWED_HOSTS = ['backend']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'NAME': os.getenv('POSTGRES_DB'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "../staticfiles/")
MEDIA_ROOT = os.path.join(BASE_DIR, "../media/")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

BROKER_URL = 'redis://redis:6379/0'
RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

CONSTANCE_REDIS_CONNECTION = {
    'host': 'redis',
    'port': 6379,
    'db': 0,
}
