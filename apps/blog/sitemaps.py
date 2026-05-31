from django.contrib.sitemaps import Sitemap

from .models import BlogPost


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return BlogPost.published.all()

    def lastmod(self, obj):
        return obj.updated_at
