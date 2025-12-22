from django.core.exceptions import ObjectDoesNotExist
from carts.utils import get_cart_items, get_or_create_cart


def counter(request):
    if "admin" in request.path:
        return {}

    else:
        cart_count = 0
        try:
            cart = get_or_create_cart(request)
            cart_items = get_cart_items(request.user, cart)
            cart_count = len(cart_items)

        except ObjectDoesNotExist:
            cart_count = 0
        return dict(cart_count=cart_count)
