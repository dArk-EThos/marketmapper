import json

from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.views.generic import ListView, DetailView

from .models import Opportunity, Region
from .filters import OpportunityFilter


class OpportunityListView(ListView):
    model = Opportunity
    template_name = "opportunities/opportunity_list.html"
    context_object_name = "opportunities"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("region")
            .filter(
                verification_status="verified",  # Only verified opportunities
                confidence_score__gte=4, 
                status__in=["open", "closing_soon"]
            )
        )

        # Full-text search via ?q=
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(opportunity_name__icontains=q)
                | Q(city__icontains=q)
                | Q(organizer_name__icontains=q)
                | Q(notes__icontains=q)
            )

        # django-filter integration
        self.filterset = OpportunityFilter(self.request.GET, queryset=qs)
        qs = self.filterset.qs

        # Sorting via ?sort=
        sort = self.request.GET.get("sort", "deadline")
        if sort == "recent":
            qs = qs.order_by("-created_at")
        elif sort == "event_date":
            qs = qs.order_by("event_date")
        else:
            # Default: deadline soonest first, nulls last
            qs = qs.order_by("application_deadline")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["search_query"] = self.request.GET.get("q", "")
        context["current_sort"] = self.request.GET.get("sort", "deadline")
        context["total_results"] = self.filterset.qs.count()
        context["opportunity_types"] = Opportunity.OPPORTUNITY_TYPES
        context["regions"] = Region.objects.all()

        # Map data for Leaflet map view
        # Note: Map functionality disabled since lat/lng fields were removed
        # TODO: Re-implement with geocoding if needed
        map_items = []
        context["map_data"] = json.dumps(map_items)

        return context


class OpportunityDetailView(DetailView):
    model = Opportunity
    template_name = "opportunities/opportunity_detail.html"
    context_object_name = "opportunity"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("region")
            .filter(
                verification_status="verified",  # Only verified opportunities
                confidence_score__gte=4, 
                status__in=["open", "closing_soon"]
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        opp = self.object

        # Related opportunities: same region or same type, exclude self
        related_qs = (
            Opportunity.objects.filter(
                verification_status="verified",  # Only verified opportunities
                confidence_score__gte=4, 
                status__in=["open", "closing_soon"]
            )
            .exclude(pk=opp.pk)
            .select_related("region")
        )

        if opp.region:
            related = related_qs.filter(
                Q(region=opp.region) | Q(opportunity_type=opp.opportunity_type)
            )[:3]
        else:
            related = related_qs.filter(
                opportunity_type=opp.opportunity_type
            )[:3]

        context["related_opportunities"] = related
        context["today"] = timezone.now().date()
        return context


# --- Type labels for human-readable display ---
TYPE_LABELS = dict(Opportunity.OPPORTUNITY_TYPES)


class CategoryLandingView(ListView):
    """SEO landing pages for region + type combinations.

    URLs like:
        /opportunities/farmers-market/
        /opportunities/farmers-market/winnipeg/
    """

    model = Opportunity
    template_name = "opportunities/category_landing.html"
    context_object_name = "opportunities"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Opportunity.objects.filter(
                verification_status="verified",  # Only verified opportunities
                confidence_score__gte=4, 
                status__in=["open", "closing_soon"]
            )
            .select_related("region")
        )

        # Filter by type
        opp_type = self.kwargs.get("opportunity_type")
        if opp_type:
            # Convert slug back to model value (e.g. "farmers-market" -> "farmers_market")
            type_key = opp_type.replace("-", "_")
            if type_key not in TYPE_LABELS:
                raise Http404("Opportunity type not found")
            qs = qs.filter(opportunity_type=type_key)
            self._type_key = type_key
            self._type_label = TYPE_LABELS[type_key]
        else:
            self._type_key = None
            self._type_label = None

        # Filter by region
        region_slug = self.kwargs.get("region_slug")
        if region_slug:
            try:
                self._region = Region.objects.get(slug=region_slug)
            except Region.DoesNotExist:
                raise Http404("Region not found")
            qs = qs.filter(region=self._region)
        else:
            self._region = None

        return qs.order_by("application_deadline")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_results"] = self.get_queryset().count()

        type_label = self._type_label or "Vendor Opportunities"
        region_name = self._region.name if self._region else "Manitoba"

        # Build SEO page title
        if self._type_label and self._region:
            context["page_title"] = f"{type_label}s in {region_name}"
        elif self._type_label:
            context["page_title"] = f"{type_label}s in Manitoba"
        elif self._region:
            context["page_title"] = f"Vendor Opportunities in {region_name}"
        else:
            context["page_title"] = "Vendor Opportunities in Manitoba"

        context["page_description"] = (
            f"Browse {context['total_results']} {type_label.lower()} "
            f"opportunities in {region_name}. "
            f"Find vendor calls, application deadlines, fees, and more."
        )

        context["current_type"] = self._type_key
        context["current_type_label"] = self._type_label
        context["current_region"] = self._region

        # Related categories for cross-linking
        context["all_types"] = [
            {"key": k, "slug": k.replace("_", "-"), "label": v}
            for k, v in Opportunity.OPPORTUNITY_TYPES
        ]
        context["all_regions"] = Region.objects.all()

        return context
