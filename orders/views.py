from django.shortcuts import render

from carts.utils import get_cart_items, get_or_create_cart

# Create your views here.

def place_order(request, total=0):
    cart = get_or_create_cart(request)
    cart_items = get_cart_items(request.user, cart)
    if request.method == "POST":
        pass
    
    
    return render(request, 'orders/place_order.html', {
        'total': total,
        'cart_items': cart_items,
    })