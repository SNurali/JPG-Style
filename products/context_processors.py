from .models import Wishlist


def wishlist_processor(request):
    """
    Добавляет в контекст шаблонов:
    - user_wishlist: список slug'ов избранных товаров текущего пользователя
    - wishlist_count: количество избранных товаров
    """
    context = {
        'user_wishlist': [],
        'wishlist_count': 0
    }

    if request.user.is_authenticated:
        wishlist_slugs = Wishlist.objects.filter(user=request.user) \
            .values_list('product__slug', flat=True)
        context['user_wishlist'] = list(wishlist_slugs)
        context['wishlist_count'] = len(context['user_wishlist'])

    return context