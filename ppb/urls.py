from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin

from .views import redirect_media, TagBlogIndexView


urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r'^tags/(?P<tag>.*)/$', TagBlogIndexView.as_view(), name="blog_tagged_posts"),
    url(r"", include("pinax.blog.urls", namespace="pinax_blog")),
    url(r"", include("pinax.pages.urls"))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # fallback for old site media
    urlpatterns += (
        url(r"^site_media/media/(?P<path>.*$)", redirect_media, name="redirect_media"),
    )
