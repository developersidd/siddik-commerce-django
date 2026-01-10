import datetime
import math
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from carts.decorators import empty_cart_redirection
from carts.utils import get_cart_items, get_or_create_cart
from coupon.models import CouponUsage
from orders.forms import OrderForm
from orders.models import Order, OrderProduct
from payment.models import Payment

# Create your views here.


# @empty_cart_redirection
def place_order(request, total=0):
    cart = get_or_create_cart(request)
    cart_items = get_cart_items(request.user, cart)
    coupon_discount = 0
    tax = 0
    grand_total = 0
    user_order = None
    coupon_usage_id = request.session.get("coupon_usage_id")
    current_user = request.user
    for item in cart_items:
        total += item.product.final_price() * item.quantity
    tax = math.ceil(2 * total) / 100
    grand_total = total + tax
    if coupon_usage_id:
        coupon_usage = (
            CouponUsage.objects.filter(user=current_user, id=coupon_usage_id)
            .order_by("-used_at")
            .first()
        )
        # Apply discount to grand total
        if coupon_usage and total > coupon_usage.discount_amount:
            coupon_discount = int(coupon_usage.discount_amount)
            grand_total -= coupon_discount
    order_id = request.session.get("order_id")
    print("🐍 File: orders/views.py | Line: 38 | place_order ~ order_id", order_id)
    if order_id:
        if Order.objects.filter(id=order_id).exists():
            user_order = Order.objects.filter(id=order_id).first()
    if request.method == "POST":
        print("Order form submitted")
        try:
            orderForm = OrderForm(request.POST, instance=user_order)
            if orderForm.is_valid():
                cleaned_data = orderForm.cleaned_data
                order_data = {
                    "first_name": cleaned_data["first_name"],
                    "last_name": cleaned_data["last_name"],
                    "email": cleaned_data["email"],
                    "phone_number": cleaned_data["phone_number"],
                    "city": cleaned_data["city"],
                    "state": cleaned_data["state"],
                    "address_line_1": cleaned_data["address_line_1"],
                    "address_line_2": cleaned_data.get("address_line_2", ""),
                    "order_note": cleaned_data["order_note"],
                    "order_total": grand_total,
                    "order_subtotal": total,
                    "tax": tax,
                    "ip": request.META.get("REMOTE_ADDR"),
                }
                order, created = Order.objects.update_or_create(
                    user=current_user, is_ordered=False, defaults=order_data
                )

                # generate order number
                if not order.order_number:
                    current_date = datetime.date.today().strftime("%Y%m%d")
                    order_number = current_date + str(order.id)
                    order.order_number = order_number
                    order.save()
                request.session["order_id"] = order.id
                return redirect("place_order")
                # url = reverse("place_order")
                # return HttpResponsePermanentRedirect(url)
            else:
                messages.error(request, "There was error an occurred")
                return redirect("checkout")

        except Exception as e:
            messages.error(request, "There was error an occurred")
            return redirect("checkout")
    return render(
        request,
        "order/place_order.html",
        {
            "order": user_order,
            "total": total,
            "cart_items": cart_items,
            "tax": tax,
            "grand_total": grand_total,
            "discount": coupon_discount,
        },
    )


@login_required(login_url="login")
def order_detail(request, order_detail):
    pass


@login_required(login_url="login")
# @empty_cart_redirection
def order_complete(request):
    order_number = request.GET.get("order_number")
    payment_id = request.GET.get("payment_id")
    current_user = request.user
    try:
        order = Order.objects.filter(
            user=current_user, order_number=order_number, is_ordered=True
        ).first()
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.filter(id=payment_id).first()

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "transID": payment.tran_id,
            "payment": payment,
            "subtotal": order.order_subtotal,
        }
        return render(request, "order/order_complete.html", context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")
