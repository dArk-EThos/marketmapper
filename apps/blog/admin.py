"""
Market Mapper — Blog admin (django-unfold).

Provides:
- Publish / unpublish bulk actions via unfold.decorators.action
- Organized fieldsets with Unfold tab grouping
- Full search, filters, and date hierarchy
"""

from django.contrib import admin
from django.utils import timezone

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import BlogPost


# ──────────────────────────────────────────────
# BlogPostAdmin
# ──────────────────────────────────────────────


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    """Admin for blog posts — uses Unfold's ModelAdmin."""

    # ── List view ──
    list_display = ("title", "category", "status", "published_date")
    list_filter = ("status", "category")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    list_per_page = 25

    # ── Detail view ──
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "title",
                    "slug",
                    "author_name",
                    "excerpt",
                    "body",
                    "featured_image_url",
                    "category",
                    "tags",
                ),
                "classes": ["tab"],
                "description": "Write and edit blog content here.",
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "published_date",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_description",),
                "classes": ["tab"],
            },
        ),
        (
            "System",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ["tab"],
            },
        ),
    )

    # ── Bulk actions ──
    actions = ["publish_posts", "unpublish_posts"]

    @action(description="✅ Publish selected posts")
    def publish_posts(self, request, queryset):
        updated = queryset.update(status="published", published_date=timezone.now())
        self.message_user(request, f"{updated} post(s) published.")

    @action(description="📝 Unpublish selected posts (set to Draft)")
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} post(s) reverted to draft.")
