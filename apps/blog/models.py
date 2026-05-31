from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class PublishedManager(models.Manager):
    """Custom manager returning only published blog posts."""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(status="published", published_date__lte=timezone.now())
        )


class BlogPost(models.Model):
    """A blog post or seasonal guide."""

    # --- Category choices ---
    CATEGORY_CHOICES = [
        ("seasonal_guide", "Seasonal Guide"),
        ("market_roundup", "Market Roundup"),
        ("vendor_tips", "Vendor Tips"),
        ("news", "News"),
        ("other", "Other"),
    ]

    # --- Status choices ---
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    # === Core fields ===
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    author_name = models.CharField(max_length=200, default="Market Mapper")
    excerpt = models.CharField(
        max_length=300,
        help_text="Short summary shown in list views and social sharing.",
    )
    body = models.TextField()
    featured_image_url = models.URLField(max_length=500, blank=True)

    # === Categorisation ===
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other",
    )
    tags = models.JSONField(default=list, blank=True)

    # === Publishing ===
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    published_date = models.DateTimeField(null=True, blank=True)

    # === SEO ===
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description (max 160 characters).",
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # === Managers ===
    objects = models.Manager()  # default
    published = PublishedManager()

    class Meta:
        ordering = ["-published_date"]
        indexes = [
            models.Index(
                fields=["status", "published_date"],
                name="idx_blog_status_pub",
            ),
            models.Index(
                fields=["category"],
                name="idx_blog_category",
            ),
            models.Index(
                fields=["slug"],
                name="idx_blog_slug",
            ),
        ]
        verbose_name = "blog post"
        verbose_name_plural = "blog posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        """Return True if the post is published and the publish date is past."""
        return (
            self.status == "published"
            and self.published_date is not None
            and self.published_date <= timezone.now()
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
