from django.urls import path

from .views import StoryDetailView, StoryListView

app_name = "stories"

urlpatterns = [
    path("", StoryListView.as_view(), name="list"),
    path("<slug:slug>/", StoryDetailView.as_view(), name="detail"),
]
