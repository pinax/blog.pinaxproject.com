from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from pinax.blog.views import BlogIndexView


class TagBlogIndexView(BlogIndexView):

    def get_queryset(self):
        queryset = super(TagBlogIndexView, self).get_queryset()
        queryset = queryset.filter(tags__name__in=[self.kwargs.get("tag")])
        return queryset


def redirect_media(request, path):
    """
    Simple redirect to catch old media hard-coded to
    /site_media/media
    """
    new_url = "{media_url}{path}".format(
        media_url=settings.MEDIA_URL,
        path=path
    )
    return HttpResponsePermanentRedirect(new_url)
