import json
import logging
import math
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_countries import countries
from alistyle.utils import get_session_key
from carts.decorators import empty_cart_redirection
from carts.models import Cart, CartItem
from carts.utils import (
    cart_item_exist,
    create_new_cart_item,
    extract_product_variations,
    get_cart_items,
    get_or_create_cart,
    handle_existing_cart_item,
)
from coupon.models import Coupon, CouponUsage
from orders.models import Order
from store.models import Product


# Get Cart details
def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    coupon_discount_amount = 0
    try:
        current_user = request.user
        cart = get_or_create_cart(request)
        cart_items = get_cart_items(current_user, cart)
        coupon_usage_id = request.session.get("coupon_usage_id")
        coupon_usage = None
        for item in cart_items:
            total += item.product.final_price() * item.quantity
            quantity += item.quantity
        tax = math.ceil((2 * total) / 100)
        grand_total = total + tax
        if current_user.is_authenticated:
            if coupon_usage_id:
                coupon_usage = (
                    CouponUsage.objects.filter(user=current_user, id=coupon_usage_id)
                    .order_by("-used_at")
                    .first()
                )
                coupon_discount_amount = coupon_usage.discount_amount
        if coupon_usage and coupon_discount_amount < total:
            grand_total -= coupon_discount_amount

    except Exception as e:
        print("🐍 File: carts/views.py | Line: 48 | cart ~ e", e)
        # logging.log("Error occurred while getting cart details")
        pass
    context = {
        "total": total,
        "cart_items": cart_items,
        "grand_total": total + tax,
        "quantity": quantity,
        "discount": coupon_discount_amount,
        "applied_coupon_code": (
            coupon_usage.coupon.coupon_code if coupon_usage is not None else ""
        ),
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, "store/cart.html", context)


# add to cart
def add_to_cart(request, product_id):
    current_path = request.META.get("HTTP_REFERER")
    try:
        
        product = Product.objects.get(pk=product_id)
        current_user = request.user
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get("quantity", 1))
        print("🐍 File: carts/views.py | Line: 79 | add_to_cart ~ quantity", quantity)
        # get the product's default variations if no variations selected
        first_color = product.variations.filter(
            variation_category__iexact="color"
        ).first()
        first_size = product.variations.filter(
            variation_category__iexact="size"
        ).first()
        if first_color and first_size:
            default_variations = tuple(sorted([first_color.id, first_size.id]))
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
        return redirect(current_path)
    except Exception as e:
        logging.error(f"There was an error occurred while adding product to cart: {e}")
        return redirect(current_path)


# Decrease Cart Item quantity
def decrease_cart_item(request, product_id, cart_item_id):
    try:
        product = Product.objects.get(id=product_id)
        print(
            "🐍 File: carts/views.py | Line: 122 | decrease_cart_item ~ product",
            product,
        )
        cart_item = CartItem.objects.get(id=cart_item_id, product=product)
        print(
            "🐍 File: carts/views.py | Line: 124 | decrease_cart_item ~ cart_item",
            cart_item,
        )
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect("cart")
    except Exception as e:
        print("🐍 File: carts/views.py | Line: 132 | decrease_cart_item ~ e", e)
        logging.log("Error occurred while decresing cart quantity")
        return redirect("home")


# Remove Cart Item
def remove_cart_item(request, product_id, cart_item_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(pk=cart_item_id, product=product)
        cart_item.delete()
        return redirect("cart")
    except Exception as e:
        logging.error(
            f"There was an error occurred while deleting cart item with Id: {cart_item_id}"
        )
        return None


# Checkout
@empty_cart_redirection
def checkout(request):
    try:
        current_user = request.user
        cart = get_or_create_cart(request)
        cart_items = get_cart_items(current_user, cart)
        user_profile = None
        if request.user.is_authenticated:
            user_profile = current_user.user_profile
        context = {"cart_items": cart_items, "user_profile": user_profile}
        return render(request, "store/checkout.html", context)
    except Exception as e:
        print("🐍 File: carts/views.py | Line: 165 | checkout ~ e", e)
