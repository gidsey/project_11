import dj_database_url
from ..settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    '.pythonanywhere.com',
    '127.0.0.1',
    ]

SECRET_KEY = get_env_variable("SECRET_KEY")

db_from_env = dj_database_url.config()
DATABASES["default"].update(db_from_env)