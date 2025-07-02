from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import StaticViewSitemap, ProductSitemap, AutoChemistrySitemap
from django.conf import settings
from django.conf.urls.static import static

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'autochemistry': AutoChemistrySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),  # ваше приложение
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),  # <--- sitemap ЗДЕСЬ!
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
