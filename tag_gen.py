#! /usr/bin/env python3

"""
Given a file, find its tags (in a single line at the bottom of markdown).

Replace the tags in its final HTML format actual links (since I don't want
to write them in the source markdown).
"""

import os
import re
import sys

from pathlib import Path
from typing import List


def find_tags(fname: str) -> List[str]:
    """
    We expect the tagline to be on the last line of the file.
    """
    with open(fname) as f:
        tagline = f.readlines()[-1].strip()

    tags = [
        local_link_parse(tag.strip())
        for tag in tagline.split(":")[1].strip().split("*")
    ]

    return tags


def local_link_parse(link: str) -> str:
    """ Returns the destination of a markdown href """
    result = re.match(r'\[.*\](.*)$', link)
    if result:
        return result.group(2)

    raise Exception("Invalid markdown href: {}".format(link))


def date_and_link_parse(line: str) -> str:
    result = re.match(r'- [0-9]{4}-[0-9][0-9]-[0-9][0-9] - .*', line)
    if result:
        return local_link_parse(result.group(1))

    raise Exception("Invalid date+post link: {}".format(line))


def html_to_md_path(fname: str) -> str:
    path = Path(fname)
    path.suffix

    return ""


def parse_index():
    with open("markdown/index.md") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    header = lines[0]
    # second line is just "# Posts"
    posts = lines[2:]

    return header, posts


def get_tags_md():
    """
    Generate a markdown file for a tag if we find a new tag in a post.
    """
    pass


def tag_text_to_ref(tag: str) -> str:
    """ Convert a tag to an html href.  """
    return '<a href="./tag-{}.html">{}</a>'.format(tag.lstrip("#"), tag)


def reference_tag_line(tags: List[str]) -> str:
    return "<p>~ tags : {}</p>".format(" * ".join(map(tag_text_to_ref, tags)))


def parse_tags_from_file(fname: str):
    """
    wrapper for other functionality

    open a file a search for the tags listed in it.
    after finding its tags, create or update tags markdown files.

    # <p>~ tags : #ricing * #android</p>
    """

    with open(fname) as f:
        lines = f.readlines()

    tag_line = None
    for idx, line in enumerate(lines):
        g = re.match(r"<p>~ tags : (.*)<\/p>$", line.strip())
        if g:
            tag_line = g
            lineno = idx
            break

    if not tag_line:
        raise Exception("No tags found: {}".format(fname))

    print("tags found: {}".format(tag_line))

    tags = [tag.strip() for tag in tag_line.group(1).split("*")]

    with open(fname, "w") as f:
        for idx, line in enumerate(lines):
            if idx != lineno:
                f.write(line)
            else:
                f.write(reference_tag_line(tags))


def main():
    parse_tags_from_file(sys.argv[1])


if __name__ == "__main__":
    main()
