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
from .models import Product, Category, Order, OrderItem, Wishlist, AutoChemistryPost
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from django.utils.encoding import smart_str
from django.http import HttpResponse
from .utils import get_usd_to_uzs_rate
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET
from decimal import Decimal

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


def yml_feed(request):
    rate = Decimal(str(get_usd_to_uzs_rate()))  # Конвертируем float в Decimal

    yml_catalog = Element('yml_catalog', date=timezone.now().strftime("%Y-%m-%d %H:%M"))
    shop = SubElement(yml_catalog, 'shop')
    SubElement(shop, 'name').text = 'SmartWash'

    currencies = SubElement(shop, 'currencies')
    SubElement(currencies, 'currency', id='USD', rate='1')

    offers = SubElement(shop, 'offers')

    for product in Product.objects.all():
        try:
            price_usd = (product.price / rate).quantize(Decimal('0.00'))  # Деление Decimal на Decimal
        except (TypeError, ZeroDivisionError) as e:
            print(f"Ошибка расчета цены для товара {product.id}: {e}")
            continue  # Пропускаем товар с ошибкой

        offer = SubElement(offers, 'offer', id=str(product.id), available='true')
        SubElement(offer, 'name').text = product.name
        SubElement(offer, 'price').text = str(price_usd)
        SubElement(offer, 'currencyId').text = 'USD'
        SubElement(offer, 'categoryId').text = str(product.category.id if product.category else 1)
        SubElement(offer, 'url').text = f'https://smartwash.uz/product/{product.slug}'
        SubElement(offer, 'picture').text = request.build_absolute_uri(product.image.url) if product.image else ''

    xml_string = tostring(yml_catalog, encoding='utf-8')
    return HttpResponse(xml_string, content_type='application/xml')



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


def add_to_cart(request, slug):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': "Некорректное количество"}, status=400)
            messages.error(request, "Некорректное количество")
            return redirect('product_detail', slug=slug)

        if quantity < 1 or quantity > 10:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': "Количество должно быть от 1 до 10"}, status=400)
            messages.error(request, "Количество должно быть от 1 до 10")
            return redirect('product_detail', slug=slug)

        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': "Товар не найден"}, status=404)
            messages.error(request, "Такого товара нет в наличии.")
            return redirect('home')

        cart = request.session.get('cart', {})

        if slug in cart:
            cart[slug] += quantity
        else:
            cart[slug] = quantity

        request.session['cart'] = cart

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"{product.name} добавлен в корзину (теперь: {cart[slug]} шт.)",
                'count': sum(cart.values())
            })

        messages.success(request, f"{product.name} добавлен в корзину (теперь: {cart[slug]} шт.)")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    return JsonResponse({'success': False, 'message': "Метод не разрешён"}, status=405)

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

def send_message_to_telegram(text):
    """Отправляет текстовое сообщение в Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML' # Используем HTML для форматирования
        }
        # Добавим таймаут для лучшей устойчивости
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status() # Проверка на ошибки HTTP
        logger.info(f"Сообщение успешно отправлено в Telegram: {text[:50]}...")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при отправке в Telegram: {e}")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
    return False

# Страница контактов
def contacts(request):
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Простая валидация (имя и сообщение обязательны)
        if not name or not message_text:
             messages.error(request, "Пожалуйста, заполните обязательные поля (Имя, Сообщение).")
             return render(request, 'products/contacts.html')

        # Формируем сообщение для Telegram
        telegram_message = (
            f"📬 <b>Новое сообщение из формы контактов</b>\n\n"
            f"<b>Имя:</b> {name}\n"
        )
        if phone:
            telegram_message += f"<b>Телефон:</b> {phone}\n"
        if email:
            telegram_message += f"<b>Email:</b> {email}\n"
        telegram_message += f"<b>Сообщение:</b>\n{message_text}"

        # Отправляем сообщение
        if send_message_to_telegram(telegram_message):
            messages.success(request, "Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.")
        else:
             messages.error(request, "К сожалению, произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже или свяжитесь с нами другим способом.")

        # Перенаправляем, чтобы избежать повторной отправки при обновлении страницы
        return redirect('contacts')

    # Если GET-запрос, просто отображаем страницу
    return render(request, 'products/contacts.html')


def autochemistry_list(request):
    posts = AutoChemistryPost.objects.filter(is_published=True).order_by('-created_at')

    # Пагинация
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'products/autochemistry_list.html', {
        'posts': posts,
        'page_title': 'Мир автохимии - полезные статьи и видео'
    })


def autochemistry_detail(request, slug):
    post = get_object_or_404(AutoChemistryPost, slug=slug, is_published=True)

    # Увеличиваем счетчик просмотров
    post.views += 1
    post.save()

    # Получаем похожие посты
    similar_posts = AutoChemistryPost.objects.filter(
        is_published=True
    ).exclude(
        id=post.id
    ).order_by('-created_at')[:3]

    return render(request, 'products/autochemistry_detail.html', {
        'post': post,
        'similar_posts': similar_posts,
        'youtube_id': post.get_youtube_id(),
        'page_title': post.title
    })