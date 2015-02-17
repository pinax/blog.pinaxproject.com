from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from pinax.blog.admin import PostAdmin
from pinax.blog.models import Post
from taggit.models import TaggedItem

from .forms import AdminPostTagsForm


class TaggitListFilter(SimpleListFilter):
    """
    A custom filter class that can be used to filter by taggit tags in the admin.

    From: https://djangosnippets.org/snippets/2807/
    """

    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "tags"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "tag"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value
        for the option that will appear in the URL query. The second element is the
        human-readable name for the option that will appear in the right sidebar.
        """
        tag_list = []
        tags = TaggedItem.tags_for(model_admin.model)
        for tag in tags:
            tag_list.append((tag.name, tag.name))
        return tag_list

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query
        string and retrievable via `self.value()`.
        """
        if self.value():
            return queryset.filter(tags__name__in=[self.value()])


class PostTagsAdmin(PostAdmin):
    form = AdminPostTagsForm
    fields = [
        "section",
        "title",
        "slug",
        "author",
        "markup",
        "teaser",
        "content",
        "description",
        "primary_image",
        "sharable_url",
        "publish",
        "tags"
    ]
    list_filter = ["section", TaggitListFilter]


admin.site.unregister(Post)
admin.site.register(Post, PostTagsAdmin)
