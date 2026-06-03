from django.urls import path

from . import views

app_name = "opportunities"

urlpatterns = [
    path("", views.OpportunityListView.as_view(), name="list"),
    
    # Submission form
    path("submit/", views.OpportunitySubmissionView.as_view(), name="submit"),
    path("submit/success/", views.submit_success_view, name="submit_success"),
    
    # AJAX endpoints
    path("ajax/regions/", views.get_regions_for_province, name="ajax_regions"),
    
    # SEO category landing pages - updated for province/region structure
    path(
        "category/<slug:opportunity_type>/",
        views.CategoryLandingView.as_view(),
        name="category",
    ),
    path(
        "category/<slug:opportunity_type>/<slug:province_slug>/",
        views.CategoryLandingView.as_view(),
        name="category_province",
    ),
    path(
        "category/<slug:opportunity_type>/<slug:province_slug>/<slug:region_slug>/",
        views.CategoryLandingView.as_view(),
        name="category_province_region",
    ),
    
    # Province/region landing pages
    path(
        "province/<slug:province_slug>/",
        views.CategoryLandingView.as_view(),
        name="province",
    ),
    path(
        "province/<slug:province_slug>/<slug:region_slug>/",
        views.CategoryLandingView.as_view(),
        name="province_region",
    ),
    
    # Legacy region URLs (now need province context)
    path(
        "region/<slug:region_slug>/",
        views.CategoryLandingView.as_view(),
        name="region_legacy",
    ),
    
    # Detail must be last (catch-all slug)
    path("<slug:slug>/", views.OpportunityDetailView.as_view(), name="detail"),
]