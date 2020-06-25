#! /usr/bin/env python3

import datetime
import re

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

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

    template = env.get_template("index.html")
    header = env.get_template("layout.html")

    result = template.render(
        siteheader=header.render(name="index"),
        posts=posts,
    )

    print(result)


if __name__ == "__main__":
    read_posts()
