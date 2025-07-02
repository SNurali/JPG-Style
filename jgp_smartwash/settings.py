from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-1234567890abcdefg'  # Используй .env в проде
DEBUG = True
ALLOWED_HOSTS = ['smartwash.uz', 'www.smartwash.uz', 'localhost', '127.0.0.1']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'products',
    'sorl.thumbnail',
    'django_ckeditor_5',
]

# Добавьте в settings.py (в раздел CKEDITOR_5_CONFIGS)

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': [
                    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
                    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
                    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
                    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
                    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
                    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
                ],
                'backgroundColors': [
                    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
                    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
                    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
                    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
                    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
                    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
                ]
            },
            'tableCellProperties': {
                'borderColors': [
                    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
                    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
                    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
                    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
                    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
                    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
                ],
                'backgroundColors': [
                    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
                    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
                    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
                    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
                    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
                    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
                ]
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

# Middleware with mobile detection
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',  # Mobile detection
]

# Cache backend
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    },
    'user_agent': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'user_agent_cache',
    }
}

ROOT_URLCONF = 'jgp_smartwash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '././public_html', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Добавленный процессор для избранного
                'products.context_processors.wishlist_processor',
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Telegram bot
TELEGRAM_TOKEN = "7492480842:AAFcwTRve8yolNVvPb1OAkiustwIz35mZII"
TELEGRAM_CHAT_ID = "532350689"

# Thumbnail aliases
THUMBNAIL_ALIASES = {
    '': {
        'carousel': {'size': (800, 400), 'crop': 'smart'},
        'product': {'size': (400, 200), 'crop': 'center'},
    },
}
THUMBNAIL_DEBUG = False

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

# Предзагрузка ключевых ресурсов
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTP/2 Server Push
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')