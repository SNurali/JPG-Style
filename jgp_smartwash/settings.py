from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-1234567890abcdefg'  # Используй .env в проде
DEBUG = True
ALLOWED_HOSTS = ['jpg-style.onrender.com', 'smartwash.onrender.com', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products',
    'sorl.thumbnail',
]

# Thumbnail aliases
THUMBNAIL_ALIASES = {
    '': {
        'carousel': {'size': (800, 400), 'crop': 'smart'},
        'product': {'size': (400, 200), 'crop': 'center'},
    },
}
THUMBNAIL_DEBUG = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'jgp_smartwash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'products', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jgp_smartwash.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Telegram bot
TELEGRAM_TOKEN = "7492480842:AAFcwTRve8yolNVvPb1OAkiustwIz35mZII"
TELEGRAM_CHAT_ID = "532350689"

# Убираем предупреждение UnorderedObjectListWarning
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # если много полей в формах

# Настройки для корзины
CART_SESSION_ID = 'cart'
CART_ITEM_MAX_QUANTITY = 10

# Автоматический git-коммит после collectstatic
if not DEBUG:
    import subprocess
    from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectstaticCommand


    class CustomCollectstaticCommand(CollectstaticCommand):
        def handle(self, **options):
            super().handle(**options)
            try:
                subprocess.run(['python', 'manage.py', 'git_track_static'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error updating Git: {e}")


    CollectstaticCommand = CustomCollectstaticCommand