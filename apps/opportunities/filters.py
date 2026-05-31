import django_filters

from .models import Opportunity, Region


class OpportunityFilter(django_filters.FilterSet):
    region = django_filters.ModelChoiceFilter(
        queryset=Region.objects.all(),
        empty_label="All Regions",
    )
    opportunity_type = django_filters.ChoiceFilter(
        choices=Opportunity.OPPORTUNITY_TYPES,
        empty_label="All Types",
    )
    status = django_filters.ChoiceFilter(
        choices=[
            ("open", "Open"),
            ("closing_soon", "Closing Soon"),
        ],
        empty_label="Any Status",
    )
    indoor_outdoor = django_filters.ChoiceFilter(
        choices=Opportunity.INDOOR_OUTDOOR_CHOICES,
        empty_label="Indoor/Outdoor",
    )

    class Meta:
        model = Opportunity
        fields = [
            "region",
            "opportunity_type",
            "status",
            "indoor_outdoor",
        ]
