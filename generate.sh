#! /usr/bin/env bash

# inputs: one markdown file
# - converts that md to html
#   - scrapes the site header from index.html, and applies proper options to markdown conversion
#
# run ./tag_gen.py to clean up text links for tabs.
# afterward, run ./main.py to fix up tags.

LINK_TAG='<link rel="stylesheet" href="'

main () {
    set -e

    fname="$1"

    if [[ ! -e "$fname" ]]; then
        "File does not exist: $1"
        exit 1
    fi

    # fname is without extension; out is fname.html
    fname="$(basename "${fname%.md}")"
    out="${fname}.html"

    # i know, i know ...
    # https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags
    site_header="$(grep -A1 "^<body class=\"container hack gruvbox-dark\">" index.html | tail -n1)"

    markdown "$1" \
        -t "${fname//-/ }" \
        -s css/gruvbox-dark.css \
        -s css/hack.css \
        | sed 's/^<body>$/<body class="container hack gruvbox-dark">/' \
        | sed "s/^\([[:space:]]*${LINK_TAG}.*\),\(.*\)/\1\">${LINK_TAG}\2/" \
        | sed "/^<body class=\"container hack gruvbox-dark\">/a \\
${site_header}
" \
        > "$out"
}

main "$@"
