#!/usr/bin/env bash
#
#
#
here="$(dirname "$0")"
function ensure_fzf {
    hash fzf || { echo "No fzf" && exit 1; }
    # TODO: ask for install using gear/binenv...
}
function all_styles {
    builtin cd "$here"
    local t && t="$(have_theme)"
    test -z "$t" || echo -e "have\t$t"
    for k in b16 5color; do
        /usr/bin/ls "$k" | grep json | sed -e "s/\.json//g" | sed -e "s/^/$k\t/g"
    done
}
function write_config {
    mkdir -p "$HOME/.config/mdv"
    local fn="$_/mdv.py" && touch "$fn"
    grep -v "^THEME=" <"$fn" >"$fn.s"
    echo "THEME='$1'" >>"$fn.s"
    mv "$fn.s" "$fn"
}
function have_theme {
    local fn="$HOME/.config/mdv/mdv.py"
    grep "^THEME=" </home/gk/.config/mdv/mdv.py | cut -d = -f 2 | sed -e 's/"//g' | sed -e "s/'//g"
}
function main {
    ensure_fzf
    local args=""
    while [[ ! -z "$1" ]]; do
        case "$1" in
            -S) shift && continue ;;
            -t) shift && continue ;;
            -T) shift && continue ;;
        esac
        args="'$1' $args"
        shift
    done
    export MDV_NO_ANSI_CURSOR_MVMT=true
    local q t r fn="$HOME/.mdv_tmp_theme"
    rm -f "$fn"
    (all_styles) | fzf --preview="mdv -c '${FZF_PREVIEW_COLUMNS}' -t {2} $args" --color preview-bg:0 --preview-window=right,70% >"$fn"
    r=$? && t="$(cut -f 2 <"$fn")"
    rm -f "$fn" && test "$r" != 0 && return 1
    write_config "$t"
    echo "$t"
}

main "$@"
