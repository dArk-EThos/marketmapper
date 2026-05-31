"""
Market Mapper — Vendor Stories admin (django-unfold).

Provides:
- Full list view with filters, search, and display columns
- filter_horizontal for the markets_mentioned M2M
- Organized fieldsets with Unfold tab grouping
- Publish / unpublish bulk actions
"""

from django.contrib import admin
from django.utils import timezone

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import VendorStory


# ──────────────────────────────────────────────
# VendorStoryAdmin
# ──────────────────────────────────────────────


@admin.register(VendorStory)
class VendorStoryAdmin(ModelAdmin):
    """Admin for vendor stories — uses Unfold's ModelAdmin."""

    # ── List view ──
    list_display = [
        "vendor_name",
        "business_name",
        "title",
        "category",
        "status",
        "featured",
        "published_date",
    ]
    list_filter = ["status", "category", "featured", "region"]
    search_fields = ["vendor_name", "business_name", "title", "body"]
    prepopulated_fields = {"slug": ("vendor_name", "business_name")}
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 25

    # M2M widget — horizontal filter for selecting related opportunities
    filter_horizontal = ["markets_mentioned"]

    # ── Fieldsets (grouped into Unfold tabs) ──
    fieldsets = (
        (
            "Author & Title",
            {
                "fields": (
                    "vendor_name",
                    "business_name",
                    "slug",
                    "title",
                    "photo_url",
                ),
                "classes": ["tab"],
                "description": "Vendor identity and headline.",
            },
        ),
        (
            "Story Content",
            {
                "fields": (
                    "body",
                    "category",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Markets & Region",
            {
                "fields": (
                    "region",
                    "markets_mentioned",
                ),
                "classes": ["tab"],
                "description": "Link this story to specific markets and a region.",
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "featured",
                    "published_date",
                ),
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
    actions = ["publish_stories", "unpublish_stories", "toggle_featured"]

    @action(description="✅ Publish selected stories")
    def publish_stories(self, request, queryset):
        updated = queryset.update(status="published", published_date=timezone.now())
        self.message_user(request, f"{updated} story(ies) published.")

    @action(description="📝 Unpublish selected stories (set to Draft)")
    def unpublish_stories(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} story(ies) reverted to draft.")

    @action(description="⭐ Toggle featured flag")
    def toggle_featured(self, request, queryset):
        count = 0
        for story in queryset:
            story.featured = not story.featured
            story.save(update_fields=["featured"])
            count += 1
        self.message_user(request, f"Toggled featured flag on {count} story(ies).")
