from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.BlogListView.as_view(), name="list"),
    path("category/<str:category>/", views.BlogCategoryView.as_view(), name="category"),
    path("<slug:slug>/", views.BlogDetailView.as_view(), name="detail"),
]
