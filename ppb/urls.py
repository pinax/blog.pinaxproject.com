from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin

from .views import TagBlogIndexView


urlpatterns = patterns(
    "",
    url(r"^admin/", include(admin.site.urls)),
    url(r'^tags/(?P<tag>.*)/$', TagBlogIndexView.as_view(), name="blog_tagged_posts"),
    url(r"", include("pinax.blog.urls")),
)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
