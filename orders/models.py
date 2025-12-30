from time import sleep
from turtle import ondrag
from django.db import models

from accounts.models import Account
from store.models import Product, Variation


# Create your models here.
class Order(models.Model):

    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed"),
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=55)
    last_name = models.CharField(max_length=55)
    email = models.EmailField(max_length=55)
    phone_number = models.CharField(max_length=55)
    city = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    order_number = models.CharField(max_length=55)
    order_note = models.TextField(max_length=100)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.FloatField()
    is_ordered = models.BooleanField(default=False)
    ip = models.CharField(max_length=50, blank=True)
    status = models.CharField(choices=STATUS, max_length=50)

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return f"Order by {self.full_name()} - Order Number {self.order_number}"


class OrderProduct(models.Model):

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.product_name} ordered by {self.order.full_name()} - Order Number {self.order.order_number}"
