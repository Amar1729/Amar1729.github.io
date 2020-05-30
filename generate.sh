#! /usr/bin/env bash

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
    local date
    date="$(date +%Y-%m-%d)"  # default date is today

    while [[ $# -gt 1 ]]; do
        arg="$1"
        shift
        case "$arg" in
            --date)
                date="$1"
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

    if [[ "$fname" != "index" ]]; then
        # add this post to index.md, and regenerate index.html
        insert_index "$fname" "$date"
        $0 markdown/index.md
    fi
    markdown "$1" \
        -t "${fname//-/ }" \
        -s css/gruvbox-dark.css \
        -s css/hack.css \
        | sed 's/^<body>$/<body class="container hack gruvbox-dark">/' \
        | sed "s/^\([[:space:]]*${LINK_TAG}.*\),\(.*\)/\1\">${LINK_TAG}\2/" \
        > "$out"
}

main "$@"
