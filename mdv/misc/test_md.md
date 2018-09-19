# Terminal Markdown Viewer

<table>
<tr><td>foo</td></tr>
<tr><td>foo</td></tr>
<tr><td>foo</td></tr>
<tr><td>foo</td></tr>
</table>

[![Build Status][travis_img]][travis]
<a href='https://coveralls.io/github/axiros/terminal_markdown_viewer?branch=master'>
<img src='https://coveralls.io/repos/github/axiros/terminal_markdown_viewer/badge.svg?branch=master' alt='Coverage Status' /></a>
[![PyPI version](https://badge.fury.io/py/mdv.svg)](https://badge.fury.io/py/mdv)
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>




When you edit multiple md files remotely, like in a larger
[mkdocs](http://www.mkdocs.org/) project, context switches between editing
terminal(s) and viewing browser may have some efficiency impact.
Also sometimes there is just no browser, like via security gateways offering
just a fixed set of applications on the hop in machine.
Further, reading efficiency and convenience is often significantly improved
by using colors.
And lastly, using such a thing for cli applications might improve user output,
e.g. for help texts.

This is where mdv, a Python based Markdown viewer for the terminal might be
a good option.

<!-- toc -->

- [Terminal Markdown Viewer](#terminal-markdown-viewer)
	- [Features](#features)
	- [Alternatives](#alternatives)
	- [Installation](#installation)
	- [Usage](#usage)
		- [CLI](#cli)
		- [Inline](#inline)
		- [Sample Inline Use Case: click module docu](#sample-inline-use-case-click-module-docu)
	- [Customization](#customization)
	- [Screenshots](#screenshots)
	- [TODO](#todo)
	- [Credits](#credits)
	- [Updates](#updates)
		

<!-- tocstop -->



If markdown is often "simple" enough to be somewhat readable on 256 color terminals (except images that is).

<img src="./samples/1.png" width=500>

from

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

	| Tables | Fmt |
	| -- | -- |
	| !!! hint: wrapped | 0.1 **strong** |

	!!! note: title
	    this is a Note


You can also use mdv as a **source code** viewer, best when you have docstrings with markdown in your code:

![](./samples/5.png)

from

```python
~/terminal_markdown_viewer $ cat setup.py
#!/usr/bin/env python2.7
# coding: utf-8

"""_
# Mdv installation

## Usage

    [sudo] ./setup.py install

----
"""

from setuptools import setup, find_packages

import mdv

setup(
    name='mdv',
    version=mdv.__version__,

```
(the '_' after the docstring telling mdv that markdown follows)

----

> mdv is a proof of concept hack: While for simple structures it does its job quite well, for complex markdown you want to use other tools.
> Especially for inlined html it simply fails.

----


## Features

- Tons of theme combinations: mdv ships with > 200 luminocity sorted themes, converted from html themes tables to ansi. Those can be combined for code vs regular markdown output...
- Admonitions
- Tables, incl. wide table handling avoiding "interleaving"
- Somewhat hackable, all in [one](mdv/markdownviewer.py) module
- Useable as lib as well
- File change monitor
- Text wrapping
- Source code highlighter
- Little directory change monitor (cames handy when working on multiple files, to get the current one always displayed)
	- which can run arbitrary commands on file changes
	- which passes filepath, raw and prettyfied content to the other command
        Note: Poor man's implementation, polling. Check inotify based tools if you want sth better.

## Alternatives

The ones I know of (and which made me write mdv ;-) ):

1. There are quite a few from the js community (e.g. [msee](https://www.npmjs.com/package/msee), ansidown, ansimd and also nd which is great) but they require nodejs & npm, which I don't have on my servers. Also I personally wanted table handling and admonition support throughout and prob. too old to hack other peoples' js (struggling enough with my own). But have a look at them, they do some things better than mdv in this early version (I try to learn from them). Also [this](https://github.com/substack/picture-tube) would be worth a look ;-)
2. pandoc -> html -> elinks, lynx or pandoc -> groff -> man. (Heavy and hard to use from within other programs. Styling suboptimal)
3. vimcat (Also heavy and hard to use inline in other programs)

Summary: For production ready robust markdown viewing (e.g. for your customers) I recommend nd still, due to the early state of mdv. For playing around, especially with theming or when with Python, this one might be a valid alternative to look at.

## Installation

    pip install mdv

If you get `no attribute HTML_PLACEHOLDER`: update your markdown package.

[Here](https://trac.macports.org/ticket/53591) is a macport (thanks Aljaž).


### Manual Install: Requirements

- python == 2.7 or > 3.5
- py markdown (pip install markdown)
- py pygments (pip install pygments)
- py yaml (pip install pyyaml)
- py docopt (pip install docopt)
- py tabulate (pip install tabulate)

Further a 256 color terminal (for now best with dark background) and font support for a few special separator characters (which you could change via config).

> For light terms you'd just need to revert the 5 colors from the themes, since they are sorted by luminocity.

I did not test anything on windows.

### Manual Install: Setup

Distribution via setuptools. If setuptools is not installed, run:

    pip install setuptools


Use the setup.py provided inside, I.e. run:

	sudo ./setup.py install
    (or ./setup.py install --user to install only for the current user)



## Usage

### CLI

```markdown

# Usage:

    mdv [OPTIONS] MDFILE

# Options:

    MDFILE    : Path to markdown file
    -A        : Strip all ansi (no colors then)
    -C MODE   : Sourcecode highlighting mode
    -H        : Print html version
    -L        : Backwards compatible shortcut for '-u i'
    -M DIR    : Monitor directory for markdown file changes
    -T C_THEME: Theme for code highlight. If not set: Using THEME.
    -X Lexer  : Default lexer name (default: python). Set -x to use it always.
    -b TABL   : Set tab_length to sth. different than 4 [default: 4]
    -c COLS   : Fix columns to this (default: your terminal width)
    -f FROM   : Display FROM given substring of the file.
    -h        : Show help
    -i        : Show theme infos with output
    -l        : Light background (not yet supported)
    -m        : Monitor file for changes and redisplay FROM given substring
    -n NRS    : Header numbering (default: off. Say e.g. -3 or 1- or 1-5
    -t THEME  : Key within the color ansi_table.json. 'random' accepted.
    -u STYL   : Link Style (it=inline table=default, h=hide, i=inline)
    -x        : Do not try guess code lexer (guessing is a bit slow)


# Notes:

We use stty tool to derive terminal size. If you pipe into mdv we use 80 cols.

## To use mdv.py as lib:

Call the main function with markdown string at hand to get a
formatted one back. Sorry then for no Py3 support, accepting PRs if they don't screw Py2.

## FROM:

FROM may contain max lines to display, seperated by colon.
Example:

    -f 'Some Head:10' -> displays 10 lines after 'Some Head'

If the substring is not found we set it to the *first* character of the file -
resulting in output from the top (if your terminal height can be derived correctly through the stty cmd).

## Code Highlighting

Set -C <all|code|doc|mod> for source code highlighting of source code files.
Mark inline markdown with a '_' following the docstring beginnings.

- all: Show markdown docstrings AND code (default if you say, e.g. `-C.`)
- code: Only Code
- doc: Only docstrings with markdown
- mod: Only the module level docstring


## File Monitor:

If FROM is not found we display the whole file.

## Directory Monitor:

We check only text file changes, monitoring their size.

By default .md, .mdown, .markdown files are checked but you can change like `-M 'mydir:py,c,md,'` where the last empty substrings makes mdv also monitor any file w/o extension (like 'README').

### Running actions on changes:

If you append to `-M` a `'::<cmd>'` we run the command on any change detected (sync, in foreground).

The command can contain placeholders:

    _fp_     # Will be replaced with filepath
    _raw_    # Will be replaced with the base64 encoded raw content
               of the file
    _pretty_ # Will be replaced with the base64 encoded prettyfied output

Like: mdv -M './mydocs:py,md::open "_fp_"'  which calls the open
command with argument the path to the changed file.


## Themes

### Theme Rollers


    mdv -T all [file]:  All available code styles on the given file.
    mdv -t all [file]:  All available md   styles on the given file.
                        If file is not given we use a short sample file.

So to see all code hilite variations with a given theme:

Say C_THEME = all and fix THEME

Setting both to all will probably spin your beach ball...

### Environ Vars

`$MDV_THEME` and `$MDV_CODE_THEME` are understood, e.g. `export
MDV_THEME=729.8953` in your .bashrc will give you a consistent color scheme.


```

> Regarding the strange theme ids: Those numbers are the calculated total luminocity of the 5 theme colors.

### Inline

mdv is designed to be used well from other (Py2) programs when they have md at hand which should be displayed to the user:

```python
import mdv

# config like this:
mdv.term_columns = 60

# calling like this (all CLI options supported, check def main
formatted = mdv.main(my_raw_markdown, c_theme=...)  
```

> Note that I set the defaultencoding to utf-8  in ``__main__``. I have this as my default python2 setup and did not test inline usage w/o. Check [this](http://stackoverflow.com/a/29832646/4583360) for risks.

### Sample Inline Use Case: click module docu

[Armin Ronacher](http://lucumr.pocoo.org/2014/5/12/everything-about-unicode/)'s
[click](http://click.pocoo.org) is a great framework for writing larger CLI apps - but its help texts are a bit boring, intended to be customized.

Here is how:

Write a normal click module with a function but w/o a doc string as shown:
```python
@pass_context                                                                   
def cli(ctx, action, name, host, port, user, msg):           
	""" docu from module __doc__ """
```

On module level you provide markdown for it, like:

```shell
~/axc/plugins/zodb_sub $ cat zodb.py | head
"""
# Fetch and push ZODB trees

## ACTION: < info | pull | push | merge | dump | serve>

- info:  Requests server availability information
(...)
```
which you set at click module import time:

	mod.cli.help = mod.__doc__


Lastly do this in your app module:

```python
from click.formatting import HelpFormatter
def write_text(self, text):
    """ since for markdown pretty out on cli I found no good tool
	so I built my own """
    # poor man's md detection:
    if not text.strip().startswith('#'):
        return orig_write_text(self, text)
    from axc.markdown.mdv import main as mdv
    self.buffer.append(mdv(md=text, theme=os.environ['AXC_THEME']))

HelpFormatter.orig_write_text = HelpFormatter.write_text
HelpFormatter.write_text = write_text
```

The output has then colors:

![](samples/3.png)

and at smaller terms rewraps nicely:

![](samples/4.png)

Further, having markdown in the module ``__doc__`` makes it simple to add into a global project docu framework, like mkdocs.



## Customization

You can supply all CLI args in `$HOME/.mdv`, in yaml format.

More flex you have via `$HOME/.mdv.py`, which is execed if present, when
running `main`.

Alternatively, in [mdv.py](mdv.py) you can change some config straight forward.

```python
# ---------------------------------------------------------------------- Config
txt_block_cut, code_pref, list_pref, br_ends = '✂', '| ', '- ', '◈'
# ansi cols (default):
# R: Red (warnings), L: low visi, BG: background, BGL: background light, C=code
# H1 - H5 = the theme, the numbers are the ansi color codes:
H1,  H2,  H3,  H4,  H5, R,   L,  BG, BGL, T,   TL, C   = \
231, 153, 117, 109, 65, 124, 59, 16, 188, 188, 59, 102
# Code (C is fallback if we have no lexer). Default: Same theme:
CH1, CH2, CH3, CH4, CH5 = H1, H2, H3, H4, H5

code_hl = { "Keyword" : 'CH3', "Name" : 'CH1',
            "Comment" : 'L',  "String": 'CH4',
            "Error"   : 'R',  "Number": 'CH4',
            "Operator": 'CH5',
            "Generic" : 'CH2'
            }

admons = {'note'     : 'H3', 'warning': 'R',
          'attention': 'H1', 'hint'   : 'H4',
          'summary'  : 'H1', 'hint'   : 'H4',
          'question' : 'H5', 'danger' : 'R',
          'caution'  : 'H2'
         }

def_lexer = 'python'
guess_lexer = True
# also global. but not in use, BG handling can get pretty involved...
background = BG

# normal text color:
color = T

show_links = None

# could be given, otherwise read from ansi_tables.json:
themes = {}


# sample for the theme roller feature:
md_sample = ''

# ------------------------------------------------------------------ End Config
```

Any importing module can overwrite those module global variables as well.

Should you need yet additional themes, add them to ``ansi_tables.json`` file by adding your ansi codes there.



## Screenshots

Random results, using the theme roller feature:

![second](https://github.com/axiros/terminal_markdown_viewer/blob/master/samples/2.png)

Note the table block splitting when the table does not fit (last picture).

## TODO

- Refactor the implementation, using a config class
- Lines separators not optimal ([nd](https://www.npmjs.com/package/nd) does better)
- Test light colorscheme
- Dimming
- A few grey scale and 8 color themes
- Sorting of the json by luminance
- Some themes have black as darkest color, change to dark grey
- Common Mark instead of markdown

## Credits

[pygments](http://pygments.org/) (using their lexer)

[tabulate](https://pypi.python.org/pypi/tabulate)

and, naturally, the [python markdown project](https://pythonhosted.org/Markdown/authors.html)

Update: Next version will be CommonMark based though...


## Updates

### July 2016:

Sort of an excuse for the long long time w/o an update:
I did actually start working on a more solid version based on CommonMark but
that went a bit out of scope, into a general html terminal viewer, which will
probably never be finished :-/

So at least here an update containing the stuff you guys sent as PRs, thanks all!!

- installation and dependencies via a setup.py (thanks
  [Martin](https://github.com/althonos))
- supporting `echo -e "# foo\n## bar" | mdv -` and a 'light' theme (thanks
  [Stanislav](https://github.com/seletskiy))
- and a few other improvements regarding python2.7, file location and pyyaml, thanks all.

Also:

- fixed the most obvious bugs with nested ordered and unordered lists
- fixed bold marker
- different color highlighting for the list markers
- added a source code highlighting mode, which highlights also docstrings in markdown (`-C <mode>`)
- some tests in the tests folder
- using `textwrap` now for the wrapping, to avoid these word breaks a few complained about
- you can supply the default lexer now, e.g. `-X javascript [-x]`
- fixed but with not rendered strong texts
- pip install mdv


### Nov 2016:

- travis

- Inline link tables

![](samples/links.png)



[travis]: https://travis-ci.org/axiros/terminal_markdown_viewer
[travis_img]: https://travis-ci.org/axiros/terminal_markdown_viewer.svg?branch=master



### Sept 2018:

foo  
bar ba


- Merged   
  some PRs. 
- Decent [code formatter](https://github.com/ambv/black). Not that this weekend hack got more readable though. Well, maybe a bit.
- Revised Py3 support (finally found peace with it, since they enforce UTF-8 everywhere the new features begin to outweigh the nightmares of trying to decode everything without need).
- Indented code in PY3 was broken, fixed that. *Why, PY3, are you you creating crap like "b'foo'" instead raising or auto-decoding?*
- Header numbering feature added (`-n 2-4` or `-n 1-`)
<img src="./samples/header_num.png" width="400"/>


tabletest

| Date           | foo                      |
|----------------|--------------------------|
| User           | Any                      |
| Campaign       | Any                      |
| Support Portal | `[cpeid, '=', a cpeid]`  |
