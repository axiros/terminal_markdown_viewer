# Terminal Markdown Viewer

Markdown is actually simple enough to be well displayed on modern (256 color) terminals (except images that is).

![first](https://github.com/axiros/terminal_markdown_viewer/blob/master/samples/1.png)

Regarding color options: mdv has quite a lot, ships with > 200 themes, converted from html to ansi.
Those can be combined for code output and regular md output, so you have > 40000 themes in total ;-)

## Alternatives

1. There are few from the js community (e.g. [msee](https://www.npmjs.com/package/msee)) but they require nodejs & npm, which I don't have on my servers. Also I personally did not like the styling and the table handling.

2. pandoc -> html -> elinks, lynx or pandoc -> man -> groff. (Heavy and hard to use from within other programs. Styling suboptimal)

3. vimcat (hard to use inline in other programs, slow)

## Installation

``alias mdv='<path to this repo>/mdv.py'`` within your .bashrc or .zshrc

### Requirements
 
- python2.7
- py markdown (pip install markdown)
- this repo
 

## Usage

### CLI

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

### Inline

mdv is designed to be used well from other (Py2) programs when they have md at hand which should be displayed to the user:

	from mdv import main   # all options there


## Screenshots

### Source

	# Header 1
	## Header 2
	### Header 3
	#### Header 4
	##### Header 5
	###### Header 6
	```python
	""" Test """
	# Make Py2 >>> Py3:
	import os, sys; reload(sys); sys.setdefaultencoding('utf-8')
	# no? see http://stackoverflow.com/a/29832646/4583360 ...
	
	# code analysis for hilite:
	try:
	    from pygments import lex, token
	    from pygments.lexers import get_lexer_by_name, guess_lexer
	```
	
	| Tables            | Fmt            |
	| -- | -- |
	| !!! hint: wrapped | 0.1 **strong** |
	    
	!!! note: title
	    this is a Note
	
	
	``You`` like **__id__**, *__name__*?

### Results

Random results, using the theme roller feature:

![second](https://github.com/axiros/terminal_markdown_viewer/blob/master/samples/2.png)



