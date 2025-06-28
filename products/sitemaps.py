# products/sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import Product

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'catalog', 'contacts']

    def location(self, item):
        from django.urls import reverse
        return reverse(item)

class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.all()

    def location(self, item):
        return reverse('product_detail', args=[str(item.slug)])