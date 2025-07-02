# products/management/commands/update_slugs.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Product

class Command(BaseCommand):
    help = 'Обновляет slug для всех продуктов'

    def handle(self, *args, **options):
        count = 0
        for product in Product.objects.all():
            if not product.slug:
                product.slug = slugify(f"{product.name}-{product.id}")
                product.save(update_fields=['slug'])
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Обновлено {count} slug\'ов'))