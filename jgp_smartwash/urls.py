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
    path('ckeditor5/', include('django_ckeditor_5.urls')),  # ✅ добавлено
    path('', include('products.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
