from django.shortcuts import redirect
from carts.utils import get_cart_items, get_or_create_cart


def empty_cart_redirection(view_func):
    def wrapper_func(request, *args, **kwargs):
        cart = get_or_create_cart(request)
        cart_items = get_cart_items(request.user, cart)

        if len(cart_items) > 0:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("store")

    return wrapper_func
