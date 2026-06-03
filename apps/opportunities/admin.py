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
from django.forms import RadioSelect, CheckboxSelectMultiple, ModelForm
from django import forms
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Opportunity, Region, Province, OpportunitySubmission
from .forms import OpportunitySubmissionAdminForm


# Custom checkbox widget that properly shows selected values
class FixedCheckboxSelectMultiple(CheckboxSelectMultiple):
    """CheckboxSelectMultiple that properly renders checked state for JSON fields"""
    
    def format_value(self, value):
        """Ensure value is properly formatted for widget rendering"""
        if value is None:
            return []
        if isinstance(value, str):
            try:
                # Handle string representations of lists
                import json
                return json.loads(value)
            except:
                return []
        if isinstance(value, list):
            return value
        return []
    
    def value_from_datadict(self, data, files, name):
        """Extract value from form data"""
        result = super().value_from_datadict(data, files, name)
        return result if result is not None else []


# Custom form with better widgets for JSON fields
class OpportunityAdminForm(ModelForm):
    # Override tags field to accept comma-separated input
    tags = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        help_text='Add tags separated by commas, e.g. "outdoor, seasonal, popular"'
    )
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        widgets = {
            'vendor_categories': FixedCheckboxSelectMultiple(choices=Opportunity.VENDOR_CATEGORIES),
            'badges': FixedCheckboxSelectMultiple(choices=Opportunity.BADGE_CHOICES),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Convert tags list to comma-separated string for display
        if self.instance and self.instance.pk and self.instance.tags:
            if isinstance(self.instance.tags, list):
                self.initial['tags'] = ', '.join(self.instance.tags)
        
        # Ensure checkbox widgets show selected values correctly
        if self.instance and self.instance.pk:
            # Explicitly set initial values for checkbox widgets
            if self.instance.vendor_categories:
                self.initial['vendor_categories'] = self.instance.vendor_categories
            if self.instance.badges:
                self.initial['badges'] = self.instance.badges
    
    def clean_tags(self):
        """Convert comma-separated tags to list"""
        tags_input = self.cleaned_data.get('tags', '')
        if isinstance(tags_input, str):
            # Split by comma and clean up
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            return tags
        return tags_input or []
    
    def clean_vendor_categories(self):
        """Ensure vendor_categories is always a list, never None"""
        categories = self.cleaned_data.get('vendor_categories')
        if categories is None:
            return []
        return categories or []
    
    def clean_badges(self):
        """Ensure badges is always a list, never None"""
        badges = self.cleaned_data.get('badges')
        if badges is None:
            return []
        return badges or []


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
        """Use radio buttons for verification status - more reliable with Unfold."""
        if db_field.name == 'verification_status':
            kwargs['widget'] = RadioSelect()
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    # Remove get_form override - let Django handle it


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
    
    form = OpportunityAdminForm
    
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
                    "verification_status",  # Prominent at top
                    "opportunity_type",
                    "vendor_categories",
                    "organizer_name",
                    "status",
                    "confidence_score",
                ),
                "classes": ["tab"],
                "description": "Core opportunity details. Set Verification Status to control public visibility.",
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "province",
                    "region",
                    "city",
                    "venue",
                    "indoor_outdoor",
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
                    "recurring_pattern",
                    "recurring_description",
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
                    "guidelines_url",
                    "source_url", 
                    "source_type",
                    "social_url",
                    "link_status_display",
                ),
                "classes": ["tab"],
                "description": "URLs for vendor applications, guidelines, and event information. Use 'Test Links' action to verify.",
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
                    "notes",
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
            if opp.guidelines_url:
                urls_to_test.append(("Guidelines", opp.guidelines_url))
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


# ──────────────────────────────────────────────
# ProvinceAdmin
# ──────────────────────────────────────────────

@admin.register(Province)
class ProvinceAdmin(ModelAdmin):
    """Admin for Canadian provinces and territories."""
    
    list_display = ("name", "code", "slug", "region_count", "opportunity_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "code")
    ordering = ("name",)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _region_count=Count("regions", distinct=True),
            _opportunity_count=Count("opportunities", distinct=True)
        )
    
    @admin.display(description="Regions", ordering="_region_count")
    def region_count(self, obj):
        return obj._region_count
    
    @admin.display(description="Opportunities", ordering="_opportunity_count") 
    def opportunity_count(self, obj):
        return obj._opportunity_count


# ──────────────────────────────────────────────
# OpportunitySubmissionAdmin  
# ──────────────────────────────────────────────

