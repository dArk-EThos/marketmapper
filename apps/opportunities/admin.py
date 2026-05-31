"""
Market Mapper — Opportunities & Region admin (django-unfold).

Provides:
- Dashboard stats via AdminSite.each_context monkey-patch
- Colored status / confidence badges
- Bulk status actions using unfold.decorators.action
- Organized fieldsets with Unfold tab grouping
- Environment callback for the UNFOLD badge
"""

from datetime import timedelta

from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Opportunity, Region


# ──────────────────────────────────────────────
# Environment callback (referenced in UNFOLD settings)
# ──────────────────────────────────────────────

def environment_callback(request):
    """
    Return the environment name shown as a colored badge in the Unfold header.
    Dotted path: apps.opportunities.admin.environment_callback
    """
    return "Production"


# ──────────────────────────────────────────────
# Inject dashboard stats into the default AdminSite
# ──────────────────────────────────────────────

_original_each_context = admin.AdminSite.each_context


def _patched_each_context(self, request):
    """Extend the default admin context with Market Mapper dashboard stats."""
    context = _original_each_context(self, request)
    now = timezone.now().date()
    week_from_now = now + timedelta(days=7)
    seven_days_ago = now - timedelta(days=7)

    try:
        context.update(
            {
                "mm_total": Opportunity.objects.count(),
                "mm_open_publishable": Opportunity.objects.filter(
                    status__in=("open", "closing_soon"),
                    confidence_score__gte=4,
                ).count(),
                "mm_closing_this_week": Opportunity.objects.filter(
                    application_deadline__gte=now,
                    application_deadline__lte=week_from_now,
                ).count(),
                "mm_leads_to_verify": Opportunity.objects.filter(
                    confidence_score=3,
                ).count(),
                "mm_recently_added": Opportunity.objects.filter(
                    created_at__date__gte=seven_days_ago,
                ).count(),
            }
        )
    except Exception:
        # Table might not exist yet during initial migrations
        context.update(
            {
                "mm_total": 0,
                "mm_open_publishable": 0,
                "mm_closing_this_week": 0,
                "mm_leads_to_verify": 0,
                "mm_recently_added": 0,
            }
        )
    return context


admin.AdminSite.each_context = _patched_each_context

# Branding (also used when UNFOLD is active for backwards compat)
admin.site.site_header = "Market Mapper Admin"
admin.site.site_title = "Market Mapper"
admin.site.index_title = "Dashboard"


# ──────────────────────────────────────────────
# Color maps for badges
# ──────────────────────────────────────────────

STATUS_COLORS = {
    "open": "#28a745",
    "closing_soon": "#ffc107",
    "closed": "#dc3545",
    "tentative": "#6c757d",
    "cancelled": "#6c757d",
    "completed": "#6c757d",
}


# ──────────────────────────────────────────────
# RegionAdmin
# ──────────────────────────────────────────────


