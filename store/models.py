from datetime import date, datetime

from itertools import product
from django.db import models
from django.db.models import indexes
from django.urls import reverse
from django.utils import timezone

from accounts.models import Account
from category.models import Category


from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(
        max_length=500,
        blank=True,
        default="This product is designed to provide excellent quality and reliable performance for everyday use. Made with durable materials and crafted with attention to detail, it offers comfort, convenience, and lasting value.",
    )
    price = models.IntegerField()
    # Tracking fields
    view_count = models.PositiveIntegerField(default=0, db_index=True)
    purchase_count = models.PositiveIntegerField(default=0, db_index=True)
    cart_add_count = models.PositiveIntegerField(default=0, db_index=True)
    last_viewed = models.DateTimeField(null=True, blank=True)
    popularity_score = models.FloatField(default=0, db_index=True)
    # Product-level discount (simple discounts)
    discount_percent = models.PositiveIntegerField(
        default=0, help_text="Product-specific discount (0-100)"
    )
    discount_start = models.DateField(null=True, blank=True)
    discount_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def get_active_discounts(self):
        """Returns all active discounts for this product with priority"""
        today = timezone.now().date()
        now = timezone.now()
        discounts = []

        # 1. Product level flash sales
        product_flash_sales = (
            FlashSaleProduct.objects.filter(
                product=self,
                flash_sale__start_time__lte=now,
                flash_sale__end_time__gte=now,
                flash_sale__is_active=True,
            )
            .select_related("flash_sale")
            .order_by("-discount_percent")
        )

        if product_flash_sales.exists():
            fs = product_flash_sales.first()
            discounts.append(
                {
                    "type": "flash_sale",
                    "percent": fs.discount_percent,
                    "priority": 1,
                    "name": fs.flash_sale.title,
                }
            )
        else:
            # Check category-level flash sales
            category_flash_sales = (
                FlashSaleCategory.objects.filter(
                    category=self.category,
                    flash_sale__start_time__lte=now,
                    flash_sale__end_time__gte=now,
                    flash_sale__is_active=True,
                )
                .select_related("flash_sale")
                .order_by("-discount_percent")
            )
            if category_flash_sales.exists():
                fs = category_flash_sales.first()
                discounts.append(
                    {
                        "type": "flash_sale",
                        "percent": fs.discount_percent,
                        "priority": 1,
                        "name": fs.flash_sale.title,
                    }
                )
                
        # 2. Campaigns
        campaigns = (
            Campaign.objects.filter(
                start_date__lte=today, end_date__gte=today, is_active=True
            )
            .filter(models.Q(categories=self.category) | models.Q(products=self))
            .order_by("-discount_percent", "start_date")
        )

        if campaigns.exists():
            campaign = campaigns.first()
            discounts.append(
                {
                    "type": "campaign",
                    "percent": campaign.discount_percent,
                    "priority": 2,
                    "name": campaign.title,
                }
            )

        # 3. Product-level discount
        if (
            self.discount_percent > 0
            and self.discount_start
            and self.discount_end
            and self.discount_start <= today <= self.discount_end
        ):
            discounts.append(
                {
                    "type": "product_discount",
                    "percent": self.discount_percent,
                    "priority": 3,
                    "name": "Product Discount",
                }
            )

        return discounts

    def final_price(self):
        """Calculate final price after applying best discount"""
        discounts = self.get_active_discounts()

        if not discounts:
            return self.price

        # Get highest priority discount (already sorted)
        best_discount = discounts[0]
        discount_amount = (self.price * best_discount["percent"]) / 100
        return round(self.price - discount_amount)

    def get_active_discount_info(self):
        """Returns info about the active discount for display"""
        discounts = self.get_active_discounts()
        return discounts[0] if discounts else None

    def get_url(self):
        return reverse("product_detail", args=[self.category.slug, self.slug])

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(
            average=models.Avg("rating")
        )

        avg = 0
        if reviews["average"] is not None:
            avg = float(reviews["average"])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(
            count=models.Count("id")
        )
        count = 0
        if reviews["count"] is not None:
            count = int(reviews["count"])
        return count


# Campaign Model
class Campaign(models.Model):
    title = models.CharField(max_length=200)
    discount_percent = models.PositiveIntegerField(
        help_text="Discount percentage (0-100)"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    categories = models.ManyToManyField(Category, blank=True, related_name="campaigns")
    products = models.ManyToManyField(Product, blank=True, related_name="campaigns")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-discount_percent", "-start_date"]

    def __str__(self):
        return f"{self.title} ({self.discount_percent}%)"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after start date")


# Flash Sale Model
class FlashSale(models.Model):
    title = models.CharField(max_length=200, default="Flash Sale")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.title}"

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")


class FlashSaleProduct(models.Model):
    flash_sale = models.ForeignKey(
        FlashSale, on_delete=models.CASCADE, related_name="flash_sale_products"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="flash_sales"
    )
    discount_percent = models.PositiveIntegerField(
        help_text="Discount percentage for this product in the flash sale (0-100)"
    )

    class Meta:
        unique_together = ("flash_sale", "product")
        ordering = ["-discount_percent"]


class FlashSaleCategory(models.Model):
    flash_sale = models.ForeignKey(
        FlashSale, on_delete=models.CASCADE, related_name="flash_sale_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="flash_sales"
    )
    discount_percent = models.PositiveIntegerField(
        help_text="Discount percentage for this category in the flash sale (0-100)"
    )

    class Meta:
        unique_together = ("flash_sale", "category")
        ordering = ["-discount_percent"]


# Product View Tracking Model
class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["-viewed_at", "session_key"]),
        ]


# Variation Choices
variation_category_choices = (
    ("color", "color"),
    ("size", "size"),
)


# Variation Manager
class VariationManager(models.Manager):
    def colors(self):
        #  This calls the filter method of the parent models.Manager to retrieve active variations that are categorized as "color"

        # here we are explicitly telling django to use models.Manager (VariationManager), and the current instance of the VariationManager(which is "self")
        # or I can call directly just super().filter... in python 3
        return super(VariationManager, self).filter(
            variation_category="color", is_active=True
        )

    def sizes(self):
        # This defines a custom method to retrieve active variations that are categorized as "size".
        return super().filter(variation_category="size", is_active=True)


# Variation Model
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variations")
    variation_category = models.CharField(choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


# Rating Model
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store/products")

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = "productgallery"
        verbose_name_plural = "product gallery"


# Banner Slider Model
class BannerSlider(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="store/banners")
    link = models.URLField(max_length=200, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


