from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Order, OrderItem
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
import requests

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

    try:
        selected_category_id = int(selected_category) if selected_category and selected_category.isdigit() else None
    except ValueError:
        selected_category_id = None

    products_list = Product.objects.filter(category_id=selected_category_id).order_by(
        '-id') if selected_category_id else Product.objects.all().order_by('-id')

    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/catalog.html', {
        'categories': categories,
        'products': products,
        'selected_category': selected_category_id,
        'has_products': products_list.exists()
    })


# Детали товара
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.exclude(pk=pk).order_by('?')[:3]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


# Корзина
def cart(request):
    cart_items = request.session.get('cart', {})
    products_in_cart = []
    total = 0

    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            products_in_cart.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            # Если товар не найден, удаляем его из корзины
            del request.session['cart'][product_id]
            request.session.modified = True
            continue

    return render(request, 'products/cart.html', {
        'cart_items': products_in_cart,
        'total': total,
        'cart_empty': len(products_in_cart) == 0
    })


# Добавление в корзину
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Такого товара нет в наличии.")
        return redirect('home')

    # Получаем текущую корзину из сессии
    cart = request.session.get('cart', {})

    # Преобразуем product_id в строку (для JSON-сериализации)
    product_id_str = str(product_id)

    # Увеличиваем количество товара, если он уже есть в корзине
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1  # Иначе добавляем товар с количеством 1

    # Сохраняем обновленную корзину в сессии
    request.session['cart'] = cart
    messages.success(request, f"{product.name} добавлен в корзину (теперь: {cart[product_id_str]} шт.)")

    # Возвращаем на предыдущую страницу или на страницу товара
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('product_detail', pk=product_id)


def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Некорректное количество")
            return redirect('cart')

        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            if quantity > 0:
                cart[product_id_str] = quantity
                messages.success(request, 'Количество товара обновлено!')
            else:
                del cart[product_id_str]
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
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
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

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * qty
            products_in_cart.append({
                'product': product,
                'quantity': qty,
                'total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            messages.error(request, f"Товар с ID {product_id} не найден")
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

# Страница контактов
def contacts(request):
    return render(request, 'products/contacts.html')