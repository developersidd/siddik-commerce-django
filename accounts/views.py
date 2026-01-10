from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.decorators import unauthenticated_user
from accounts.forms import RegistrationForm
from accounts.models import Account, UserProfile
from carts.utils import (
    cart_item_exist,
    extract_product_variations,
    get_cart_items,
    get_or_create_cart,
    get_variation_map,
    handle_existing_cart_item,
    handle_existing_cart_items,
)

# Create your views here.


@unauthenticated_user
def register(request):
    if request.method == "POST":
        current_language = request.LANGUAGE_CODE
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            first_name = cleaned_data["first_name"]
            last_name = cleaned_data["last_name"]
            email = cleaned_data["email"]
            username = email.split("@")[0]
            password = cleaned_data["password"]
            phone_number = cleaned_data["phone_number"]
            country = cleaned_data["country"]
            gender = cleaned_data["gender"]
            city = cleaned_data["city"]
            user = Account.objects.create_user(
                first_name=first_name,
                email=email,
                username=username,
                last_name=last_name,
                password=password,
            )
            user.save()
            user.phone_number = phone_number
            profile = UserProfile()
            profile.user = user
            profile.country = country
            profile.gender = gender
            profile.city = city
            profile.save()

            # send email for account activation
            current_site = get_current_site(request)
            mail_subject = "Please active your account"
            message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(
                        user
                    ),  # one time use token
                    "brand_name": "Siddik Commerce",
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = "html"
            send_email.send()
            return redirect(
                f"/{current_language}/accounts/login/?command=verification&email={email}"
            )
        else:
            print("Error", form.errors)
    else:
        form = RegistrationForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def email_template(request):
    user = request.user
    current_site = get_current_site(request)
    mail_subject = "Please active your account"
    message = render_to_string(
        "accounts/account_verification_email.html",
        {
            "user": user,
            "domain": current_site,
            "uid": user.pk,
            "token": default_token_generator.make_token(user),  # one time use token
            "brand_name": "Siddik Commerce",
        },
    )

    to_email = "siddik.prgmr@gmail.com"
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.content_subtype = "html"
    send_email.send()
    return redirect("home")


# @unauthenticated_user
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # check if user exist
        cart = get_or_create_cart(request)
        new_cartitems = get_cart_items(request.user, cart)
        user = auth.authenticate(request, email=email, password=password)

        if user != None:
            auth.login(request, user)
            handle_existing_cart_items(new_cartitems, user)
            messages.success(request, f"You are logged In")
            return redirect("home")
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
            return redirect("login")
    return render(request, "accounts/signin.html")


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user != None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your acccount has been activated")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link!")
        return redirect("register")


# @login_required(login_url="login")
def logout(request):
    try:
        auth.logout(request)
        messages.success(request, "You are logged out successfully!")
        return redirect("login")
    except Exception as e:
        messages.error(request, "Oops! There was as error occurred")
