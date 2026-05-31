from django.contrib.sitemaps import Sitemap

from .models import Opportunity


class OpportunitySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Opportunity.objects.filter(
            confidence_score__gte=4,
            status__in=["open", "closing_soon"],
        )

    def lastmod(self, obj):
        return obj.updated_at
