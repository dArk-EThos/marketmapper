from datetime import timedelta

from django.utils import timezone
from django.views.generic import TemplateView

from apps.opportunities.models import Opportunity


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        publishable = Opportunity.objects.filter(
            verification_status="verified",  # Only verified opportunities
            confidence_score__gte=4, 
            status__in=["open", "closing_soon"]
        ).select_related("region")

        today = timezone.now().date()
        week_out = today + timedelta(days=7)
        month_out = today + timedelta(days=30)  # Add 30-day threshold

        # Stats
        context["stats"] = {
            "total_open": publishable.count(),
            "closing_this_week": publishable.filter(
                application_deadline__lte=week_out,
                application_deadline__gte=today,
            ).count(),
            "last_updated": (
                publishable.order_by("-updated_at").values_list(
                    "updated_at", flat=True
                ).first()
            ),
        }

        # Closing soon: top 5 with deadlines within 30 days
        context["closing_soon"] = publishable.filter(
            application_deadline__gte=today,
            application_deadline__lte=month_out  # Only show deadlines within 30 days
        ).order_by("application_deadline")[:5]

        # Recently added
        context["recently_added"] = publishable.order_by("-created_at")[:5]

        context["today"] = today

        return context


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


class ContactPageView(TemplateView):
    template_name = "pages/contact.html"


class PrivacyPageView(TemplateView):
    template_name = "pages/privacy.html"
