from math import prod
from venv import logger

from django.shortcuts import redirect
from alistyle.utils import get_session_key
from carts.models import Cart, CartItem
from store.models import Variation


# Get Current Product Variations
def extract_product_variations(request, product):
    variations = []
    if request.method == "POST":
        variation_keys = ["color", "size"]

        for key, value in request.POST.items():
            if key not in variation_keys:
                continue
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                variations.append(variation)
            except Variation.DoesNotExist:
                continue

    return tuple(sorted(v.id for v in variations))


# Create or get cart
def get_or_create_cart(request):
    cart, created = Cart.objects.get_or_create(cart_id=get_session_key(request))
    print(
        "🐍 File: carts/utils.py | Line: 36 | get_or_create_cart ~ get_session_key(request)",
        get_session_key(request),
    )
    return cart


# Get cart items
def get_cart_items(user, cart):
    print("🐍 File: carts/utils.py | Line: 41 | undefined ~ cart", cart)
    print("🐍 File: carts/utils.py | Line: 41 | get_cart_items ~ user", user)

    if user.is_authenticated:
        cart_items = CartItem.objects.filter(user=user)
        print(
            "🐍 File: carts/utils.py | Line: 43 | get_cart_items ~ cart_items",
            cart_items,
        )
    else:
        cart_items = CartItem.objects.filter(cart=cart)
    return cart_items


# Cart Item Exist
def cart_item_exist(product, user, cart):
    if user.is_authenticated:
        return CartItem.objects.filter(product=product, user=user).exists()
    else:
        return CartItem.objects.filter(product=product, cart=cart).exists()


# get existed product variation map
def get_variation_map(cart_items):
    variation_map = {}
    for item in cart_items:
        variation_ids = sorted(
            item.variations.values_list("id", flat=True)
        )  # values_list returns a QuerySet of variation ids using flat=True to get a flat list

        variation_map[tuple(variation_ids)] = item.id
    return variation_map


# create new cart item
def create_new_cart_item(product, user, cart, variations, quantity=1):
    user_value = user if user.is_authenticated else None

    cart_item = CartItem.objects.create(
        product=product, user=user_value, cart=cart, quantity=quantity
    )
    if variations:
        cart_item.variations.set(variations)
    cart_item.save()
    logger.info(f"Created new cart item for product {product.id}")
    # return redirect("home")


# Check if product in cart item exist otherwise create new cart item
def handle_existing_cart_item(product, user, cart, current_variations, quantity=1):
    print(
        "🐍 File: carts/utils.py | Line: 94 | undefined ~ current_variations",
        current_variations,
    )

    cart_items = get_cart_items(user, cart)
    variation_map = get_variation_map(cart_items)
    if current_variations:
        if current_variations in variation_map:
            item_id = variation_map[current_variations]
            cart_item = CartItem.objects.get(id=item_id)
    elif not current_variations:
        user = user if user.is_authenticated else None
        cart_item = CartItem.objects.get(product=product, user=user)
    if cart_item:
        cart_item.quantity += quantity
        cart_item.save()
        print(
            f"!!Increment quantity for cart item",
            "cart_item",
            cart_item,
            "product",
            product,
        )
    # return redirect("home")
    else:
        create_new_cart_item(product, user, cart, current_variations, quantity)

        logger.info(f"Created new cart item for product {product.id}")


def handle_existing_cart_items(new_cart_items, user):
    # print(
    #    "🐍 File: carts/utils.py | Line: 120 | undefined ~ new_cart_items",
    #    new_cart_items,
    # )
    old_cart_items = CartItem.objects.filter(user=user)

    old_variations = get_variation_map(old_cart_items)
    # print(
    #    "🐍 File: carts/utils.py | Line: 122 | handle_existing_cart_items ~ old_variations",
    #    old_variations,
    # )
    if new_cart_items.exists():
        for item in new_cart_items:
            product_variation = tuple(
                sorted(item.variations.values_list("id", flat=True))
            )
            if product_variation:
                if product_variation in old_variations:
                    item_id = old_variations [product_variation]
                    cart_item = CartItem.objects.get(id=item_id)
            elif not product_variation:
                cart_item = CartItem.objects.get(product=item.product, user=user)
            if cart_item:
                cart_item.user = user
                cart_item.quantity += item.quantity
                cart_item.save()
                item.delete()
            else:
                print("!!asssigning user")
                item.user = user
                item.save()
