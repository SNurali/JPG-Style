from django.contrib.sitemaps import Sitemap
from .models import Product
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['home', 'catalog', 'contacts', 'cart']

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # добавьте это поле в модель

    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])