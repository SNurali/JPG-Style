from django.contrib import admin
from django import forms
from .models import Product, Category, Order, OrderItem, AutoChemistryPost
from django_ckeditor_5.widgets import CKEditor5Widget

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


class AutoChemistryPostAdminForm(forms.ModelForm):
    class Meta:
        model = AutoChemistryPost
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name='extends'
            ),
        }


@admin.register(AutoChemistryPost)
class AutoChemistryPostAdmin(admin.ModelAdmin):
    form = AutoChemistryPostAdminForm
    list_display = ('title', 'post_type', 'is_published', 'created_at', 'views')
    list_filter = ('post_type', 'is_published')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'post_type', 'is_published')
        }),
        ('Контент', {
            'fields': ('youtube_url', 'image', 'content')
        }),
        ('Статистика', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )