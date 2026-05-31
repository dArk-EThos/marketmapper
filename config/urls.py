"""
URL configuration for Market Mapper.
"""

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.opportunities.sitemaps import OpportunitySitemap
from apps.blog.sitemaps import BlogSitemap

sitemaps = {
    "opportunities": OpportunitySitemap,
    "blog": BlogSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("opportunities/", include("apps.opportunities.urls")),
    path("newsletter/", include("apps.newsletter.urls")),
    path("blog/", include("apps.blog.urls")),
    path("stories/", include("apps.stories.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ),
        name="robots_txt",
    ),
    path("", include("apps.pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
