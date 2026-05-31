from django.views.generic import DetailView, ListView

from .models import VendorStory


class StoryListView(ListView):
    model = VendorStory
    template_name = "stories/story_list.html"
    context_object_name = "stories"
    paginate_by = 9

    def get_queryset(self):
        return VendorStory.objects.filter(status="published")


class StoryDetailView(DetailView):
    model = VendorStory
    template_name = "stories/story_detail.html"
    context_object_name = "story"

    def get_queryset(self):
        return VendorStory.objects.filter(status="published")
