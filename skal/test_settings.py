from skal.settings import *

SECRET_KEY = 'test-secret-key-only-for-testing'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Faster password hashing in tests
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

MEDIA_ROOT = '/tmp/skal_test_media/'