@admin.register(Region)
class RegionAdmin(ModelAdmin):
    """Admin for geographic regions — uses Unfold's ModelAdmin."""

    list_display = ("name", "slug", "opportunity_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_opportunity_count=Count("opportunities"))

    @admin.display(description="Opportunities", ordering="_opportunity_count")
    def opportunity_count(self, obj):
        return obj._opportunity_count


# ──────────────────────────────────────────────
# OpportunityAdmin
# ──────────────────────────────────────────────


@admin.register(Opportunity)
class OpportunityAdmin(ModelAdmin):
    """
    Full-featured admin for vendor opportunities.

    Uses Unfold's ModelAdmin for the polished UI while preserving all
    existing functionality: colored badges, bulk actions, fieldsets,
    and dashboard stats injection.
    """

    # ── List view ──
    list_display = (
        "opportunity_name",
        "city",
        "region",
        "opportunity_type",
        "status",
        "status_colored",
        "confidence_score",
        "confidence_colored",
        "application_deadline",
        "is_publishable_display",
        "last_checked",
    )
    list_filter = (
        "status",
        "confidence_score",
        "opportunity_type",
        "region",
        "city",
        "indoor_outdoor",
    )
    search_fields = (
        "opportunity_name",
        "city",
        "organizer_name",
        "notes",
        "contact_name",
    )
    list_editable = ("status", "confidence_score")
    date_hierarchy = "created_at"
    list_per_page = 30

    # ── Detail view — readonly fields ──
    readonly_fields = (
        "date_found",
        "last_checked",
        "created_at",
        "updated_at",
        "slug",
    )

    # ── Fieldsets (grouped into Unfold tabs) ──
    # Tab 1: General — Basic Info + Location
    # Tab 2: Schedule & Links — Dates + Links & Source
    # Tab 3: Vendor Info — Vendor Details + Contact
    # Tab 4: Admin — Tracking & SEO + System
    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "opportunity_name",
                    "slug",
                    "opportunity_type",
                    "vendor_categories",
                    "organizer_name",
                    "status",
                    "confidence_score",
                ),
                "classes": ["tab"],
                "description": "Core opportunity details.",
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "province",
                    "region",
                    "city",
                    "indoor_outdoor",
                    "latitude",
                    "longitude",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "event_date",
                    "event_date_end",
                    "event_date_text",
                    "application_deadline",
                    "application_deadline_text",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Links & Source",
            {
                "fields": (
                    "application_url",
                    "source_url",
                    "source_type",
                    "social_url",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Vendor Details",
            {
                "fields": (
                    "vendor_fee",
                    "booth_size",
                    "power_available",
                    "insurance_required",
                    "food_vendor_notes",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "contact_name",
                    "contact_email",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Tracking & SEO",
            {
                "fields": (
                    "notes",
                    "tags",
                    "badges",
                    "duplicate_of",
                    "meta_description",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "System",
            {
                "fields": (
                    "date_found",
                    "last_checked",
                    "created_at",
                    "updated_at",
                ),
                "classes": ["tab"],
            },
        ),
    )

    # ── Bulk actions ──
    actions = [
        "mark_as_open",
        "mark_as_closed",
        "mark_as_closing_soon",
        "update_last_checked",
    ]

    @action(description="✅ Mark selected as Open")
    def mark_as_open(self, request, queryset):
        updated = queryset.update(status="open")
        self.message_user(request, f"{updated} opportunity(ies) marked as Open.")

    @action(description="🔴 Mark selected as Closed")
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status="closed")
        self.message_user(request, f"{updated} opportunity(ies) marked as Closed.")

    @action(description="⚠️ Mark selected as Closing Soon")
    def mark_as_closing_soon(self, request, queryset):
        updated = queryset.update(status="closing_soon")
        self.message_user(
            request, f"{updated} opportunity(ies) marked as Closing Soon."
        )

    @action(description="🔄 Update last_checked to today")
    def update_last_checked(self, request, queryset):
        # last_checked is auto_now so we trigger a save on each object
        count = 0
        for obj in queryset:
            obj.save(update_fields=[])
            count += 1
        self.message_user(request, f"Refreshed last_checked for {count} record(s).")

    # ── Custom display columns ──

    @admin.display(description="Status", ordering="status")
    def status_colored(self, obj):
        """Render a colored badge for the opportunity status."""
        color = STATUS_COLORS.get(obj.status, "#6c757d")
        text_color = "#000" if obj.status == "closing_soon" else "#fff"
        return format_html(
            '<span style="background:{}; color:{}; padding:3px 8px; '
            'border-radius:4px; font-size:11px; font-weight:600;">{}</span>',
            color,
            text_color,
            obj.get_status_display(),
        )

    @admin.display(description="Confidence", ordering="confidence_score")
    def confidence_colored(self, obj):
        """Render a dot-based confidence meter."""
        score = obj.confidence_score
        if score >= 4:
            color = "#28a745"
        elif score == 3:
            color = "#ffc107"
        else:
            color = "#dc3545"
        dots = "●" * score + "○" * (5 - score)
        return format_html(
            '<span style="color:{}; font-size:14px; letter-spacing:2px;" '
            'title="{}/5">{}</span>',
            color,
            score,
            dots,
        )

    @admin.display(description="Publishable", boolean=True)
    def is_publishable_display(self, obj):
        """Show a green check if the opportunity meets publishing criteria."""
        return obj.is_publishable()
