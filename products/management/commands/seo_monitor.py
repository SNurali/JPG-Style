from django.core.management.base import BaseCommand
import requests
from django.conf import settings


class Command(BaseCommand):
    help = 'Check SEO parameters'

    def handle(self, *args, **options):
        urls_to_check = [
            '/',
            '/catalog/',
            # добавьте другие важные URL
        ]

        for url in urls_to_check:
            full_url = f"https://{settings.DOMAIN}{url}"
            self.stdout.write(f"\nChecking {full_url}")

            try:
                # Проверка ответа сервера
                response = requests.get(full_url)
                self.stdout.write(f"Status code: {response.status_code}")

                # Проверка заголовков
                self.stdout.write("Headers:")
                for header in ['content-type', 'x-robots-tag', 'link']:
                    self.stdout.write(f"{header}: {response.headers.get(header)}")

                # Проверка времени загрузки
                self.stdout.write(f"Load time: {response.elapsed.total_seconds()}s")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error checking {url}: {str(e)}"))