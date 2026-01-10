from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import get_language, get_language_info
from django.views.decorators.csrf import csrf_exempt

from carts.utils import get_cart_items, get_or_create_cart
from orders.models import Order, OrderProduct, OrderStatus
from payment.models import Payment, PaymentStatus
from payment.sslcommerz import sslcommerz_payment_gateway
from store.models import Product


# Create your views here.
@login_required(login_url="login")
def ssl_payment(request):
    if request.method == "POST":
        order_number = request.POST["order_number"]
        cus_name = request.POST["full_name"]
        amount_to_pay = request.POST["total_amount"]
        current_lang = get_language()
        return redirect(
            sslcommerz_payment_gateway(
                cus_name, amount_to_pay, order_number, current_lang
            )
        )
    else:
        print("Redirecting......")
        return redirect("place_order")


# basically telling the view that it doesn't need the token
@csrf_exempt
def validate_payment(request):
    if request.method == "POST":
        body = request.POST
        print("🐍 File: payment/views.py | Line: 39 | validate_payment ~ body", body)
        status = body.get("status")
        # print(
        #    "🐍 File: payment/views.py | Line: 39 | validate_payment ~ status", status
        # )
        if status == "VALID" or status == "SUCCESS":
            order_number = request.GET["order_number"]
            payment_method = body["card_type"]
            tran_id = body["tran_id"]
            base_url = reverse("payment_success")
            query_string = urlencode(
                {
                    "order_number": order_number,
                    "tran_id": tran_id,
                    "payment_method": payment_method,
                    "status": status,
                }
            )
            url = f"{base_url}?{query_string}"
            return redirect(url)
    else:
        return redirect("place_order")


@login_required(login_url="login")
def payment_success(request):
    current_user = request.user
    tran_id = request.GET["tran_id"]
    order_number = request.GET["order_number"]
    payment_method = request.GET["payment_method"]

    if request.method == "GET":
        order = Order.objects.filter(
            is_ordered=False, user=current_user, order_number=order_number
        ).first()

        if order:
            payment = Payment(
                payment_method=payment_method,
                tran_id=tran_id,
                user=current_user,
                order_id=order.id,
                status=PaymentStatus.COMPLETED,
                amount_paid=order.order_total,
            )
            payment.save()

            # Update order
            order.is_ordered = True
            order.status = OrderStatus.ACCEPTED
            order.save()

            # transfer cart items to order product
            cart = get_or_create_cart(request)
            cart_items = get_cart_items(current_user, cart)

            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = order.id
                order_product.user_id = current_user.id
                order_product.quantity = item.quantity
                order_product.product_id = item.product.id
                order_product.product_price = item.product.final_price()
                order_product.ordered = True
                order_product.save()

                order_product.variations.set(item.variations.all())
                order_product.save()

                # Reduce original product stocks
                product = Product.objects.get(id=item.product.id)
                product.stock -= item.quantity
                product.save()

            # clear carts
            cart_items.delete()

            # ordered products
            order_products = order.products.all()

            # send order confirmation Email
            current_site = get_current_site(request).domain
            mail_subject = (
                f"Order Confirmation - #{order.order_number} | Siddik Commerce"
            )
            message = render_to_string(
                "order/order_received_email.html",
                {
                    "order": order,
                    "order_items": order_products,
                    "brand_name": "Siddik Commerce",
                    "domain": current_site,
                },
            )
            to_mail = current_user.email
            send_email = EmailMessage(mail_subject, message, to=[to_mail])
            send_email.content_subtype = "html"

            send_email.send()
            query_string = urlencode(
                {"order_number": order_number, "payment_id": payment.id}
            )
            base_url = reverse("order_complete")
            url = f"{base_url}?{query_string}"
            return redirect(url)

    return redirect("cart")


@csrf_exempt
def payment_failure_callback(request):
    order_number = request.GET.get("order_number")
    tran_id = request.POST.get("tran_id")
    status = request.POST.get("status")
    query_string = urlencode(
        {"order_number": order_number, "tran_id": tran_id, "status": status}
    )
    base_url = reverse("payment_failure")
    url = f"{base_url}?{query_string}"
    return redirect(url)


@login_required(login_url="login")
def payment_failure(request):
    print("🐸🐸 method", request.method)
    order_number = request.GET["order_number"]
    tran_id = request.GET["tran_id"]
    print(
        "🐍 File: payment/views.py | Line: 156 | payment_failure ~ tran_id",
        tran_id,
        order_number,
    )
    current_user = request.user
    order = None
    if order_number:
        order = Order.objects.filter(
            is_ordered=False,
            user=current_user,
            order_number=order_number,
        ).first()
        order.state = OrderStatus.CANCELLED
        print("🐍 File: payment/views.py | Line: 164 | payment_failure ~ order", order)
    context = {"order": order, "tran_id": tran_id}

    return render(request, "payment/payment_failure.html", context)
