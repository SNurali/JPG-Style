# products/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product, AutoChemistryPost

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

class AutoChemistrySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return AutoChemistryPost.objects.filter(is_published=True)

    def location(self, item):
        return reverse('autochemistry_detail', args=[str(item.slug)])