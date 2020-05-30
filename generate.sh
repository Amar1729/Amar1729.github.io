#! /usr/bin/env bash

LINK_TAG='<link rel="stylesheet" href="'

append_index () {
    name="$1"
    date="$2"

    link="[${name}](./${name}.html)"
    echo "- $date - $link" >> markdown/index.md
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
        append_index "$fname" "$date"
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
