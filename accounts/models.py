from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries import countries


# Custom Account Manager
class MyAccountManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, email, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have an username")
        # self.model is the model class this manager manages
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


# Custom user model
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # set my custom manager
    objects = MyAccountManager()

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

    # This method checks whether the user has a specific permission (e.g., "app_name.add_modelname", "app_name.delete_modelname").
    def has_perm(self, perm, obj=None):
        return self.is_admin or self.is_superadmin

    def has_module_perms(self, app_label):
        # Does the user have permissions to view the app `app_label`?
        # This means only superadmin can see all my installed (e.g. accounts, product, cart) app in admin panel
        return self.is_superadmin


# User Profile model

COUNTRY_CHOICES = tuple(countries)
GENDER_CHOICE = [
    ("male", "male"),
    ("female", "female"),
]


class UserProfile(models.Model):
    # if related_name is not given, it will be userprofile by default
    user = models.OneToOneField(
        Account, on_delete=models.CASCADE, related_name="user_profile"
    )
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    avatar = models.ImageField(upload_to="avatars", blank=True)
    gender = models.CharField(choices=GENDER_CHOICE, blank=True)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(choices=COUNTRY_CHOICES, blank=True)

    def __str__(self):
        return self.user.first_name

    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
