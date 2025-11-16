from django.contrib import admin

from carts.models import Cart, CartItem


# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "date_added")
    list_filter = ("date_added",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    def get_variations(self, obj: CartItem):
        # obj is the CartItem instance
        # self is the CartItemAdmin instance
        return ", ".join(
            [
                f"{var.variation_category}: {var.variation_value}"
                for var in obj.variations.all()
            ]
        )

    get_variations.short_description = "Variations"

    list_display = (
        "product",
        "cart",
        "quantity",
        "user",
        "get_variations",
        "is_active",
    )
    list_filter = ("is_active",)
