from pinax.blog.forms import FIELDS, AdminPostForm
from pinax.blog.models import Post

from taggit.forms import TagField


FIELDS.append("tags")


class AdminPostTagsForm(AdminPostForm):

    tags = TagField(required=False)

    class Meta:
        model = Post
        fields = FIELDS
