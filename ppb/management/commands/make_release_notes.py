from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils.functional import curry

from django.contrib.auth.models import User

import pytz
import requests

from pinax.blog.models import Post, Revision
from pinax.blog.utils import load_path_attr


RENAMES = [
    ("biblion", "pinax-blog"),
    ("agon", "pinax-points"),
    ("agon-ratings", "pinax-ratings")
]


class Command(BaseCommand):
    help = "generate release notes blog post drafts"
    option_list = BaseCommand.option_list + (
        make_option(
            "--auth-token",
            type="string",
            dest="token",
            help="your github auth token"
        ),
        make_option(
            "--org",
            type="string",
            dest="org",
            help="github org"
        ),
        make_option(
            "--package",
            type="string",
            dest="pkg",
            help="PyPI Package"
        )
    )

    def _next_url(self, headers):
        if headers.get("Link"):
            link = headers.get("Link")
            next_link = [l.split("; ") for l in link.split(", ") if "next" in l]
            if next_link:
                return next_link[0][0].replace("<", "").replace(">", "")

    def _fetch_url(self, url):
        r = self.session.get(url)
        print "Rate Limits", r.headers.get("X-RateLimit-Limit"), "/", r.headers.get("X-RateLimit-Remaining")
        data = r.json()
        next_url = self._next_url(r.headers)
        if next_url:
            data.extend(
                self._fetch_url(next_url)
            )
        return data

    def _fetch(self, path):
        return self._fetch_url("https://api.github.com{}?per_page=100".format(path))

    def fetch_repos(self, org):
        return self._fetch("/orgs/{}/repos?type=sources".format(org))

    def generate_release_note(self, org, name):
        releases = []
        if name in ["pinax"]:
            return
        print "Processing {}".format(name)
        try:
            pypi_data = self.pypi_session.get("http://pypi.python.org/pypi/{}/json".format(name)).json()
            for release in pypi_data["releases"]:
                if pypi_data["releases"][release]:
                    rdata = pypi_data["releases"][release][0]
                    url = rdata["url"]
                    date = pytz.timezone("UTC").localize(parse_datetime(rdata["upload_time"]))
                    releases.append((date, release, url, rdata["upload_time"] + "Z"))
        except Exception as e:
            pass
        releases.sort()
        prev = None
        for release in releases:
            if prev:
                commits = self._fetch_url("https://api.github.com/repos/{}/{}/commits?since={}&until={}".format(
                    org,
                    name,
                    prev,
                    release[3]
                ))
            else:
                commits = self._fetch_url("https://api.github.com/repos/{}/{}/commits?until={}".format(
                    org,
                    name,
                    release[3]
                ))
            commits = [c for c in commits if not c["commit"]["message"].startswith("Merge pull")]
            if len(commits) == 0:
                continue
            prev = release[3]
            render_func = curry(
                load_path_attr(
                    settings.PINAX_BLOG_MARKUP_CHOICE_MAP["markdown"]["parser"]
                )
            )
            teaser = "A new release of {}".format(name)
            content = u"This release includes the following:\n\n"
            for commit in commits:
                content += u"* {}\n".format(commit["commit"]["message"].split("\n")[0])
            content += u"\n\nDownload: <{}>".format(release[2])
            description = "A new release of {}.".format(name)
            post = Post.objects.create(
                section=2,  # Release Notes
                author=self.author,
                title="{} {} Released".format(name, release[1]),
                slug="{}-{}-released".format(name, release[1].replace(".", "-")),
                markup="markdown",
                teaser_html=render_func(teaser),
                content_html=render_func(content),
                description=description,
                created=release[0],
                updated=release[0],
                published=release[0]
            )
            Revision.objects.create(
                post=post,
                title=post.title,
                teaser=teaser,
                content=content,
                author=post.author,
                updated=post.updated,
                published=post.published
            )

    def handle(self, *args, **options):
        auth_token = options["token"]
        org = options["org"]
        pkg = options["pkg"]
        if auth_token is None and org is not None:
            print "You must supply an auth token and GitHub org"
            return
        self.author = User.objects.get(pk=1)
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token {}".format(auth_token)
        })
        self.pypi_session = requests.Session()
        public_repos = [r for r in self.fetch_repos(org) if not r["private"]]
        if pkg is None:
            for repo in public_repos:
                self.generate_release_note(org, repo["name"])
        else:
            self.generate_release_note(org, pkg)
