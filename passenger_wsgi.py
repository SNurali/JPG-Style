import sys
import os

# Добавляем путь к проекту
sys.path.append('/home/smartwa2/jpg_style')

# Устанавливаем переменную окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jgp_smartwash.settings')

# Загружаем WSGI-приложение Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()