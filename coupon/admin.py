from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from coupon.models import Coupon, CouponUsage


# Register your models here.
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "coupon_code",
        "discount_display",
        "status_badge",
        "validity_period",
        "usage_stats",
        "min_order_amount",
        "created_at",
    )
    list_filter = ("is_active", "discount_type", "created_at", "start_time", "end_time")
    search_fields = ("coupon_code", "description")
    readonly_fields = ("created_at", "updated_at", "usage_stats")

    fieldsets = (
        ("Basic Information",
        {"fields": ("coupon_code", "description", "is_active")}),
        (
            "Discount Details",
            {"fields": ("discount_type", "discount_value", "min_order_amount")},
        ),
        ("Validity Period", {"fields": ("start_time", "end_time")}),
        ("Usage Limits", {"fields": ("max_usage", "max_usage_per_user")}),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at", "usage_stats"),
                "classes": ("collapse",),
            },
        ),
    )

    def discount_display(self, obj):
        if obj.discount_type == "percentage":
            return f"{obj.discount_value}%"
        return f"${obj.discount_value}"

    discount_display.short_description = "Discount"

    def status_badge(self, obj):
        now = timezone.now()
        if not obj.is_active:
            color = "gray"
            status = "Inactive"
        elif now < obj.start_time:
            color = "orange"
            status = "Scheduled"
        elif now > obj.end_time:
            color = "red"
            status = "Expired"
        else:
            color = "green"
            status = "Active"

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            status,
        )

    status_badge.short_description = "Status"

    def validity_period(self, obj):
        return f"{obj.start_time.date()} to {obj.end_time.date()}"

    validity_period.short_description = "Valid Period"

    def usage_stats(self, obj):
        count = obj.get_usage_count()
        remaining = obj.get_remaining_usage()
        return f"{count} used / {remaining} remaining"

    usage_stats.short_description = "Usage Statistics"


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user",  "discount_amount", "used_at") # "order"
    list_filter = ("used_at", "coupon")
    search_fields = ("user__username", "user__email", "coupon__coupon_code")
    readonly_fields = ("used_at",)
    raw_id_fields = ("user",)  # "order"

    def has_add_permission(self, request):
        # Prevent manual creation through admin
        return False
