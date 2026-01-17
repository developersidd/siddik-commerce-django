from django.contrib import messages
from django.shortcuts import redirect, render

from carts.models import Cart
from coupon.models import Coupon, CouponUsage


# Create your views here.
def apply_coupon(request):
    try:
        current_user = request.user
        if request.method == "POST":
            coupon_code = request.POST.get("coupon_code", "")
            total = int(request.POST.get("total"))
            if coupon_code:
                if not current_user.is_authenticated:
                    messages.error(request, "You must log in to use coupon code")
                    return redirect("cart")
                coupon = Coupon.objects.filter(coupon_code__iexact=coupon_code).first()
               
                if coupon is not None:
                    if coupon.is_valid(current_user, total):
                        coupon_discount_amount = coupon.calculate_discount(total)
                        coupon_usage = CouponUsage.objects.create(
                            user=current_user,
                            discount_amount=coupon_discount_amount,
                            coupon=coupon,
                        )
                        request.session["coupon_usage_id"] = coupon_usage.id
                        messages.success(request, "Coupon Code applied successfully!")
                    else:
                        messages.error(request, "Invalid Coupon Code")
                else:
                     messages.error(request, "Invalid Coupon Code")
            return redirect("cart")
    except Exception as e:
        print("🐍 File: coupon/views.py | Line: 52 | apply_coupon ~ e", e)
        messages.error(request, "There was an error occurred")
        return redirect("cart")
