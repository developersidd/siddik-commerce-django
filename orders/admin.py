from django.contrib import admin
from django.utils.html import format_html

from orders.models import Order, OrderProduct, OrderStatus


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = (
        "product",
        "quantity",
        "product_price",
        "ordered",
        "variations",
        "user",
    )
    extra = 0


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "ip",
        "status_badge",
        "is_ordered",
        "order_total",
        "user",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "order_number",
        "status",
        "user",
        "created_at",
        "updated_at",
    )
    search_fields = ("order_number", "user", "is_ordered", "phone_number", "email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderProductInline]
    #fieldsets = (
    #    (("Basic Information", {"fields": ("order_number", "ip", "user", "status")})),
    #)

    def status_badge(self, obj):
        status = obj.status
        print("🐍 File: orders/admin.py | Line: 13 | status_badge ~ status", status)

        if status == OrderStatus.NEW:
            color = "#ffc107"
        elif status == OrderStatus.COMPLETED:
            color = "#28a745"

        elif status == OrderStatus.CANCELLED:
            color = "#dc3545"

        elif status == OrderStatus.ACCEPTED:
            color = "#6c757d"
        else:
            color = "#ffc107"
        return format_html(
            "<span style='background-color{}; color: white;padding: 3px 10px; border-radius: 3px;'> {} </span>",
            color,
            status,
        )

    status_badge.short_description = "Order Status"
