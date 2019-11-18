from .base import *
from .docker import *


DEBUG = True

ALLOWED_HOSTS.append('127.0.0.1')

MEDIA_ROOT = os.path.join(BASE_DIR, "../media/")
STATIC_ROOT = os.path.join(BASE_DIR, "../staticfiles/")
