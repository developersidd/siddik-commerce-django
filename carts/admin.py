from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "user_info", "items_count", "date_added")
    list_filter = ("date_added",)
    search_fields = ("cart_id",)
    readonly_fields = ("cart_id", "date_added")

    def user_info(self, obj):
        return obj.user.username if hasattr(obj, "user") and obj.user else "Guest"

    user_info.short_description = "User"

    def items_count(self, obj):
        # obj is the Cart instance
        # cartitem_set gets ALL CartItems objects related to this cart
        count = obj.cartitem_set.count()
        return format_html(
            "<strong>{}</strong> item{}", count, "s" if count != 1 else ""
        )

    items_count.short_description = "Items"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "cart",
        "quantity",
        "user_info",
        "get_variations",
        "status_badge",
    )
    list_filter = ("is_active", "cart__date_added")
    search_fields = ("product__product_name", "user__username", "cart__cart_id")
    raw_id_fields = ("product", "cart", "user")

    def get_variations(self, obj):
        variations = obj.variations.all()
        if not variations:
            return "-"
        return format_html(
            "<br>".join(
                [
                    f"<span style='background: #e3f2fd; padding: 2px 6px; border-radius: 3px; margin: 2px;color:gray;'>"
                    f"{var.variation_category}: {var.variation_value}</span>"
                    for var in variations
                ]
            )
        )

    get_variations.short_description = "Variations"

    def user_info(self, obj):
        return obj.user.username if obj.user else "Guest"

    user_info.short_description = "User"

    def status_badge(self, obj):
        color = "green" if obj.is_active else "gray"
        status = "Active" if obj.is_active else "Inactive"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            status,
        )

    status_badge.short_description = "Status"
