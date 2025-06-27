# products/urls.py
from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import StaticViewSitemap, ProductSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap
}

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('contacts/', views.contacts, name='contacts'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

]