#! /usr/bin/env python3

import datetime
import re

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import mistune

from jinja2 import Environment, FileSystemLoader, select_autoescape


@dataclass
class Post:
    date: str
    name: str
    tags: List[str]

    def __lt__(self, other) -> bool:
        s_date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
        o_date = datetime.datetime.strptime(other.date, "%Y-%m-%d")
        return s_date < o_date


def date_from_md(fname: str) -> Optional[str]:
    """
    Attempt to parse the date of a post from a markdown file.

    Returns the date formatted as YYYY-MM-DD.
    """
    p = Path(fname)

    if p.stem == "index":
        return None

    with open(fname) as f:
        content = f.read()

    date_str = re.search(r'\n\*[A-Z][a-z][a-z] \d\d \d\d\d\d\*\n', content)

    if date_str:
        try:
            date = datetime.datetime.strptime(date_str.group().strip(), "*%b %d %Y*")
            return datetime.datetime.strftime(date, "%Y-%m-%d")
        except ValueError:
            pass

    return None


def tags_from_md(fname: str) -> List[str]:
    """
    Get the tags from a markdown file.
    """
    with open(fname) as f:
        content = f.readlines()

    for line in content:
        g = re.match(r"~ tags : (.*)$", line.strip())
        if g:
            return [tag.strip().lstrip("#") for tag in g.group(1).split(" * ")]

    raise Exception("No tags found: {}".format(fname))


def parse_post(fname: str) -> Post:
    """
    Parse an input markdown 'fname' into a Post.
    """
    p = Path(fname)

    date = date_from_md(fname)
    if not date:
        raise Exception("Could not parse date from file: {}".format(fname))

    return Post(
        date=date,
        name=p.stem,
        tags=tags_from_md(fname),
    )


def gen_index(env, posts: List[Post]):
    """
    Regenerate the index from our list of posts.
    """
    template = env.get_template("index.html")
    header = env.get_template("layout.html")

    with open("markdown/other.md") as f:
        content = f.read()
    other = mistune.create_markdown(plugins=["url"]).parse(content)

    result = template.render(
        siteheader=header.render(name="index"),
        posts=posts,
        other=other,
    )

    print("Rewriting index.html ...")
    with open("index.html", "w") as f:
        f.write(result)


def gen_tags(env, posts: List[Post]):
    """
    Template and write all the tags files based on tags in posts.
    tags.html should be sorted, with most recent tags at the top.
    """
    tags = []
    for post in posts:
        for tag in post.tags:
            if tag not in tags:
                tags.append(tag)

    header = env.get_template("layout.html")

    all_tmpl = env.get_template("tags.html")
    result = all_tmpl.render(
        siteheader=header.render(name="tags"),
        tags=tags,
    )

    # write the all tags page
    print("Rewriting tags.html ...")
    with open("tags.html", "w") as f:
        f.write(result)

    # get each individual tag page
    tag_tmpl = env.get_template("tag-tag.html")
    for tag in tags:
        result = tag_tmpl.render(
            siteheader=header.render(name=tag),
            tagname="#{}".format(tag),
            posts=filter(lambda p: tag in p.tags, posts),
        )

        print("Rewriting tag-{}.html ...".format(tag))
        with open("tag-{}.html".format(tag), "w") as f:
            f.write(result)


def read_posts():
    """
    Read the posts from markdown/.posts
    Convert each filename to a Post

    TODO - convert each one to HTML if it's not found in this dir

    Sort the posts and template our index and tags files.
    """
    with open(".posts") as f:
        posts = sorted([parse_post(line.strip()) for line in f.readlines()], reverse=True)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"]),
    )

    gen_index(env, posts)
    gen_tags(env, posts)


if __name__ == "__main__":
    read_posts()