@admin.register(OpportunitySubmission)
class OpportunitySubmissionAdmin(ModelAdmin):
    """Admin for user-submitted opportunities requiring approval."""
    
    form = OpportunitySubmissionAdminForm
    
    list_display = (
        "opportunity_name",
        "city", 
        "province_name",
        "submitter_name",
        "status", 
        "status_colored",
        "submitted_at",
        "reviewed_by"
    )
    list_filter = (
        "status",
        "opportunity_type", 
        "province_name",
        "submitted_at",
    )
    search_fields = (
        "opportunity_name",
        "city",
        "province_name", 
        "submitter_name",
        "submitter_email",
        "organizer_name"
    )
    readonly_fields = ("submitted_at", "converted_opportunity")
    date_hierarchy = "submitted_at" 
    list_per_page = 25
    
    fieldsets = (
        (
            "Submission Info",
            {
                "fields": (
                    "status",
                    "submitted_at", 
                    "submitter_name",
                    "submitter_email", 
                    "submitter_organization",
                    "converted_opportunity",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Opportunity Details", 
            {
                "fields": (
                    "opportunity_name",
                    "opportunity_type",
                    "province_name",
                    "region_name",
                    "city",
                    "venue",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Dates & Contact",
            {
                "fields": (
                    "event_date_text",
                    "application_deadline_text",
                    "application_url", 
                    "source_url",
                    "contact_email",
                    "organizer_name",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Vendor Information",
            {
                "fields": (
                    "vendor_fee",
                    "vendor_categories_text", 
                    "additional_notes",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Admin Review",
            {
                "fields": (
                    "admin_notes",
                    "reviewed_by",
                    "reviewed_at",
                ),
                "classes": ["tab"],
            },
        ),
    )
    
    actions = [
        "approve_submissions",
        "reject_submissions", 
        "mark_as_pending",
    ]
    
    @admin.display(description="Status", ordering="status")
    def status_colored(self, obj):
        """Display colored status badge."""
        colors = {
            "pending": "#f59e0b",    # Orange
            "approved": "#10b981",   # Green  
            "rejected": "#ef4444",   # Red
        }
        icons = {
            "pending": "⏳",
            "approved": "✅", 
            "rejected": "❌",
        }
        
        color = colors.get(obj.status, "#6b7280")
        icon = icons.get(obj.status, "")
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{} {}</span>',
            color,
            icon, 
            obj.get_status_display()
        )
    
    @action(description="✅ Approve selected submissions") 
    def approve_submissions(self, request, queryset):
        """Approve submissions and convert to opportunities."""
        approved = 0
        for submission in queryset.filter(status="pending"):
            try:
                # Create opportunity from submission
                opportunity = self._convert_submission_to_opportunity(submission)
                
                # Update submission  
                submission.status = "approved"
                submission.reviewed_by = request.user.username
                submission.reviewed_at = timezone.now()
                submission.converted_opportunity = opportunity
                submission.save()
                
                approved += 1
                
            except Exception as e:
                self.message_user(
                    request,
                    f"Error converting {submission.opportunity_name}: {str(e)}", 
                    level=messages.ERROR
                )
        
        if approved:
            self.message_user(
                request,
                f"Successfully approved {approved} submission(s) and created opportunities."
            )
    
    @action(description="❌ Reject selected submissions")
    def reject_submissions(self, request, queryset):
        """Reject submissions."""
        updated = queryset.filter(status="pending").update(
            status="rejected",
            reviewed_by=request.user.username,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f"Rejected {updated} submission(s).")
    
    @action(description="⏳ Mark as Pending Review")
    def mark_as_pending(self, request, queryset):
        """Mark submissions as pending review."""
        updated = queryset.update(status="pending")
        self.message_user(request, f"Marked {updated} submission(s) as pending review.")
    
    def _convert_submission_to_opportunity(self, submission):
        """Convert a submission to an approved opportunity."""
        from django.utils.text import slugify
        
        # Try to match province
        try:
            province = Province.objects.get(
                Q(name__iexact=submission.province_name) |
                Q(code__iexact=submission.province_name)
            )
        except Province.DoesNotExist:
            # Default to first available province if no match
            province = Province.objects.first()
            if not province:
                raise ValueError(f"No provinces available. Please create provinces first.")
        
        # Try to match or create region
        region = None
        if submission.region_name:
            region, created = Region.objects.get_or_create(
                name=submission.region_name,
                province=province,
                defaults={"slug": slugify(submission.region_name)}
            )
        
        # Create the opportunity
        opportunity = Opportunity.objects.create(
            opportunity_name=submission.opportunity_name,
            province=province,
            region=region,
            city=submission.city,
            venue=submission.venue,
            opportunity_type=submission.opportunity_type,
            event_date_text=submission.event_date_text,
            application_deadline_text=submission.application_deadline_text,
            application_url=submission.application_url,
            source_url=submission.source_url,
            source_type="user_submission",
            contact_email=submission.contact_email,
            organizer_name=submission.organizer_name,
            vendor_fee=submission.vendor_fee,
            notes=submission.additional_notes,
            # Submission tracking
            submitter_name=submission.submitter_name,
            submitter_email=submission.submitter_email,
            submission_notes=f"Converted from submission ID {submission.id}",
            # Set as unverified by default - requires manual verification
            verification_status="unverified",
            confidence_score=3,
            status="tentative"
        )
        
        return opportunity
