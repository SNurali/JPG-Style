from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from PIL import Image
import os
from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="URL-адрес категории"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name='products'
    )
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        verbose_name="Фото товара",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Рекомендуемый формат: WebP или JPEG. Размер: не более 800×800 пикселей."
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name="URL-адрес"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Генерирует URL для детального просмотра товара"""
        return reverse('product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Генерация slug перед сохранением
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            # Проверяем уникальность slug
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

        # Оптимизация изображения после сохранения
        self.optimize_image()

    def optimize_image(self):
        """Оптимизирует загруженное изображение"""
        if not self.image:
            return

        try:
            img_path = self.image.path

            if not os.path.exists(img_path):
                return

            with Image.open(img_path) as img:
                # Конвертируем в RGB если это PNG с прозрачностью
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

                # Изменяем размер, если больше 800x800
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, Image.LANCZOS)

                # Определяем формат для сохранения
                ext = os.path.splitext(img_path)[1].lower()
                if ext in ('.jpg', '.jpeg'):
                    format = 'JPEG'
                    quality = 85
                elif ext == '.webp':
                    format = 'WEBP'
                    quality = 85
                else:
                    format = img.format
                    quality = 95

                # Сохраняем с оптимизацией
                img.save(
                    img_path,
                    format=format,
                    quality=quality,
                    optimize=True
                )

        except Exception as e:
            print(f"Ошибка при обработке изображения {self.image.name}: {e}")

    @property
    def image_url(self):
        """Возвращает URL изображения или None если его нет"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
    @property
    def is_new(self):
        """Возвращает True, если товар добавлен менее 7 дней назад"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days < 7

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


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    def get_total_price(self):
        return self.price * self.quantity

User = get_user_model()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Один товар - один раз у пользователя
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'