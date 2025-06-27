# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Order
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    products = Product.objects.all()[:6]
    return render(request, 'products/home.html', {
        'products': products,
        'has_products': products.exists()
    })


def catalog(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')

    # Приводим к int, если возможно
    selected_category_id = None
    if selected_category and selected_category.isdigit():
        selected_category_id = int(selected_category)

    if selected_category_id:
        products_list = Product.objects.filter(category_id=selected_category_id)
    else:
        products_list = Product.objects.all()

    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'products/catalog.html', {
        'categories': categories,
        'products': products,
        'selected_category': selected_category_id,
        'has_products': products_list.exists()
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.exclude(pk=pk).order_by('?')[:3]  # случайные товары
    return render(request, 'products/product_detail.html', {'product': product, 'related_products': related_products})

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
            continue  # пропускаем удаленные товары

    return render(request, 'products/cart.html', {
        'cart_items': products_in_cart,
        'total': total,
        'cart_empty': len(products_in_cart) == 0
    })

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

def checkout(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, "Ваша корзина пуста.")
            return redirect('cart')

        total = 0
        valid_cart = {}

        for product_id, qty in cart.items():
            try:
                product = Product.objects.get(pk=product_id)
                total += product.price * qty
                valid_cart[product_id] = qty
            except Product.DoesNotExist:
                continue

        if not valid_cart:
            messages.warning(request, "Все товары в вашей корзине были удалены.")
            return redirect('cart')

        Order.objects.create(
            customer_name=name,
            phone=phone,
            address=address,
            total_price=total
        )

        request.session['cart'] = {}
        messages.success(request, "Спасибо за заказ! Мы свяжемся с вами в ближайшее время.")
        return redirect('home')

    return render(request, 'products/checkout.html')

def contacts(request):
    return render(request, 'products/contacts.html')