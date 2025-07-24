from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Product, AutoChemistryPost

class StaticViewSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return ['home', 'catalog', 'contacts']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Принудительно возвращаем одинаковую дату обновления для всех статических страниц
        return timezone.now()

class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.all()

    def location(self, item):
        return reverse('product_detail', args=[item.slug])

    def lastmod(self, item):
        return item.updated_at if item.updated_at else item.created_at or timezone.now()

class AutoChemistrySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return AutoChemistryPost.objects.filter(is_published=True)

    def location(self, item):
        return reverse('autochemistry_detail', args=[item.slug])

    def lastmod(self, item):
        return item.updated_at if item.updated_at else item.created_at or timezone.now()
