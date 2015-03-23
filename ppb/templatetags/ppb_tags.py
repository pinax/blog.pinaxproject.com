from django import template


register = template.Library()


@register.assignment_tag
def related_posts(post):
    posts = [p for p in post.tags.similar_objects() if p.is_published]
    return posts
