#! /usr/bin/env bash

# inputs: one markdown file and optional args (see main() argparsing)
# - converts that md to html
# - adds that file+date to index, and regens index
# - get the site header from the index, and add it to our new post
#
# note - this script is pretty hacky, requires double-checking files afterward.
# Also, have to run ./tag_gen.py to make sure tags are updated in resulting htmls.
# if new tags have been added, have to update tags.md and tags.html manually :/
#  -> see tag_gen.get_tags_md

LINK_TAG='<link rel="stylesheet" href="'

insert_index () {
    name="$1"
    date="$2"

    # making some assumptions about the format of index.md here
    # but essentially we assume first 4 lines are the header
    # rest of the lines are just bulleted list of links
    # insert 'name' blog post at the fifth line

    header="$(sed '1,5!d' markdown/index.md)"
    posts="$(sed '1,4d' markdown/index.md)"

    link="[${name}](./${name}.html)"

    echo "$header" > markdown/index.md
    echo "- $date - $link" >> markdown/index.md
    echo "$posts" >> markdown/index.md
}

main () {
    set -e

    local date dry
    date="$(date +%Y-%m-%d)"  # default date is today
    dry=''  # default is NOT to --dry run

    while [[ $# -gt 1 ]]; do
        arg="$1"
        shift
        case "$arg" in
            --date)
                date="$1"
                shift
                ;;
            --dry)
                dry=1
                ;;
        esac
    done

    # should be one argument left over:
    fname="$1"

    if [[ ! -e "$fname" ]]; then
        "File does not exist: $1"
        exit 1
    fi

    # fname is without extension; out is fname.html
    fname="$(basename "${fname%.md}")"
    out="${fname}.html"

    if [[ "$fname" != "index" && -z "$dry" ]]; then
        # add this post to index.md, and regenerate index.html
        insert_index "$fname" "$date"
        $0 markdown/index.md
    fi

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
