from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Order, OrderItem
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from telegram import Bot
from telegram.error import TelegramError

TELEGRAM_TOKEN = "7492480842:AAFcwTRve8yolNVvPb1OAkiustwIz35mZII"
TELEGRAM_CHAT_ID = "532350689"

def send_order_to_telegram(order):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    message = f"📦 Новый заказ #{order.id}\n\n"
    message += f"👤 Клиент: {order.customer_name}\n"
    message += f"📞 Телефон: {order.phone}\n"
    message += f"📍 Адрес: {order.address}\n"
    message += "🛒 Товары:\n"

    for item in order.items.all():
        message += f"• {item.product.name} — {item.quantity} шт. × {item.price} сум\n"

    message += f"\n💰 Итого: {order.total_price} сум"

    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
    except TelegramError as e:
        print("Ошибка Telegram:", e)

# Главная страница с пагинацией и слайдером
def home(request):
    all_products = Product.objects.all().order_by('-id')
    slider_products = all_products[:6]

    products_list = all_products
    page = request.GET.get('page', 1)

    paginator = Paginator(products_list, 6)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/home.html', {
        'products': products,
        'slider_products': slider_products,
        'has_products': products_list.exists(),
        'is_paginated': paginator.num_pages > 1
    })


# Каталог товаров
def catalog(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')

    # Приводим к int, если возможно
    selected_category_id = None
    if selected_category and selected_category.isdigit():
        selected_category_id = int(selected_category)

    if selected_category_id:
        products_list = Product.objects.filter(category_id=selected_category_id).order_by('-id')
    else:
        products_list = Product.objects.all().order_by('-id')

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

    for product_id, qty in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            products_in_cart.append({
                'product': product,
                'quantity': qty,
                'total': product.price * qty
            })
            total += product.price * qty
        except Product.DoesNotExist:
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

    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"{product.name} добавлен в корзину")
    return redirect('product_detail', pk=product_id)


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

    products_in_cart = []
    total = 0

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            products_in_cart.append({
                'product': product,
                'quantity': qty,
                'total': product.price * qty
            })
            total += product.price * qty
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        order = Order.objects.create(
            customer_name=name,
            phone=phone,
            address=address,
            total_price=total
        )

        for item in products_in_cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        # Очистка корзины
        request.session['cart'] = {}

        # Отправка в Telegram
        send_order_to_telegram(order)

        messages.success(request, "Спасибо за заказ!")
        return redirect('home')

    return render(request, 'products/checkout.html', {
        'cart_items': products_in_cart,
        'total': total
    })


# Страница контактов
def contacts(request):
    return render(request, 'products/contacts.html')