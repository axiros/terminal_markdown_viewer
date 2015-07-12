# Terminal Markdown Viewer

Markdown is actually simple enough to be well displayed on modern (256 color) terminals (except images that is).

## Alternatives

1. There are few (e.g. [msee](https://www.npmjs.com/package/msee)) from the js community but they require nodejs & npm, which I don't have on my servers. Also I did not like the styling.

2. pandoc -> html -> elinks, lynx or pandoc -> man -> groff


## Installation

### Requirements
 
- python2.7
- py markdown (pip install markdown)
- this repo

## Usage


    mdv [-t THEME] [-T C_THEME] [-x] [-l] [-L] [-c COLS] [MDFILE]

	Options

    MDFIlE    : path to markdown file
    -t THEME  : key within the color ansi_table.json. 'random' accepted.
    -T C_THEME: pygments theme for code highlight. If not set: Use THEME.
    -l        : light background (not yet supported)
    -L        : display links
    -x        : Do not try guess code lexer (guessing is a bit slow)
    -c COLS   : fix columns to this (default: your terminal width)

	Notes

    Call the main function with markdown string at hand to get a formatted one
    back

    Theme Rollers
    mdv -T all:  All available code styles on the given file.
    mdv -t all:  All available md   styles on the given file.
                 If file is not given we use a short sample file.

    So to see all code hilite variations with a given theme:
        Say C_THEME = all and fix THEME
    Setting both to all will probably spin your beach ball, at least on OSX.


*who knows of a docopt to markdown converter ;-)*?

## Screenshots


