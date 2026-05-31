from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class VendorStory(models.Model):
    CATEGORY_CHOICES = [
        ("first_time", "First Time"),
        ("success", "Success Story"),
        ("tips", "Tips & Advice"),
        ("seasonal", "Seasonal"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    vendor_name = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    title = models.CharField(
        max_length=255,
        help_text="A headline quote, e.g. 'My First Market Changed Everything'",
    )
    body = models.TextField()
    photo_url = models.URLField(blank=True, help_text="URL for vendor photo")
    markets_mentioned = models.ManyToManyField(
        "opportunities.Opportunity",
        blank=True,
        related_name="vendor_stories",
    )
    region = models.ForeignKey(
        "opportunities.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_stories",
    )
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="first_time"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    featured = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_date"]
        verbose_name = "Vendor Story"
        verbose_name_plural = "Vendor Stories"

    def __str__(self):
        return f"{self.vendor_name} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.vendor_name} {self.business_name}".strip()
            slug = slugify(base)
            # Ensure uniqueness
            unique_slug = slug
            counter = 1
            while VendorStory.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("stories:detail", kwargs={"slug": self.slug})
