#! /usr/bin/env python3

"""
Replace the tags line in output html with actual links
(they aren't actual links because i don't feel like writing them as links the original markdown)
"""

import re
import shutil
import sys


def main(content):
    for line in content.split("\n"):
        g = re.match(r"<p>~ tags : (.*)<\/p>", line.strip())
        if g:
            tags = [tag.strip().lstrip("#") for tag in g.group(1).split("*")]
            # print(tags)
            # print(line)

            if any(" " in tag for tag in tags):
                raise Exception("improper tags?: {}".format(line))

            tag_line = " * ".join(
                "[{}](./tag-{}.html)".format("#{}".format(tag), tag)
                for tag in tags
            )

            # print(tag_line)
            yield "<p>~ tags : {}</p>".format(tag_line)

        else:
            yield line


if __name__ == "__main__":
    try:
        fname = sys.argv[1]
        with open(fname) as f:
            content = f.read()

        shutil.copy(fname, "{}.bak".format(fname))

        with open(fname, "w") as f:
            f.write("\n".join(main(content)))

    except IndexError:
        content = sys.stdin.read()
        main(content)
