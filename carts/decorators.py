from functools import wraps
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from carts.utils import get_cart_items, get_or_create_cart


def empty_cart_redirection(view_func):
    @wraps(view_func)
    @csrf_exempt
    def wrapper_func(request, *args, **kwargs):
        cart = get_or_create_cart(request)
        cart_items = get_cart_items(request.user, cart)

        if len(cart_items) > 0:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("store")

    return wrapper_func
