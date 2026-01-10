from django.db import models
from accounts.models import Account
from orders.models import Order


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    REFUNDED = "REFUNDED", "Refunded"

# Create your models here.
class Payment(models.Model):

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True, related_name="payment")
    payment_method = models.CharField(max_length=100)
    tran_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PaymentStatus, default=PaymentStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Paid: {self.amount_paid} through {self.payment_method} by {self.user.full_name()} - Order Number: {self.order.order_number}"


class PaymentGatewaySettings(models.Model):

    store_id = models.CharField(max_length=500, blank=True, null=True)
    store_pass = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = "PaymentGatewaySetting"
        verbose_name_plural = "PaymentGatewaySettings"
        db_table = "paymentgatewaysettings"

    def __str__(self):
        return self.store_id
