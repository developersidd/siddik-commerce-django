import random
import string

from sslcommerz_lib import SSLCOMMERZ

from payment.models import PaymentGatewaySettings


def generate_trans_id(size=10, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def sslcommerz_payment_gateway(cus_name, amount_to_pay, order_number, lang):

    payment_gateway_settings = PaymentGatewaySettings.objects.all().first()

    settings = {
        "store_id": payment_gateway_settings.store_id,
        "store_pass": payment_gateway_settings.store_pass,
        "issandbox": True,
    }

    sslcommerz = SSLCOMMERZ(settings)
    tran_id = generate_trans_id()
    post_body = {}
    post_body["total_amount"] = amount_to_pay
    post_body["currency"] = "BDT"
    post_body["tran_id"] = tran_id
    post_body["success_url"] = (
        f"http://127.0.0.1:8000/{lang}/payment/validate_payment?order_number={order_number}"
    )

    post_body["fail_url"] = (
        f"http://127.0.0.1:8000/{lang}/payment/payment-failure-callback?order_number={order_number}"
    )
    post_body["cancel_url"] = f"http://127.0.0.1:8000/{lang}/cart"
    post_body["emi_option"] = 0
    post_body["cus_name"] = cus_name
    post_body["cus_email"] = 'request.data["email"]'
    post_body["cus_phone"] = 'request.data["phone"]'
    post_body["cus_add1"] = 'request.data["address_line_1"]'
    post_body["cus_city"] = 'request.data["city"]'
    post_body["cus_country"] = "Bangladesh"
    post_body["shipping_method"] = "NO"
    post_body["multi_card_name"] = ""
    post_body["num_of_item"] = 1
    post_body["product_name"] = "Test"
    post_body["product_category"] = "Test Category"
    post_body["product_profile"] = "general"

    # OPTIONAL PARAMETERS
    post_body["value_a"] = cus_name

    response = sslcommerz.createSession(post_body)
    # print("🐍 File: payment/sslcommerz.py | Line: 57 | sslcommerz_payment_gateway ~ response",response)

    return f"https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY={response["sessionkey"]}"
