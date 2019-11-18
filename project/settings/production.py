from .base import *
from .docker import *

DEBUG = False

STATIC_ROOT = os.path.join(BASE_DIR, "../staticfiles/")
MEDIA_ROOT = os.path.join(BASE_DIR, "../media/")
