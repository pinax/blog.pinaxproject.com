from importlib import import_module

from django.apps import AppConfig as BaseAppConfig

from pinax.blog.models import Post
from taggit.managers import TaggableManager


class AppConfig(BaseAppConfig):

    name = "ppb"

    def ready(self):
        Post.add_to_class("tags", TaggableManager())
        import_module("ppb.receivers")
