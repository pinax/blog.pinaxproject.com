from pinax.blog.views import BlogIndexView


class TagBlogIndexView(BlogIndexView):

    def get_queryset(self):
        queryset = super(TagBlogIndexView, self).get_queryset()
        queryset = queryset.filter(tags__name__in=[self.kwargs.get("tag")])
        return queryset
