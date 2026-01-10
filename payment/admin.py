from django.contrib import admin

from payment.models import Payment, PaymentGatewaySettings


# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_method", "amount_paid", "tran_id", "user", "order")


admin.site.register(PaymentGatewaySettings)
