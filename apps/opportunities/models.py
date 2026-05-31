import json

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Region(models.Model):
    """Manitoba geographic region."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    """A vendor opportunity (market, fair, festival, etc.)."""

    # --- Opportunity type choices ---
    OPPORTUNITY_TYPES = [
        ("farmers_market", "Farmers Market"),
        ("craft_fair", "Craft Fair"),
        ("food_festival", "Food Festival"),
        ("night_market", "Night Market"),
        ("pop_up", "Pop-Up"),
        ("holiday_market", "Holiday Market"),
        ("exhibition", "Exhibition"),
        ("community_event", "Community Event"),
        ("retail_opportunity", "Retail Opportunity"),
        ("other", "Other"),
    ]

    # --- Vendor category choices ---
    VENDOR_CATEGORIES = [
        ("food", "Food"),
        ("craft", "Craft"),
        ("art", "Art"),
        ("farm", "Farm"),
        ("vintage", "Vintage"),
        ("wellness", "Wellness"),
        ("other", "Other"),
    ]

    # --- Source type choices ---
    SOURCE_TYPES = [
        ("official", "Official Website"),
        ("organizer", "Organizer Direct"),
        ("municipal", "Municipal/Government"),
        ("social_organizer", "Social Media (Organizer)"),
        ("social_repost", "Social Media (Repost)"),
        ("community", "Community Tip"),
    ]

    # --- Status choices ---
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closing_soon", "Closing Soon"),
        ("closed", "Closed"),
        ("tentative", "Tentative"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    # --- Indoor/outdoor choices ---
    INDOOR_OUTDOOR_CHOICES = [
        ("indoor", "Indoor"),
        ("outdoor", "Outdoor"),
        ("both", "Both"),
    ]

    # --- Confidence score choices ---
    CONFIDENCE_CHOICES = [
        (1, "1 - Very Low"),
        (2, "2 - Low"),
        (3, "3 - Medium"),
        (4, "4 - High"),
        (5, "5 - Very High"),
    ]

    # === Core fields ===
    opportunity_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    province = models.CharField(max_length=100, default="Manitoba")
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    city = models.CharField(max_length=100)
    opportunity_type = models.CharField(max_length=50, choices=OPPORTUNITY_TYPES)
    vendor_categories = models.JSONField(default=list, blank=True)

    # === Date fields ===
    event_date = models.DateField(null=True, blank=True)
    event_date_end = models.DateField(null=True, blank=True)
    event_date_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human-readable date description for recurring/complex schedules",
    )
    application_deadline = models.DateField(null=True, blank=True)
    application_deadline_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human-readable deadline description",
    )

    # === Source fields ===
    application_url = models.URLField(max_length=500, blank=True)
    source_url = models.URLField(max_length=500)
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPES)
    date_found = models.DateField(auto_now_add=True)
    last_checked = models.DateField(auto_now=True)

    # === Status & confidence ===
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="tentative"
    )
    confidence_score = models.IntegerField(choices=CONFIDENCE_CHOICES, default=3)

    # === Logistics ===
    vendor_fee = models.CharField(max_length=255, blank=True)
    booth_size = models.CharField(max_length=100, blank=True)
    indoor_outdoor = models.CharField(
        max_length=20, blank=True, choices=INDOOR_OUTDOOR_CHOICES
    )
    power_available = models.BooleanField(null=True, blank=True)
    insurance_required = models.BooleanField(null=True, blank=True)
    food_vendor_notes = models.TextField(blank=True)

    # === Contact ===
    contact_name = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    social_url = models.URLField(max_length=500, blank=True)
    organizer_name = models.CharField(max_length=200, blank=True)

    # === Meta / admin ===
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    duplicate_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
    )
    meta_description = models.CharField(max_length=160, blank=True)

    # === Location coordinates (for map view) ===
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    # === Badges ===
    BADGE_CHOICES = [
        ("verified", "Verified"),
        ("vendor_favorite", "Vendor Favorite"),
        ("new_market", "New Market"),
        ("returning_annual", "Returning Annual"),
        ("high_demand", "High Demand"),
        ("family_friendly", "Family Friendly"),
        ("accessible", "Accessible"),
    ]
    badges = models.JSONField(
        default=list,
        blank=True,
        help_text="List of badge keys, e.g. ['verified', 'vendor_favorite']",
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-confidence_score", "application_deadline", "-created_at"]
        verbose_name_plural = "opportunities"
        indexes = [
            models.Index(
                fields=["status", "confidence_score"],
                name="idx_status_confidence",
            ),
            models.Index(
                fields=["application_deadline"],
                name="idx_app_deadline",
            ),
            models.Index(
                fields=["opportunity_type"],
                name="idx_opp_type",
            ),
            models.Index(
                fields=["city"],
                name="idx_city",
            ),
            models.Index(
                fields=["region"],
                name="idx_region",
            ),
        ]

    def __str__(self):
        return f"{self.opportunity_name} ({self.city})"

    def is_publishable(self):
        """Whether this opportunity should be shown publicly."""
        return self.confidence_score >= 4 and self.status in ("open", "closing_soon")

    def get_absolute_url(self):
        return reverse(
            "opportunities:detail", kwargs={"slug": self.slug}
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.opportunity_name)
            slug = base_slug
            counter = 1
            while Opportunity.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
