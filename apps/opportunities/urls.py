from django.urls import path

from . import views

app_name = "opportunities"

urlpatterns = [
    path("", views.OpportunityListView.as_view(), name="list"),
    # SEO category landing pages
    path(
        "category/<slug:opportunity_type>/",
        views.CategoryLandingView.as_view(),
        name="category",
    ),
    path(
        "category/<slug:opportunity_type>/<slug:region_slug>/",
        views.CategoryLandingView.as_view(),
        name="category_region",
    ),
    path(
        "region/<slug:region_slug>/",
        views.CategoryLandingView.as_view(),
        name="region",
    ),
    # Detail must be last (catch-all slug)
    path("<slug:slug>/", views.OpportunityDetailView.as_view(), name="detail"),
]
