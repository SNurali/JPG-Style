from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from PIL import Image
import os

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Фото товара",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Рекомендуемый формат: WebP или JPEG. Размер: не более 800×800 пикселей."
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, default='')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Генерация slug, если его нет
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.id}")

        # Сохраняем объект, чтобы убедиться, что файл загружен
        super().save(*args, **kwargs)

        # Если изображение загружено — оптимизируем его
        if self.image:
            img_path = self.image.path
            if os.path.exists(img_path):
                try:
                    with Image.open(img_path) as img:
                        # Изменяем размер, если больше 800x800
                        if img.height > 800 or img.width > 800:
                            output_size = (800, 800)
                            img.thumbnail(output_size)

                        # Сохраняем с оптимизацией и качеством
                        img.save(img_path, optimize=True, quality=85, format=img.format)
                except Exception as e:
                    print(f"Ошибка при обработке изображения: {e}")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-price']  # или ['name'], как тебе удобнее


# products/models.py

from django.db import models

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        default="new",
        choices=[
            ('new', 'Новый'),
            ('processing', 'В обработке'),
            ('completed', 'Завершён'),
            ('cancelled', 'Отменён')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.customer_name}"


# products/models.py

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"