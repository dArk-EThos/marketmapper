import json
from django.contrib import messages
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView

from apps.opportunities.models import Opportunity, Province, Region, OpportunitySubmission
from apps.opportunities.filters import OpportunityFilter
from apps.opportunities.forms import OpportunitySubmissionForm


class OpportunityListView(ListView):
    model = Opportunity
    template_name = "opportunities/opportunity_list.html"
    context_object_name = "opportunities"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("province", "region")
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
                | Q(province__name__icontains=q)
                | Q(region__name__icontains=q)
                | Q(organizer_name__icontains=q)
                | Q(notes__icontains=q)
            )

        # Province filtering via ?province=
        province_slug = self.request.GET.get("province", "").strip()
        if province_slug:
            qs = qs.filter(province__slug=province_slug)

        # Region filtering via ?region=
        region_slug = self.request.GET.get("region", "").strip()
        if region_slug:
            qs = qs.filter(region__slug=region_slug)

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
        context["provinces"] = Province.objects.all().prefetch_related("regions")
        
        # Current filters for display
        context["current_province"] = self.request.GET.get("province", "")
        context["current_region"] = self.request.GET.get("region", "")
        
        # Get regions for selected province (for AJAX updates)
        selected_province = self.request.GET.get("province")
        if selected_province:
            try:
                province = Province.objects.get(slug=selected_province)
                context["regions"] = province.regions.all()
                context["selected_province_name"] = province.name
            except Province.DoesNotExist:
                context["regions"] = Region.objects.none()
        else:
            context["regions"] = Region.objects.none()

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
            .select_related("province", "region")
            .filter(
                verification_status="verified",  # Only verified opportunities
                confidence_score__gte=4, 
                status__in=["open", "closing_soon"]
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        opp = self.object

        # Related opportunities: same province/region or same type, exclude self
        related_qs = (
            Opportunity.objects.filter(
                verification_status="verified",  # Only verified opportunities
                confidence_score__gte=4, 
                status__in=["open", "closing_soon"]
            )
            .exclude(pk=opp.pk)
            .select_related("province", "region")
        )

        # Prioritize same region, then same province, then same type
        if opp.region:
            related = related_qs.filter(
                Q(region=opp.region) | Q(province=opp.province) | Q(opportunity_type=opp.opportunity_type)
            )[:3]
        else:
            related = related_qs.filter(
                Q(province=opp.province) | Q(opportunity_type=opp.opportunity_type)
            )[:3]

        context["related_opportunities"] = related
        context["today"] = timezone.now().date()
        return context


# --- Type labels for human-readable display ---
TYPE_LABELS = dict(Opportunity.OPPORTUNITY_TYPES)


class CategoryLandingView(ListView):
    """SEO landing pages for province/region + type combinations.

    URLs like:
        /opportunities/farmers-market/
        /opportunities/farmers-market/alberta/
        /opportunities/farmers-market/alberta/calgary-region/
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
            .select_related("province", "region")
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

        # Filter by province
        province_slug = self.kwargs.get("province_slug")
        if province_slug:
            try:
                self._province = Province.objects.get(slug=province_slug)
            except Province.DoesNotExist:
                raise Http404("Province not found")
            qs = qs.filter(province=self._province)
        else:
            self._province = None

        # Filter by region
        region_slug = self.kwargs.get("region_slug")
        if region_slug:
            if not self._province:
                raise Http404("Region specified without province")
            try:
                self._region = Region.objects.get(slug=region_slug, province=self._province)
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
        
        # Build location string
        if self._region:
            location_name = f"{self._region.name}, {self._province.name}"
        elif self._province:
            location_name = self._province.name
        else:
            location_name = "Canada"

        # Build SEO page title
        if self._type_label and self._region:
            context["page_title"] = f"{type_label}s in {self._region.name}, {self._province.name}"
        elif self._type_label and self._province:
            context["page_title"] = f"{type_label}s in {self._province.name}"
        elif self._type_label:
            context["page_title"] = f"{type_label}s across Canada"
        elif self._region:
            context["page_title"] = f"Vendor Opportunities in {self._region.name}, {self._province.name}"
        elif self._province:
            context["page_title"] = f"Vendor Opportunities in {self._province.name}"
        else:
            context["page_title"] = "Vendor Opportunities across Canada"

        context["page_description"] = (
            f"Browse {context['total_results']} {type_label.lower()} "
            f"opportunities in {location_name}. "
            f"Find vendor calls, application deadlines, fees, and more."
        )

        context["current_type"] = self._type_key
        context["current_type_label"] = self._type_label
        context["current_province"] = self._province
        context["current_region"] = self._region

        # Related categories for cross-linking
        context["all_types"] = [
            {"key": k, "slug": k.replace("_", "-"), "label": v}
            for k, v in Opportunity.OPPORTUNITY_TYPES
        ]
        context["all_provinces"] = Province.objects.all()
        
        # Regions for current province if applicable
        if self._province:
            context["province_regions"] = self._province.regions.all()

        return context


class OpportunitySubmissionView(CreateView):
    """Form for users to submit new opportunities."""
    
    model = OpportunitySubmission
    form_class = OpportunitySubmissionForm
    template_name = "opportunities/submit_opportunity.html"
    
    def form_valid(self, form):
        # Save the submission
        submission = form.save()
        
        # Show success message
        messages.success(
            self.request,
            "Thank you for your submission! We'll review it and add it to our listings if approved. "
            "You should hear back from us within 3-5 business days."
        )
        
        # Redirect to thank you page or back to form
        return redirect('opportunities:submit_success')
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "There were some errors in your submission. Please review and try again."
        )
        return super().form_invalid(form)


def submit_success_view(request):
    """Thank you page after submitting an opportunity."""
    return render(request, 'opportunities/submit_success.html')


def get_regions_for_province(request):
    """AJAX view to get regions for a selected province."""
    province_slug = request.GET.get('province_slug')
    
    if not province_slug:
        return JsonResponse({'regions': []})
    
    try:
        province = Province.objects.get(slug=province_slug)
        regions = [
            {'slug': region.slug, 'name': region.name}
            for region in province.regions.all()
        ]
        return JsonResponse({'regions': regions})
    except Province.DoesNotExist:
        return JsonResponse({'regions': []})