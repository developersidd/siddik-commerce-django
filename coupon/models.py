from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import Account

DISCOUNT_TYPE_CHOICES = [("percentage", "Percentage"), ("fixed", "Fixed Amount")]


# Coupon Model
class Coupon(models.Model):
    description = models.TextField(max_length=200)
    coupon_code = models.TextField(max_length=50, unique=True, db_index=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # Provides exact representation of whole numbers.
    # min_order_amount = models.IntegerField()
    # Offers precise representation of decimal numbers. It handles floating-point arithmetic more accurately than standard float types.
    min_order_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    discount_type = models.CharField(
        choices=DISCOUNT_TYPE_CHOICES, max_length=10, default="percentage"
    )
    discount_value = models.DecimalField(
        decimal_places=2, max_digits=5, validators=[MinValueValidator(Decimal("0.01"))]
    )

    max_usage = models.PositiveIntegerField(default=0, help_text="0 unlimited")
    max_usage_per_user = models.PositiveIntegerField(
        default=1, help_text="Maximum uses per user"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["coupon_code", "is_active"],
            ),
            models.Index(fields=["start_time", "end_time"]),
        ]

    def __str__(self):
        return f"{self.coupon_code} - {self.discount_value} {self.discount_type}"

    def is_valid(self, user=None, order_amount=Decimal("0.00")):
        now = timezone.now()
        if not self.is_active:
            return False, "Coupon is not active"

        if self.start_time > now:
            return False, "Coupon is not yet valid"

        if self.end_time < now:
            return False, "Coupon has expired"

        if self.min_order_amount > 0 and self.min_order_amount > order_amount:
            return False, f"Minimum order amount is {self.min_order_amount}"

        if (
            self.max_usage
            and self.max_usage < CouponUsage.objects.filter(coupon=self).count()
        ):
            return False, f"Coupon usage limit reached"

        if user and user.is_authenticated:

            if (
                self.max_usage_per_user
                and self.max_usage_per_user
                < CouponUsage.objects.filter(coupon=self, user=user).count()
            ):

                return False, f"You have already used this coupon maximum times"

        return True, "Valid"

    def calculate_discount(self, order_amount):
        if self.discount_type == "percentage":
            discount = order_amount / Decimal("100") * self.discount_value
            print(
                "🐍 File: coupon/models.py | Line: 92 | calculate_discount ~ discount",
                discount,
            )
            print(
                "🐍 File: coupon/models.py | Line: 92 | calculate_discount ~ self.discount_value",
                self.discount_value,
            )
        else:
            discount = self.discount_value

        return min(order_amount, discount)

    def get_usage_count(self):

        return CouponUsage.objects.filter(coupon=self).count()

    def get_remaining_usage(self):
        if self.max_usage == 0:
            return "Unlimited"
        return max(0, self.max_usage - CouponUsage.objects.filter(coupon=self).count())


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="coupon_usages"
    )
    # order = models.ForeignKey(
    #    'orders.Order',  # Add this to track which order used the coupon
    #    on_delete=models.CASCADE,
    #    related_name='coupon_usages',
    #    null=True,
    #    blank=True
    # )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Actual discount applied"
    )
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-used_at"]
        indexes = [
            models.Index(fields=["user", "coupon"]),
            models.Index(fields=["used_at"]),
        ]
        # unique_together = [["coupon"]]

    def __str__(self):
        return f"{self.coupon.coupon_code} used by: {self.user.username} on {self.used_at.date()}"
