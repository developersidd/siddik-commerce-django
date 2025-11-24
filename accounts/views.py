from django.shortcuts import redirect, render

from accounts.forms import RegistrationForm
from accounts.models import Account, UserProfile

# Create your views here.


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print(
                "🐍 File: accounts/views.py | Line: 14 | register ~ cleaned_data",
                cleaned_data,
            )
            first_name = cleaned_data["first_name"]
            print(
                "🐍 File: accounts/views.py | Line: 16 | register ~ first_name",
                first_name,
            )
            last_name = cleaned_data["last_name"]
            email = cleaned_data["email"]
            username = email.split("@")[0]
            password = cleaned_data["password"]
            phone_number = cleaned_data["phone_number"]
            country = cleaned_data["country"]
            print("🐍 File: accounts/views.py | Line: 22 | register ~ country", country)
            gender = cleaned_data["gender"]
            city = cleaned_data["city"]
            print("🐍 File: accounts/views.py | Line: 25 | register ~ city", city)
            user = Account.objects.create_user(
                first_name=first_name,
                email=email,
                username=username,
                last_name=last_name,
                password=password,
            )
            print("🐍 File: accounts/views.py | Line: 29 | register ~ user", user)
            user.save()
            user.phone_number = phone_number
            profile = UserProfile()
            profile.user = user
            profile.country = country
            profile.gender = gender
            profile.city = city
            profile.save()
            return redirect("home")
        else:
            print("Error", form.errors)
    else:
        form = RegistrationForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)
