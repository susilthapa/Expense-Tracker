from .base import *


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = ['.herokuapp.com']


import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)