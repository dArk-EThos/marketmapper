from django.views.generic import DetailView, ListView

from .models import BlogPost


class BlogListView(ListView):
    """List all published blog posts with pagination."""

    model = BlogPost
    template_name = "blog/blog_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = BlogPost.CATEGORY_CHOICES
        return context


class BlogDetailView(DetailView):
    """Display a single published blog post with related posts."""

    model = BlogPost
    template_name = "blog/blog_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_posts"] = (
            BlogPost.published.filter(category=self.object.category)
            .exclude(pk=self.object.pk)[:3]
        )
        return context


class BlogCategoryView(ListView):
    """List published blog posts filtered by category."""

    model = BlogPost
    template_name = "blog/blog_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.published.filter(category=self.kwargs["category"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = BlogPost.CATEGORY_CHOICES
        # Resolve the human-readable category name from the slug
        category_map = dict(BlogPost.CATEGORY_CHOICES)
        context["category_name"] = category_map.get(
            self.kwargs["category"], self.kwargs["category"]
        )
        context["current_category"] = self.kwargs["category"]
        return context
