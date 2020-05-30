#! /usr/bin/env bash

LINK_TAG='<link rel="stylesheet" href="'

main () {
    if [[ ! -e "$1" ]]; then
        "File does not exist: $1"
        exit 1
    fi

    fname="$(basename "${1%.md}")"
    out="${fname}.html"

    markdown "$1" \
        -t "${fname//-/ }" \
        -s css/gruvbox-dark.css \
        -s css/hack.css \
        | sed 's/^<body>$/<body class="container hack gruvbox-dark">/' \
        | sed "s/^\([[:space:]]*${LINK_TAG}.*\),\(.*\)/\1\">${LINK_TAG}\2/" \
        > "$out"
}

main "$@"
