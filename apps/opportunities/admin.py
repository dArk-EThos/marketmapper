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
from django.contrib.admin import widgets  
from django.db.models import Count
from django.forms import Select
from django.utils import timezone
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Opportunity, Region


# Custom mixin to ensure edit links work properly with Unfold
class EditableMixin:
    """Ensures admin list items are properly linked for editing."""
    
    def get_list_display_links(self, request, list_display):
        """Force the first column to be editable even with Unfold."""
        if self.list_display_links is None:
            # Default behavior: make the first field clickable
            if list_display:
                return [list_display[0]]
            return []
        return self.list_display_links

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """Ensure choice fields use proper select widgets."""
        if db_field.name == 'verification_status':
            kwargs['widget'] = Select()
        return super().formfield_for_choice_field(db_field, request, **kwargs)


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
class OpportunityAdmin(EditableMixin, ModelAdmin):
    """
    Full-featured admin for vendor opportunities.

    Uses Unfold's ModelAdmin for the polished UI while preserving all
    existing functionality: colored badges, bulk actions, fieldsets,
    and dashboard stats injection.
    """
    
    # Ensure all permissions are enabled
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
        
    def has_view_permission(self, request, obj=None):
        return True

    # ── List view ──
    list_display = (
        "opportunity_name",
        "city",
        "region", 
        "opportunity_type",
        "status",
        "status_colored",
        "verification_status",
        "verification_colored",
        "confidence_score",
        "confidence_colored",
        "link_status_display",
        "application_deadline",
        "is_publishable_display", 
        "last_checked",
    )
    list_display_links = ("opportunity_name",)  # Make opportunity name clickable for editing
    list_filter = (
        "verification_status",
        "status",
        "confidence_score",
        "opportunity_type",
        "region",
        "indoor_outdoor",
        "created_at",
        "application_deadline",
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
        "link_status_display",
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
                    "verification_status",
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
                    "link_status_display",
                ),
                "classes": ["tab"],
                "description": "URLs for vendor applications and event information. Use 'Test Links' action to verify.",
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
        "test_links",
        "mark_links_need_research",
        "mark_as_verified",
        "mark_as_pending",
        "mark_as_unverified", 
        "mark_as_rejected",
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

    @action(description="🔗 Test Links for Dead URLs")
    def test_links(self, request, queryset):
        """Test application_url and source_url for each selected opportunity."""
        import requests
        from requests.exceptions import RequestException
        
        results = {"working": 0, "broken": 0, "details": []}
        
        for opp in queryset:
            urls_to_test = []
            if opp.application_url:
                urls_to_test.append(("Application", opp.application_url))
            if opp.source_url:
                urls_to_test.append(("Source", opp.source_url))
                
            for url_type, url in urls_to_test:
                try:
                    response = requests.get(url, timeout=10, allow_redirects=True)
                    if response.status_code < 400:
                        results["working"] += 1
                        status = f"✅ {url_type}: {response.status_code}"
                    else:
                        results["broken"] += 1
                        status = f"❌ {url_type}: {response.status_code}"
                        # Add note to opportunity
                        if not opp.notes:
                            opp.notes = f"LINK CHECK: {url_type} URL returned {response.status_code}"
                        else:
                            opp.notes += f" | LINK CHECK: {url_type} URL returned {response.status_code}"
                        opp.save()
                except RequestException as e:
                    results["broken"] += 1
                    status = f"❌ {url_type}: Connection failed"
                    # Add note to opportunity
                    if not opp.notes:
                        opp.notes = f"LINK CHECK: {url_type} URL connection failed"
                    else:
                        opp.notes += f" | LINK CHECK: {url_type} URL connection failed" 
                    opp.save()
                    
                results["details"].append(f"{opp.opportunity_name}: {status}")
        
        message = f"Link test complete: {results['working']} working, {results['broken']} broken. Check 'Notes' field for broken links."
        self.message_user(request, message)

    @action(description="🔍 Mark as Needs Link Research")
    def mark_links_need_research(self, request, queryset):
        """Mark opportunities as needing link research in notes."""
        count = 0
        for opp in queryset:
            if not opp.notes:
                opp.notes = "ADMIN: Links need research - check for working vendor/application pages"
            else:
                opp.notes += " | ADMIN: Links need research"
            opp.confidence_score = 3  # Mark as needing verification
            opp.save()
            count += 1
        self.message_user(request, f"Marked {count} opportunities for link research.")

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

    @admin.display(description="Link Status")
    def link_status_display(self, obj):
        """Display quick link status indicators."""
        status_parts = []
        
        if obj.application_url:
            if "LINK CHECK" in (obj.notes or "") and ("404" in obj.notes or "failed" in obj.notes):
                status_parts.append("❌ App URL")
            else:
                status_parts.append("🔗 App URL") 
                
        if obj.source_url:
            if "LINK CHECK" in (obj.notes or "") and ("404" in obj.notes or "failed" in obj.notes):
                status_parts.append("❌ Source")
            else:
                status_parts.append("🔗 Source")
        
        if not status_parts:
            return "No URLs"
            
        return " | ".join(status_parts)

    # ── Verification Actions ──
    
    @action(description="✅ Mark as Verified (Public)")
    def mark_as_verified(self, request, queryset):
        """Mark opportunities as verified for public display."""
        updated = queryset.update(verification_status="verified")
        self.message_user(request, f"{updated} opportunities marked as Verified (will appear on public site).")

    @action(description="⏳ Mark as Pending Review") 
    def mark_as_pending(self, request, queryset):
        """Mark opportunities as pending review."""
        updated = queryset.update(verification_status="pending")
        self.message_user(request, f"{updated} opportunities marked as Pending Review.")

    @action(description="🔍 Mark as Unverified")
    def mark_as_unverified(self, request, queryset):
        """Mark opportunities as unverified (hidden from public)."""
        updated = queryset.update(verification_status="unverified") 
        self.message_user(request, f"{updated} opportunities marked as Unverified (hidden from public).")

    @action(description="❌ Mark as Rejected")
    def mark_as_rejected(self, request, queryset):
        """Mark opportunities as rejected (permanently hidden)."""
        updated = queryset.update(verification_status="rejected")
        self.message_user(request, f"{updated} opportunities marked as Rejected (will not appear publicly).")

    # ── Verification Display Methods ──
    
    @admin.display(description="Verification", ordering="verification_status")
    def verification_colored(self, obj):
        """Display colored verification status badge."""
        badge = obj.get_verification_badge()
        return format_html(
            '<span class="admin-badge {}" style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{} {}</span>',
            badge["class"],
            {
                "badge-warning": "#f59e0b",   # Orange for unverified
                "badge-info": "#3b82f6",      # Blue for pending  
                "badge-success": "#10b981",   # Green for verified
                "badge-danger": "#ef4444",    # Red for rejected
            }.get(badge["class"], "#6b7280"),
            badge["icon"],
            badge["text"]
        )
