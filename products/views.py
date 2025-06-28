from django.shortcuts import render, get_object_or_404, redirect
from django.db import models  # Добавлен импорт models
from .models import Product, Category, Order, OrderItem
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
import requests
from django.templatetags.static import static
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Category, Order, OrderItem, Wishlist


# Настройка логгера
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "7492480842:AAFcwTRve8yolNVvPb1OAkiustwIz35mZII"
TELEGRAM_CHAT_ID = "532350689"


def send_order_to_telegram(order):
    try:
        message = f"🛒 Новый заказ #{order.id}\n\n"
        message += f"👤 Имя: {order.customer_name}\n"
        message += f"📞 Телефон: {order.phone}\n"
        message += f"🏠 Адрес: {order.address}\n\n"
        message += "📦 Состав заказа:\n"

        for item in order.items.all():
            message += f"• {item.product.name} - {item.quantity} × {item.price} = {item.quantity * item.price} сум\n"

        message += f"\n💰 Итого: {order.total_price} сум"

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {str(e)}")


# Главная страница с пагинацией и слайдером
def home(request):
    all_products = Product.objects.all().order_by('-id')
    slider_products = all_products[:6]

    paginator = Paginator(all_products, 6)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/home.html', {
        'products': products,
        'slider_products': slider_products,
        'has_products': all_products.exists(),
        'is_paginated': paginator.num_pages > 1
    })


# Каталог товаров
def catalog(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()

    # Основной запрос товаров
    products_list = Product.objects.all().order_by('-created_at')  # Убрали select_related для простоты

    # Фильтрация по категории если выбрана
    if selected_category:
        products_list = products_list.filter(category__slug=selected_category)

    # Поиск по названию или описанию
    if search_query:
        products_list = products_list.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )

    # Пагинация
    paginator = Paginator(products_list, 9)  # 9 товаров на странице
    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'search_query': search_query,
    }

    return render(request, 'products/catalog.html', context)

# Детали товара
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(slug=slug).order_by('?')[:3]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'og_title': product.name,
        'og_description': product.description[:200] + '...' if len(product.description) > 200 else product.description,
        'og_image': request.build_absolute_uri(product.image.url) if product.image else request.build_absolute_uri(
            static('img/og-image.jpg')),
    })


# Корзина
def cart(request):
    cart_items = request.session.get('cart', {})
    products_in_cart = []
    total = 0

    for product_slug, quantity in cart_items.items():
        try:
            product = Product.objects.get(slug=product_slug)
            item_total = product.price * quantity
            products_in_cart.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            # Если товар не найден, удаляем его из корзины
            del request.session['cart'][product_slug]
            request.session.modified = True
            continue

    return render(request, 'products/cart.html', {
        'cart_items': products_in_cart,
        'cart_total': total,
        'cart_empty': len(products_in_cart) == 0
    })


# Добавление в корзину
def add_to_cart(request, slug):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Некорректное количество")
            return redirect('product_detail', slug=slug)

        if quantity < 1 or quantity > 10:
            messages.error(request, "Количество должно быть от 1 до 10")
            return redirect('product_detail', slug=slug)
    else:
        quantity = 1

    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        messages.error(request, "Такого товара нет в наличии.")
        return redirect('home')

    cart = request.session.get('cart', {})

    if slug in cart:
        cart[slug] += quantity
    else:
        cart[slug] = quantity

    request.session['cart'] = cart
    messages.success(request, f"{product.name} добавлен в корзину (теперь: {cart[slug]} шт.)")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

def update_cart(request, slug):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Некорректное количество")
            return redirect('cart')

        cart = request.session.get('cart', {})

        if slug in cart:
            if quantity > 0:
                cart[slug] = quantity
                messages.success(request, 'Количество товара обновлено!')
            else:
                del cart[slug]
                messages.success(request, 'Товар удален из корзины!')

            request.session['cart'] = cart
        else:
            messages.error(request, 'Товар не найден в корзине.')

    return redirect('cart')


def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        messages.success(request, 'Корзина успешно очищена!')
    return redirect('cart')

# Удаление из корзины
def remove_from_cart(request, slug):
    cart = request.session.get('cart', {})

    if slug in cart:
        del cart[slug]
        request.session['cart'] = cart
        messages.success(request, "Товар удален из корзины")

    return redirect('cart')


# Оформление заказа
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Ваша корзина пуста")
        return redirect('home')

    # Подготовка данных о товарах в корзине
    products_in_cart = []
    total = 0

    for product_slug, qty in cart.items():
        try:
            product = Product.objects.get(slug=product_slug)
            item_total = product.price * qty
            products_in_cart.append({
                'product': product,
                'quantity': qty,
                'total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            messages.error(request, f"Товар {product_slug} не найден")
            continue

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # Валидация данных
        if not name:
            messages.error(request, "Пожалуйста, укажите ваше имя")
            return redirect('checkout')
        if not phone:
            messages.error(request, "Пожалуйста, укажите телефон")
            return redirect('checkout')
        if not address:
            messages.error(request, "Пожалуйста, укажите адрес")
            return redirect('checkout')

        try:
            # Создаем заказ
            order = Order.objects.create(
                customer_name=name,
                phone=phone,
                address=address,
                total_price=total,
                status='new'
            )

            # Создаем позиции заказа
            for item in products_in_cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )

            # Очищаем корзину
            request.session['cart'] = {}

            # Отправляем уведомление в Telegram
            send_order_to_telegram(order)

            messages.success(request, "Ваш заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.")
            return redirect('order_success', order_id=order.id)

        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {str(e)}")
            messages.error(request, "Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.")
            return redirect('checkout')

    return render(request, 'products/checkout.html', {
        'cart_items': products_in_cart,
        'total': total
    })

def order_success(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return render(request, 'products/order_success.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, "Заказ не найден")
        return redirect('home')


@login_required
def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    if created:
        return JsonResponse({'status': 'added'})
    return JsonResponse({'status': 'already_exists'})

@login_required
def remove_from_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()
    return JsonResponse({'status': 'removed'})

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})

# Страница контактов
def contacts(request):
    return render(request, 'products/contacts.html')