from django.contrib import admin
from .models import Product, Category, Order, OrderItem


# Inline для отображения товаров в заказе
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False
    verbose_name = "Товар"
    verbose_name_plural = "Товары в заказе"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'phone', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer_name', 'phone', 'address')
    inlines = [OrderItemInline]
    readonly_fields = ('total_price', 'created_at')


# Модель товара
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

    # Проверяем наличие поля slug перед использованием prepopulated_fields
    def get_prepopulated_fields(self, request, obj=None):
        try:
            if 'slug' in [f.name for f in Product._meta.fields]:
                return {'slug': ('name',)}
            return {}
        except Exception:
            return {}

    prepopulated_fields = {}  # Используем безопасное значение по умолчанию


# Категории
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def get_prepopulated_fields(self, request, obj=None):
        try:
            if 'slug' in [f.name for f in Category._meta.fields]:
                return {'slug': ('name',)}
            return {}
        except Exception:
            return {}

    prepopulated_fields = {}  # Используем безопасное значение по умолчанию


# Товары в заказе
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_total')
    list_filter = ('order', 'product')

    def get_total(self, obj):
        return obj.quantity * obj.price

    get_total.short_description = 'Общая цена'