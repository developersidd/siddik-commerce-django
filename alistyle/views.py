from django.shortcuts import render
from django.utils import timezone

from carts.utils import get_cart_items, get_or_create_cart
from store.models import Campaign, FlashSale, FlashSaleCategory, Product


def home(request):
    now = timezone.now()
    start_time = None
    end_time = None
    # Flash Sale Products (only active)
    flash_sale_categories = (
        FlashSaleCategory.objects.filter(
            flash_sale__start_time__lte=now,
            flash_sale__end_time__gte=now,
            flash_sale__is_active=True,
        )
        .select_related("flash_sale")
        .order_by("flash_sale__start_time")
    )

    if flash_sale_categories.exists():
        flash_sale = flash_sale_categories.first().flash_sale
        start_time = flash_sale.start_time
        end_time = flash_sale.end_time
    else:
        flash_sale = None
    # get popular products
    popular_products = Product.objects.filter(is_active=True).order_by(
        "-view_count", "-purchase_count", "-cart_add_count"
    )[:8]

    # newly arrived products
    new_arrivals = Product.objects.filter(is_active=True).order_by("-created_at")[:8]

    # Active Campaigns
    #    active_campaigns = Campaign.objects.filter(
    #        start_date__lte=today, end_date__gte=today
    #    ).prefetch_related("products", "categories")
    #
    #    # Get products that have product-level discount
    #    discounted_products = Product.objects.filter(
    #        discount_percent__gt=0, discount_start__lte=today, discount_end__gte=today
    #    )
    #
    # cart = get_or_create_cart(request)
    # cart_items = get_cart_items(request.user, cart)
    # print("🐍 File: alistyle/views.py | Line: 50 | home ~ cart_items",cart_items)
    context = {
        "flash_sale": (
            {
                "categories": flash_sale_categories,
                "start_time": start_time,
                "end_time": end_time,
            }
            if flash_sale
            else None
        ),
        "popular_products": popular_products,
        "new_arrivals": new_arrivals,
        # "campaigns": active_campaigns,
        # "discounted_products": discounted_products,
    }

    return render(request, "home.html", context)
