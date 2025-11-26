from calendar import c
import logging
import math
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from alistyle.utils import get_session_key
from carts.models import Cart, CartItem
from carts.utils import (
    cart_item_exist,
    create_new_cart_item,
    extract_product_variations,
    get_cart_items,
    get_or_create_cart,
    handle_existing_cart_item,
)
from store.models import Product


# Get Cart details
def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    session_key = get_session_key(request)
    try:
        current_user = request.user
        cart = get_or_create_cart(request)
        cart_items = get_cart_items(current_user, cart)
        total = sum(item.sub_total() for item in cart_items)
        quantity = sum(item.quantity for item in cart_items)
        tax = math.ceil((2 * total) / 100)
    except ObjectDoesNotExist:
        logging.log("Error occurred while getting cart details")
    context = {
        "total": total,
        "cart_items": cart_items,
        "grand_total": total + tax,
        "quantity": quantity,
        "tax": tax,
    }
    return redirect("home")


# add to cart
def add_to_cart(request, product_id):
    current_path = request.META.get("HTTP_REFERER")
    # raise Exception("Test exception for logging")
    try:
        # throw a test exception
        product = Product.objects.get(pk=product_id)
        current_user = request.user
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get("quantity", 1))
        # get the product's default variations if no variations selected
        first_color = product.variations.filter(
            variation_category__iexact="color"
        ).first()
        first_size = product.variations.filter(
            variation_category__iexact="size"
        ).first()
        if first_color and first_size:
            default_variations = tuple([first_color.id, first_size.id])
        else:
            default_variations = tuple()
        # extract selected variations from the request if any
        current_variations = extract_product_variations(request, product)
        if not current_variations:
            current_variations = default_variations
        if cart_item_exist(product, current_user, cart):
            handle_existing_cart_item(
                product, current_user, cart, current_variations, quantity
            )
        else:
            create_new_cart_item(
                product, current_user, cart, current_variations, quantity
            )
        messages.success(request, f"{product.product_name} added to cart successfully!")
        # check if it's an ajax request
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            print(" --------> AJAX request detected")
            return JsonResponse(
                {"message": f"{product.product_name} added to cart successfully!"},
                status=200,
            )
        # return redirect("cart")
        return redirect(current_path)
    except Exception as e:
        logging.error(f"There was an error occurred while adding product to cart: {e}")
        return redirect(current_path)


# Decrease Cart Item quantity
def decrease_cart_item(request, product_id, cart_item_id):
    try:
        product = Product.objects.get(id=product_id)
        cart_item = CartItem.objects.get(id=cart_item_id, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            return redirect("home")
    except Exception as e:
        logging.log("Error occurred while decresing cart quantity")


# Remove Cart Item
def remove_cart_item(request, product_id, cart_item_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(pk=cart_item_id, product=product)
        cart_item.delete()
        return redirect("home")
    except Exception as e:
        logging.error(
            f"There was an error occurred while deleting cart item with Id: {cart_item_id}"
        )
        return None
