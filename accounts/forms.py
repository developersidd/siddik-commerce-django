from ast import arg
import re
from django import forms
from django.forms import ModelForm, ValidationError
from django_countries import countries
from accounts.models import COUNTRY_CHOICES, GENDER_CHOICE, Account



class RegistrationForm(ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter Password", "class": "form-control"}
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        )
    )
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=True)
    gender = forms.ChoiceField(
        choices=GENDER_CHOICE, required=True, widget=forms.RadioSelect
    )
    city = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "email", "password", "phone_number"]

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("Password does not match!")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        placeholders = {
            "first_name": "Enter First Name",
            "last_name": "Enter Last Name",
            "phone_number": "Enter Phone Number",
            "email": "Enter Email Address",
            "password": "Enter Password",
            "confirm_password": "Enter Confirm Password",
            "country": "Select Country",
            "gender": "Select Gender",
            "city": "Enter City",
        }

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "custom-control-input" if field_name == "gender" else "form-control"
            
            field.widget.attrs["placeholder"] = placeholders[field_name]
