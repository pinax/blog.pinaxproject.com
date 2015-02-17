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

RENDER_FUNC = curry(
    load_path_attr(
        settings.PINAX_BLOG_MARKUP_CHOICE_MAP["markdown"]["parser"]
    )
)


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

    def _fetch_url(self, url, params=None):
        r = self.session.get(url, params=params)
        print "Rate Limits {} / {}: {} with {}".format(
            r.headers.get("X-RateLimit-Limit"),
            r.headers.get("X-RateLimit-Remaining"),
            url,
            params
        )
        data = r.json()
        next_url = self._next_url(r.headers)
        if next_url:
            data.extend(
                self._fetch_url(next_url)
            )
        return data

    def _fetch(self, path, **kwargs):
        kwargs.update(dict(per_page=100))
        return self._fetch_url(
            "https://api.github.com{}".format(path),
            params=kwargs
        )

    def fetch_repos(self, org):
        return self._fetch("/orgs/{}/repos".format(org), type="sources")

    def fetch_commits(self, org, repo, until, since=None):
        commits = []
        url = "/repos/{}/{}/commits".format(org, repo)
        if since:
            commits = self._fetch(url, since=since, until=until)
        else:
            commits = self._fetch(url, until=until)
        return commits

    def format_title(self, name, release_url, version, date, commits):
        return "{} {} Released".format(name, version)

    def format_slug(self, name, release_url, version, date, commits):
        return "{}-{}-released".format(name, version.replace(".", "-"))

    def format_teaser(self, name, release_url, version, date, commits):
        return "A new release of {}".format(name)

    def format_content(self, name, release_url, version, date, commits):
        content = u"This release includes the following:\n\n"
        for commit in commits:
            content += u"* {}\n".format(
                commit["commit"]["message"].split("\n")[0]
            )
        content += u"\n\nDownload: <{}>".format(release_url)
        return content

    def format_description(self, name, release_url, version, date, commits):
        return "A new release of {}.".format(name)

    def create_post(self, name, release_url, version, date, commits):
        title = self.format_title(name, release_url, version, date, commits)
        slug = self.format_slug(name, release_url, version, date, commits)
        teaser = self.format_teaser(name, release_url, version, date, commits)
        content = self.format_content(name, release_url, version, date, commits)
        description = self.format_description(name, release_url, version, date, commits)
        post = Post.objects.create(
            section=2,  # Release Notes
            author=self.author,
            title=title,
            slug=slug,
            markup="markdown",
            teaser_html=RENDER_FUNC(teaser),
            content_html=RENDER_FUNC(content),
            description=description,
            created=date,
            updated=date,
            published=date
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

    def get_releases(self, name):
        releases = []
        if name in ["pinax"]:
            releases
        print "Processing {}".format(name)
        try:
            pypi_data = self.pypi_session.get(
                "http://pypi.python.org/pypi/{}/json".format(name)
            ).json()
            for release in pypi_data["releases"]:
                if pypi_data["releases"][release]:
                    rdata = pypi_data["releases"][release][0]
                    url = rdata["url"]
                    date = pytz.timezone("UTC").localize(
                        parse_datetime(rdata["upload_time"])
                    )
                    releases.append(
                        (date, release, url, rdata["upload_time"] + "Z")
                    )
        except Exception:
            pass
        releases.sort()
        return releases

    def generate_release_note(self, org, name):
        releases = self.get_releases(name)
        prev = None
        for release in releases:
            commits = self.fetch_commits(org, name, release[3], prev)
            commits = [
                c
                for c in commits
                if not c["commit"]["message"].startswith("Merge pull")
            ]
            if len(commits) == 0:
                continue
            prev = release[3]
            self.create_post(name, release[2], release[1], release[0], commits)

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
