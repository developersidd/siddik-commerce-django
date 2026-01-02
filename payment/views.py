from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from payment.sslcommerz import sslcommerz_payment_gateway


# Create your views here.
@login_required(login_url="login")
def ssl_payment(request):
    if request.method == "POST":
        order_number = request.POST["order_number"]
        cus_name = request.POST["full_name"]
        amount_to_pay = request.POST["total_amount"]

        return redirect(sslcommerz_payment_gateway(cus_name, amount_to_pay, order_number))
    else:
        return redirect("place_order")
# basically telling the view that it doesn't need the token


@csrf_exempt
def validate_payment(request):
    if request.method == "POST":
        body = request.body()
        print("🐍 File: payment/views.py | Line: 18 | validate_payment ~ body", body)
        status = body.get("status")
        if status == "VALID" or status == "SUCCESS":
            order_number = request.GET["order_number"]
            payment_method = body["cart_type"]
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


@login_required(login_url="login")
def payment_success(request):
    pass
