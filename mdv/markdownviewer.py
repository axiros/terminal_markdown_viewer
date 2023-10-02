#!/usr/bin/env python
# coding: utf-8
"""_
# Usage:

    mdv [options] [MDFILE]

# Options:
    -A         : no_colors     : Strip all ansi (no colors then)
    -C MODE    : code_hilite   : Sourcecode highlighting mode
    -F FILE    : config_file   : Alternative configfile (defaults ~./.mdv or ~/.config/mdv)
    -H         : do_html       : Print html version
    -L         : display_links : Backwards compatible shortcut for '-u i'
    -M DIR     : monitor_dir   : Monitor directory for markdown file changes
    -T C_THEME : c_theme       : Theme for code highlight. If not set we use THEME.
    -X Lexer   : c_def_lexer   : Default lexer name (default python). Set -x to use it always.
    -b TABL    : tab_length    : Set tab_length to sth. different than 4 [default 4]
    -c COLS    : cols          : Fix columns to this (default <your terminal width>)
    -f FROM    : from_txt      : Display FROM given substring of the file.
    -h         : sh_help       : Show help
    -i         : theme_info    : Show theme infos with output
    -l         : bg_light      : Light background (not yet supported)
    -m         : monitor_file  : Monitor file for changes and redisplay FROM given substring
    -n NRS     : header_nrs    : Header numbering (default off. Say e.g. -3 or 1- or 1-5)
    -t THEME   : theme         : Key within the color ansi_table.json. 'random' accepted.
    -u STYL    : link_style    : Link Style (it=inline table=default, h=hide, i=inline)
    -x         : c_no_guess    : Do not try guess code lexer (guessing is a bit slow)

# Details

### **MDFILE**

Filename to markdownfile or '-' for pipe mode (no termwidth auto dedection then)

### Configuration

Happens like:

    1. parse_default_files at (`~/.mdv` or `~/.config/mdv`)
    2. overlay with any -F <filename> config
    3. overlay with environ vars (e.g. `$MDV_THEME`)
    4. overlay with CLI vars

#### File Formats

We try yaml.
If not installed we try json.
If it is the custom config file we fail if not parsable.
If you prefer shell style config then source and export so you have it as environ.

### **-c COLS**: Columns

We use stty tool to derive terminal size. If you pipe into mdv we use 80 cols.
You can force the columns used via `-c`.
If you export `$width`, this has precedence over `$COLUMNS`.

### **-b TABL**: Tablength

Setting tab_length away from 4 violates [markdown](https://pythonhosted.org/Markdown/).
But since many editors interpret such source we allow it via that flag.


### **-f FROM**: Partial Display

FROM may contain max lines to display, seperated by colon.
Example:

    -f 'Some Head:10' -> displays 10 lines after 'Some Head'

If the substring is not found we set it to the *first* character of the file -
resulting in output from the top (if your terminal height can be derived
correctly through the stty cmd).


## Themes

`$MDV_CODE_THEME` is an alias for the standard `$MDV_C_THEME`

```bash
export MDV_THEME='729.8953'; mdv foo.md
```

### Theme rollers:


    mdv -T all:  All available code styles on the given file.
    mdv -t all:  All available md styles on the given file.
                 If file is not given we use a short sample file.

So to see all code hilite variations with a given theme:

Say `C_THEME=all` and fix `THEME`

Setting both to all will probably spin your beach ball...


## Inline Usage (mdv as lib)

Call the main function with markdown string at hand to get a
formatted one back. Sorry then for no Py3 support, accepting PRs if they
don't screw Py2.


## Source Code Highlighting

Set -C <all|code|doc|mod> for source code highlighting of source code files.
Mark inline markdown with a '_' following the docstring beginnings.

- all: Show markdown docstrings AND code (default, if you say e.g. -C.)
- code: Only Code
- doc: Only docstrings with markdown
- mod: Only the module level docstring


## File Monitor:

If FROM is not found we display the whole file.

## Directory Monitor:

We check only text file changes, monitoring their size.

By default .md, .mdown, .markdown files are checked but you can change like
`-M 'mydir:py,c,md,'` where the last empty substrings makes mdv also monitor
any file w/o extension (like 'README').

### Running actions on changes:

If you append to `-M` a `'::<cmd>'` we run the command on any change detected
(sync, in foreground).

The command can contain placeholders:

    _fp_     # Will be replaced with filepath
    _raw_    # Will be replaced with the base64 encoded raw content
               of the file
    _pretty_ # Will be replaced with the base64 encoded prettyfied output

Like: `mdv -M './mydocs:py,md::open "_fp_"'` which calls the open command
with argument the path to the changed file.



"""
from __future__ import absolute_import, print_function, unicode_literals

import sys

PY3 = sys.version_info.major > 2

if not PY3:

    def breakpoint():
        import pdb

        pdb.set_trace()


import io
import os
import textwrap
import shutil
import time
import markdown
import re
import markdown.util

try:
    # in py3 not done automatically:
    import xml.etree.cElementTree as etree
except:
    import xml.etree.ElementTree as etree

from markdown.extensions.tables import TableExtension
from random import randint
from .tabulate import tabulate
from json import loads
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension, fenced_code
from functools import partial

errout, envget = partial(print, file=sys.stderr), os.environ.get

# ---------------------------------------------------------------------- Config
hr_sep, txt_block_cut, code_pref, list_pref, bquote_pref, hr_ends = (
    '─',
    '✂',
    '| ',
    '- ',
    '|',
    '◈',
)
# ansi cols (default):
# R: Red (warnings), L: low visi, BG: background, BGL: background light, C=code
# H1 - H5 = the theme, the numbers are the ansi color codes:
H1, H2, H3, H4, H5, R, L, BG, BGL, T, TL, C = (
    231,
    153,
    117,
    109,
    65,
    124,
    59,
    16,
    188,
    188,
    59,
    102,
)
# Code (C is fallback if we have no lexer). Default: Same theme:
CH1, CH2, CH3, CH4, CH5 = H1, H2, H3, H4, H5

code_hl = {
    'Keyword': 'CH3',
    'Name': 'CH1',
    'Comment': 'L',
    'String': 'CH4',
    'Error': 'R',
    'Number': 'CH4',
    'Operator': 'CH5',
    'Generic': 'CH2',
}

admons = {
    'note': 'H3',
    'warning': 'R',
    'attention': 'H1',
    'hint': 'H4',
    'summary': 'H1',
    'hint': 'H4',
    'question': 'H5',
    'danger': 'R',
    'dev': 'H5',
    'hint': 'H4',
    'caution': 'H2',
}

link_start = '①'
link_start_ord = ord(link_start)

def_lexer = 'python'
guess_lexer = True
# also global. but not in use, BG handling can get pretty involved, to do with
# taste, since we don't know the term backg....:
background = BG

# hirarchical indentation by:
left_indent = '  '
# normal text color:
color = T

# it: inline table, h: hide, i: inline
show_links = 'it'


# could be given, otherwise read from ansi_tables.json:
themes = {}


# sample for the theme roller feature:
md_sample = ''

# dir monitor recursion max:
mon_max_files = 1000
# ------------------------------------------------------------------ End Config

# columns(!) - may be set to smaller width:
# could be exported by the shell, normally not in subprocesses:


def get_terminal_size():
    """get terminal size for python3.3 or greater, using shutil.

    taken and modified from http://stackoverflow.com/a/14422538

    Returns:
        tuple: (column, rows) from terminal size, or (0, 0) if error.
    """
    error_terminal_size = (0, 0)
    if hasattr(shutil, 'get_terminal_size'):
        # The following statement will return 0, 0 if running by PyCharm in Windows,
        # resulting in printing "!! Could not derive your terminal width !!" later.
        # if raise error, it will cause "OSError: [WinError 6] The handle is invalid."
        terminal_size = shutil.get_terminal_size(fallback=error_terminal_size)
        return terminal_size.columns, terminal_size.lines
    else:
        return error_terminal_size


# zsh does not allow to override COLUMNS ! Thats why we also respect $width:
term_columns, term_rows = envget('width', envget('COLUMNS')), envget('LINES')
if not term_columns and not '-c' in sys.argv:
    try:
        if sys.platform != "win32":
            # The following statement will print "the system cannot find the path specified" in Windows, so omitting
            term_rows, term_columns = os.popen('stty size 2>/dev/null', 'r').read().split()
        else:
            raise Warning('OS is win32, entering expect statement...')
        term_columns, term_rows = int(term_columns), int(term_rows)
    except:  # pragma: no cover
        term_columns, term_rows = get_terminal_size()
        if '-' not in sys.argv and (term_columns, term_rows) == (0, 0):
            errout('!! Could not derive your terminal width !!')
term_columns, term_rows = int(term_columns or 80), int(term_rows or 200)


def die(msg):
    errout(msg)
    sys.exit(1)


def parse_env_and_cli():
    """replacing docopt"""
    kw, argv = {}, list(sys.argv[1:])
    opts = __doc__.split('# Options', 1)[1].split('# Details', 1)[0].strip()
    opts = [_.lstrip().split(':', 2) for _ in opts.splitlines()]
    opts = dict(
        [
            (l[0].split()[0], (l[0].split()[1:], l[1].strip(), l[2].strip()))
            for l in opts
            if len(l) > 2
        ]
    )

    # check environ:
    aliases = {
        'MDV_C_THEME': ['AXC_CODE_THEME', 'MDV_CODE_THEME'],
        'MDV_THEME': ['AXC_THEME'],
    }
    for k, v in aliases.items():
        for f in v:
            if f in os.environ:
                os.environ[k] = envget(f)
    for k, v in opts.items():
        V = envget('MDV_' + v[1].upper())
        if V is not None:
            kw[v[1]] = V
    # walk cli args:
    while argv:
        k = argv.pop(0)
        k = '-h' if k == '--help' else k
        try:
            reqv, n = opts[k][:2]
            kw[n] = argv.pop(0) if reqv else True
        except:
            if not argv:
                kw['filename'] = k
            else:
                die('Not understood: %s' % k)
    return kw


# code analysis for hilite:
try:
    from pygments import lex, token
    from pygments.lexers import get_lexer_by_name
    from pygments.lexers import guess_lexer as pyg_guess_lexer

    have_pygments = True
except ImportError:  # pragma: no cover
    have_pygments = False


if PY3:
    unichr = chr
    from html.parser import HTMLParser

    string_type = str
else:
    from HTMLParser import HTMLParser

    string_type = basestring

    def breakpoint():
        import pdb

        pdb.set_trace()


if getattr(HTMLParser, 'unescape', None) is None:
    from html import unescape
else:
    unescape = HTMLParser().unescape


from xml.etree.ElementTree import Element

if getattr(Element, 'getchildren', None) is None:
    get_element_children = lambda el: el
else:
    get_element_children = lambda el: el.getchildren()

is_app = 0

def_enc_set = False


def fix_py2_default_encoding():
    """ can be switched off when used as library"""
    if PY3:
        return
    global def_enc_set
    if not def_enc_set:
        # Make Py2 > Py3:
        import imp

        imp.reload(sys)
        sys.setdefaultencoding('utf-8')
        # no? see http://stackoverflow.com/a/29832646/4583360 ...
        def_enc_set = True


import logging

md_logger = logging.getLogger('MARKDOWN')
md_logger.setLevel(logging.WARNING)


# below here you have to *know* what u r doing... (since I didn't too much)

dir_mon_filepath_ph = '_fp_'
dir_mon_content_raw = '_raw_'
dir_mon_content_pretty = '_pretty_'


def readfile(fn, kw={'encoding': 'utf-8'} if PY3 else {}):
    with io.open(fn, **kw) as fd:
        return fd.read()


def read_themes():
    if not themes:
        themes.update(loads(readfile(j(mydir, 'ansi_tables.json'))))
    return themes


you_like = 'You like this theme?'


def make_sample():
    """ Generate the theme roller sample markdown """
    if md_sample:
        # user has set another:
        return md_sample
    _md = []
    for hl in range(1, 7):
        _md.append('#' * hl + ' ' + 'Header %s' % hl)
    sample_code = '''class Foo:
    bar = 'baz'
    '''
    _md.append('```python\n""" Doc String """\n%s\n```' % sample_code)
    _md.append(
        '''
| Tables        | Fmt |
| -- | -- |
| !!! hint: wrapped | 0.1 **strong** |
    '''
    )
    for ad in list(admons.keys())[:1]:
        _md.append('!!! %s: title\n    this is a %s\n' % (ad, ad.capitalize()))
    # 'this theme' replaced in the roller (but not at mdv w/o args):
    globals()['md_sample'] = '\n'.join(_md) + '\n----\n!!! question: %s' % you_like


code_hl_tokens = {}


def build_hl_by_token():
    if not have_pygments:
        return
    # replace code strs with tokens:
    for k, col in list(code_hl.items()):
        code_hl_tokens[getattr(token, k)] = globals()[col]


def clean_ansi(s):
    # if someone does not want the color foo:
    ansi_escape = re.compile(r'\x1b[^m]*m')
    return ansi_escape.sub('', s)


# markers: tab is 09, omit that
code_start, code_end = '\x07', '\x08'
stng_start, stng_end = '\x16', '\x10'
link_start, link_end = '\x17', '\x18'
emph_start, emph_end = '\x11', '\x12'
punctuationmark = '\x13'
fenced_codemark = '\x14'
hr_marker = '\x15'
no_split = '\x19'


def j(p, f):
    return os.path.join(p, f)


mydir = os.path.realpath(__file__).rsplit(os.path.sep, 1)[0]


def set_theme(theme=None, for_code=None, theme_info=None):
    """ set md and code theme """
    # for md the default is None and should return the 'random' theme
    # for code the default is 'default' and should return the default theme.
    # historical reasons...
    dec = {
        False: {'dflt': None, 'on_dflt': 'random', 'env': ('MDV_THEME', 'AXC_THEME'),},
        True: {
            'dflt': 'default',
            'on_dflt': None,
            'env': ('MDV_CODE_THEME', 'AXC_CODE_THEME'),
        },
    }
    dec = dec[bool(for_code)]
    try:
        if theme == dec['dflt']:
            for k in dec['env']:
                ek = envget(k)
                if ek:
                    theme = ek
                    break
        if theme == dec['dflt']:
            theme = dec['on_dflt']
        if not theme:
            return

        theme = str(theme)
        # all the themes from here:
        themes = read_themes()
        if theme == 'random':
            rand = randint(0, len(themes) - 1)
            theme = list(themes.keys())[rand]
        t = themes.get(theme)
        if not t or len(t.get('ct')) != 5:
            # leave defaults:
            return
        _for = ''
        if for_code:
            _for = ' (code)'

        if theme_info:
            print(low('theme%s: %s (%s)' % (_for, theme, t.get('name'))))

        t = t['ct']
        cols = (t[0], t[1], t[2], t[3], t[4])
        if for_code:
            global CH1, CH2, CH3, CH4, CH5
            CH1, CH2, CH3, CH4, CH5 = cols
        else:
            global H1, H2, H3, H4, H5
            # set the colors now from the ansi codes in the theme:
            H1, H2, H3, H4, H5 = cols
    finally:
        if for_code:
            build_hl_by_token()


def style_ansi(raw_code, lang=None):
    """ actual code hilite """

    def lexer_alias(n):
        # markdown lib now creates "language-python" (pygments still wants "python")
        if n.startswith('language-'):
            n = n[9:]
        # not found:
        if n == 'markdown':
            return 'md'
        return n

    lexer = 0
    if lang:
        try:
            lexer = get_lexer_by_name(lexer_alias(lang))
        except Exception as ex:
            print(col(str(ex), R), file=sys.stderr)

    if not lexer:
        try:
            if guess_lexer:
                # takes a long time!
                lexer = pyg_guess_lexer(raw_code)
        except:
            pass

    if not lexer:
        for l in def_lexer, 'yaml', 'python', 'c':
            try:
                lexer = get_lexer_by_name(lexer_alias(l))
                break
            except:
                # OUR def_lexer (python) was overridden,but not found.
                # still we should not fail. lets use yaml. or python:
                continue

    tokens = lex(raw_code, lexer)
    cod = []
    for t, v in tokens:
        if not v:
            continue
        _col = code_hl_tokens.get(t) or C  # color
        cod.append(col(v, _col))
    return ''.join(cod)


def col_bg(c):
    """ colorize background """
    return '\033[48;5;%sm' % c


def col(s, c, bg=0, no_reset=0):
    """
    print col('foo', 124) -> red 'foo' on the terminal
    c = color, s the value to colorize """
    reset = reset_col
    if no_reset:
        reset = ''
    for _strt, _end, _col in (
        (code_start, code_end, H2),
        (stng_start, stng_end, H2),
        (link_start, link_end, H2),
        (emph_start, emph_end, H3),
    ):

        if _strt in s:
            uon, uoff = '', ''
            if _strt == link_start:
                uon, uoff = '\033[4m', '\033[24m'
            s = s.replace(_strt, col('', _col, bg=background, no_reset=1) + uon)
            s = s.replace(_end, uoff + col('', c, no_reset=1))

    s = '\033[38;5;%sm%s%s' % (c, s, reset)
    if bg:
        pass
        # s = col_bg(bg) + s
    return s


reset_col = '\033[0m'


def low(s):
    # shorthand
    return col(s, L)


def plain(s, **kw):
    # when a tag is not found:
    return col(s, T)


def sh(out):
    """ debug tool"""
    for l in out:
        print(l)


# --------------------------------------------------------- Tag formatter funcs

# number these header levels:
header_nr = {'from': 0, 'to': 0}
# current state scanning the document:
cur_header_state = {i: 0 for i in range(1, 11)}


def reset_cur_header_state():
    """after one document is complete"""
    [into(cur_header_state, i, 0) for i in range(1, 11)]


def parse_header_nrs(nrs):
    'nrs e.g. "4-10" or "1-"'
    if not nrs:
        return
    if isinstance(nrs, dict):
        return header_nr.update(nrs)
    if isinstance(nrs, string_type):
        if nrs.startswith('-'):
            nrs = '1' + nrs
        if nrs.endswith('-'):
            nrs += '10'
        if not '-' in nrs:
            nrs += '-10'
        nrs = nrs.split('-')[0:2]
    try:
        if isinstance(nrs, (tuple, list)):
            header_nr['from'] = int(nrs[0])
            header_nr['to'] = int(nrs[1])
            return
    except Extension as ex:
        errout('header numbering not understood', nrs)
        sys.exit(1)


def into(m, k, v):
    m[k] = v


class Tags:
    _last_header_level = 0
    """ can be overwritten in derivations. """

    def update_header_state(_, level):
        cur = cur_header_state
        if _._last_header_level > level:
            [into(cur, i, 0) for i in range(level + 1, 10)]

        for l in range(_._last_header_level + 1, level):
            if cur[l] == 0:
                cur[l] = 1
        cur[level] += 1
        _._last_header_level = level
        ret = ''
        f, t = header_nr['from'], header_nr['to']
        if level >= f and level <= t:
            ret = '.'.join([str(cur[i]) for i in range(f, t + 1) if cur[i] > 0])
        return ret

    # @staticmethod everywhere is eye cancer, so we instantiate it later
    def h(_, s, level, **kw):
        """we set h1 to h10 formatters calling this when we do tag = Tag()"""
        nrstr = _.update_header_state(level)
        if nrstr:
            # if we have header numbers we don't indent the text yet more:
            s = ' ' + s.lstrip()
        # have not more colors:
        header_col = min(level, 5)
        return '\n%s%s%s' % (
            low('#' * 0),
            nrstr,
            col(s, globals()['H%s' % header_col]),
        )

    def p(_, s, **kw):
        return col(s, T)

    def a(_, s, **kw):
        return col(s, L)

    def hr(_, s, **kw):
        # we want nice line seps:
        hir = kw.get('hir', 1)
        ind = (hir - 1) * left_indent
        s = e = col(hr_ends, globals()['H%s' % hir])
        return low('\n%s%s%s%s%s\n' % (ind, s, hr_marker, e, ind))

    def code(_, s, from_fenced_block=None, **kw):
        """ md code AND ``` style fenced raw code ends here"""
        lang = kw.get('lang')
        if not from_fenced_block:
            s = ('\n' + s).replace('\n    ', '\n')[1:]

        # funny: ":-" confuses the tokenizer. replace/backreplace:
        raw_code = s.replace(':-', '\x01--')
        if have_pygments:
            s = style_ansi(raw_code, lang=lang)

        # outest hir is 2, use it for fenced:
        ind = ' ' * kw.get('hir', 2)
        # if from_fenced_block: ... WE treat equal.

        # shift to the far left, no matter the indent (screenspace matters):
        firstl = s.split('\n')[0]
        del_spaces = ' ' * (len(firstl) - len(firstl.lstrip()))
        s = ('\n' + s).replace('\n%s' % del_spaces, '\n')[1:]

        # we want an indent of one and low vis prefix. this does it:
        code_lines = ('\n' + s).splitlines()
        prefix = '\n%s%s %s' % (ind, low(code_pref), col('', C, no_reset=1))
        code_lines.pop() if code_lines[-1] == '\x1b[0m' else None
        code = prefix.join(code_lines)
        code = code.replace('\x01--', ':-')
        return code + '\n' + reset_col


if PY3:
    elstr = lambda el: etree.tostring(el).decode('utf-8')
else:
    elstr = lambda el: etree.tostring(el)


def is_text_node(el):
    """ """
    s = elstr(el)
    # strip our tag:
    html = s.split('<%s' % el.tag, 1)[1].split('>', 1)[1].rsplit('>', 1)[0]
    # do we start with another tagged child which is NOT in inlines:?
    if not html.startswith('<'):
        return 1, html
    for inline in ('<a', '<em>', '<code>', '<strong>'):
        if html.startswith(inline):
            return 1, html
    return 0, 0


# ----------------------------------------------------- Text Termcols Adaptions
def rewrap(el, t, ind, pref):
    """ Reasonably smart rewrapping checking punctuations """
    cols = max(term_columns - len(ind + pref), 5)
    if el.tag == 'code' or len(t) <= cols:
        return t

    # this is a code replacement marker of markdown.py. Don't split the
    # replacement marker:
    if t.startswith('\x02') and t.endswith('\x03'):
        return t

    dedented = textwrap.dedent(t).strip()
    ret = textwrap.fill(dedented, width=cols)
    return ret

    # forgot why I didn't use textwrap from the beginning. In case there is a
    # reason I leave the old code here:
    # edit: think it was because of ansi code unawareness of textwrap.
    # wrapping:
    # we want to keep existing linebreaks after punctuation
    # marks. the others we rewrap:

    # puncs = ',', '.', '?', '!', '-', ':'
    # parts = []
    # origp = t.splitlines()
    # if len(origp) > 1:
    #    pos = -1
    #    while pos < len(origp) - 1:
    #        pos += 1
    #        # last char punctuation?
    #        if origp[pos][-1] not in puncs and \
    #                not pos == len(origp) - 1:
    #            # concat:
    #            parts.append(origp[pos].strip() + ' ' + origp[pos + 1].strip())
    #            pos += 1
    #        else:
    #            parts.append(origp[pos].strip())
    #    t = '\n'.join(parts)
    ## having only the linebreaks with puncs before we rewrap
    ## now:
    # parts = []
    # for part in t.splitlines():
    #    parts.extend([part[i:i+cols] for i in range(0, len(part), cols)])
    ## last remove leading ' ' (if '\n' came just before):
    # t = []
    # for p in parts:
    #    t.append(p.strip())
    # return '\n'.join(t)


def split_blocks(text_block, w, cols, part_fmter=None):
    """ splits while multiline blocks vertically (for large tables) """
    ts = []
    for line in text_block.splitlines():
        parts = []
        # make equal len:
        line = line.ljust(w, ' ')
        # first part full width, others a bit indented:
        parts.append(line[:cols])
        scols = cols - 2
        # the txt_block_cut in low makes the whole secondary tables
        # low. which i find a feature:
        # if you don't want it remove the col(.., L)
        parts.extend(
            [
                ' ' + col(txt_block_cut, L, no_reset=1) + line[i : i + scols]
                for i in range(cols, len(line), scols)
            ]
        )
        ts.append(parts)

    blocks = []
    for block_part_nr in range(len(ts[0])):
        tpart = []
        for lines_block in ts:
            tpart.append(lines_block[block_part_nr])
        if part_fmter:
            part_fmter(tpart)
        tpart[1] = col(tpart[1], H3)
        blocks.append('\n'.join(tpart))
    t = '\n'.join(blocks)
    return '\n%s\n' % t


# ---------------------------------------------------- Create the treeprocessor
def replace_links(el, html):
    """digging through inline "<a href=..."
    """
    parts = html.split('<a ')
    if len(parts) == 1:
        return None, html
    links_list, cur_link = [], 0
    links = [l for l in get_element_children(el) if 'href' in l.keys()]
    if not len(parts) == len(links) + 1:
        # there is an html element within which we don't support,
        # e.g. blockquote
        return None, html
    cur = ''
    while parts:
        cur += parts.pop(0).rsplit('</a>')[-1]
        if not parts:
            break

        # indicating link formatting start:
        cur += link_start

        # the 'a' xml element:
        link = links[cur_link]

        # bug in the markdown api? link el is not providing inlines!!
        # -> get them from the html:
        # cur += link.text or ''
        cur += parts[0].split('>', 1)[1].split('</a', 1)[0] or ''
        cur += link_end
        if show_links != 'h':
            if show_links == 'i':
                cur += low('(%s)' % link.get('href', ''))
            else:  # inline table (it)
                # we build a link list, add the number like ① :
                try:
                    cur += '%s ' % unichr(link_start_ord + cur_link)
                except NameError:
                    # fix for py3
                    # http://stackoverflow.com/a/2352047
                    cur += '%s ' % chr(link_start_ord + cur_link)
                links_list.append(link.get('href', ''))
        cur_link += 1
    return links_list, cur


class AnsiPrinter(Treeprocessor):
    header_tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')

    def run(self, doc):
        tags = Tags()
        for h in cur_header_state:
            setattr(tags, 'h%s' % h, partial(tags.h, level=h))

        def get_attr(el, attr):
            for c in list(el.items()):
                if c[0] == attr:
                    return c[1]
            return ''

        def formatter(el, out, hir=0, pref='', parent=None):
            """
            Main recursion.

            debugging:
            if el.tag == 'code':
                import pdb

                pdb.set_trace()
                # for c in get_element_children(get_element_children(el)[0]): print c.text, c
            print('---------')
            print(el, el.text)
            print('---------')
            """
            if el.tag == 'br':
                out.append('\n')
                return
            # for c in get_element_children(el): print c.text, c
            links_list, is_txt_and_inline_markup = None, 0
            if el.tag == 'blockquote':
                for el1 in get_element_children(el):
                    iout = []
                    formatter(el1, iout, hir + 2, parent=el)
                    pr = col(bquote_pref, H1)
                    sp = ' ' * (hir + 2)
                    for l in iout:
                        for l1 in l.splitlines():
                            if sp in l1:
                                l1 = ''.join(l1.split(sp, 1))
                            out.append(pr + l1)
                return

            if el.tag == 'hr':
                return out.append(tags.hr('', hir=hir))

            if el.text or el.tag == 'p' or el.tag == 'li' or el.tag.startswith('h'):
                el.text = el.text or ''
                # <a attributes>foo... -> we want "foo....". Is it a sub
                # tag or inline text?
                if el.tag == 'code':
                    t = unescape(el.text)
                else:
                    is_txt_and_inline_markup, html = is_text_node(el)

                    if is_txt_and_inline_markup:
                        # foo:  \nbar -> will be seing a foo:<br>bar with
                        # mardkown.py. Code blocks are already quoted -> no prob.
                        html = html.replace('<br />', '\n')
                        # strip our own closing tag:
                        t = html.rsplit('<', 1)[0]
                        links_list, t = replace_links(el, html=t)
                        for tg, start, end in (
                            ('<code>', code_start, code_end),
                            ('<strong>', stng_start, stng_end),
                            ('<em>', emph_start, emph_end),
                        ):
                            t = t.replace('%s' % tg, start)
                            close_tag = '</%s' % tg[1:]
                            t = t.replace(close_tag, end)
                        t = unescape(t)
                    else:
                        t = el.text
                t = t.strip()
                admon = ''
                pref = body_pref = ''
                if t.startswith('!!! '):
                    # we allow admons with spaces. so check for startswith:
                    _ad = None
                    for k in admons:
                        if t[4:].startswith(k):
                            _ad = k
                            break
                    # not found - markup using hte first one's color:
                    if not _ad:
                        k = t[4:].split(' ', 1)[0]
                        admons[k] = list(admons.values())[0]

                    pref = body_pref = '┃ '
                    pref += k.capitalize()
                    admon = k
                    t = t.split(k, 1)[1]

                # set the parent, e.g. nrs in ols:
                if el.get('pref'):
                    # first line pref, like '-':
                    pref = el.get('pref')
                    # next line prefs:
                    body_pref = ' ' * len(pref)
                    el.set('pref', '')

                ind = left_indent * hir
                if el.tag in self.header_tags:
                    # header level:
                    hl = int(el.tag[1:])
                    ind = ' ' * (hl - 1)
                    hir += hl

                t = rewrap(el, t, ind, pref)

                # indent. can color the prefixes now, no more len checks:
                if admon:
                    out.append('\n')
                    pref = col(pref, globals()[admons[admon]])
                    body_pref = col(body_pref, globals()[admons[admon]])

                if pref:
                    # different color per indent:
                    h = globals()['H%s' % (((hir - 2) % 5) + 1)]
                    if pref == list_pref:
                        pref = col(pref, h)
                    elif pref.split('.', 1)[0].isdigit():
                        pref = col(pref, h)

                t = ('\n' + ind + body_pref).join((t).splitlines())
                t = ind + pref + t

                # headers outer left: go sure.
                # actually... NO. commented out.
                # if el.tag in self.header_tags:
                #    pref = ''

                # calling the class Tags  functions
                # IF the parent is li and we have a linebreak then the renderer
                # delivers <li><p>foo</p> instead of <li>foo, i.e. we have to
                # omit the linebreak and append the text of p to the previous
                # result, (i.e. the list separator):
                tag_fmt_func = getattr(tags, el.tag, plain)
                if (
                    type(parent) == type(el)
                    and parent.tag == 'li'
                    and not parent.text
                    and el.tag == 'p'
                ):
                    _out = tag_fmt_func(t.lstrip(), hir=hir)
                    out[-1] += _out
                else:
                    out.append(tag_fmt_func(t, hir=hir))

                if admon:
                    out.append('\n')

                if links_list:
                    i = 1
                    for l in links_list:
                        out.append(low('%s[%s] %s' % (ind, i, l)))
                        i += 1

            # have children?
            #    nr for ols:
            if is_txt_and_inline_markup:
                if el.tag == 'li':
                    childs = get_element_children(el)
                    for nested in 'ul', 'ol':
                        if childs and childs[-1].tag == nested:
                            ul = childs[-1]
                            # do we have a nested sublist? the li was inline
                            # formattet,
                            # split all from <ul> off and format it as own tag:
                            # (ul always at the end of an li)
                            out[-1] = out[-1].split('<%s>' % nested, 1)[0]
                            formatter(ul, out, hir + 1, parent=el)
                return

            if el.tag == 'table':
                # processed all here, in one sweep:
                # markdown ext gave us a xml tree from the ascii,
                # our part here is the cell formatting and into a
                # python nested list, then tabulate spits
                # out ascii again:
                def borders(t):
                    t[0] = t[-1] = low(t[0].replace('-', '─'))

                def fmt(cell, parent):
                    """ we just run the whole formatter - just with a fresh new
                    result list so that our 'out' is untouched """
                    _cell = []
                    formatter(cell, out=_cell, hir=0, parent=parent)
                    return '\n'.join(_cell)

                t = []
                for he_bo in 0, 1:
                    for Row in get_element_children(el[he_bo]):
                        row = []
                        t.append(row)
                        for cell in get_element_children(Row):
                            row.append(fmt(cell, row))
                cols = term_columns
                # good ansi handling:
                tbl = tabulate(t)

                # do we have right room to indent it?
                # first line is seps, so no ansi esacapes foo:
                w = len(tbl.split('\n', 1)[0])
                if w <= cols:
                    t = tbl.splitlines()
                    borders(t)
                    # center:
                    ind = (cols - w) / 2
                    # too much:
                    ind = hir
                    tt = []
                    for line in t:
                        tt.append('%s%s' % (ind * left_indent, line))
                    out.extend(tt)
                else:
                    # TABLE CUTTING WHEN NOT WIDTH FIT
                    # oh snap, the table bigger than our screen. hmm.
                    # hey lets split into vertical parts:
                    # but len calcs are hart, since we are crammed with esc.
                    # seqs.
                    # -> get rid of them:
                    tc = []
                    for row in t:
                        tc.append([])
                        l = tc[-1]
                        for cell in row:
                            l.append(clean_ansi(cell))
                    # again sam:
                    # note: we had to patch it, it inserted '\n' within cells!
                    table = tabulate(tc)
                    out.append(split_blocks(table, w, cols, part_fmter=borders))
                return

            nr = 0
            for c in el:
                if el.tag == 'ul':  # or el.tag == 'li':
                    c.set('pref', list_pref)
                elif el.tag == 'ol':
                    nr += 1
                    c.set('pref', str(nr) + '. ')

                # handle the ``` style unindented code blocks -> parsed as p:
                formatter(c, out, hir + 1, parent=el)
            # if el.tag == 'ul' or el.tag == 'ol' and not out[-1] == '\n':
            #    out.append('\n')

        out = []
        formatter(doc, out)
        self.md.ansi = '\n'.join(out)


def set_hr_widths(result):
    """
    We want the hrs indented by hirarchy...
    A bit 2 much effort to calc, maybe just fixed with 10
    style seps would have been enough visually:
    ◈────────────◈
    """
    # set all hrs to max width of text:
    mw = 0
    hrs = []
    if hr_marker not in result:
        return result
    for line in result.splitlines():
        if hr_marker in line:
            hrs.append(line)
            continue
        if len(line) < mw:
            continue
        l = len(clean_ansi(line))
        if l > mw:
            mw = l

    for hr in hrs:
        # pos of hr marker is indent, derives full width:
        # (more indent = less '-'):
        hcl = clean_ansi(hr)
        ind = len(hcl) - len(hcl.split(hr_marker, 1)[1]) - 1
        w = min(term_columns, mw) - 2 * ind
        hrf = hr.replace(hr_marker, hr_sep * w)
        result = result.replace(hr, hrf)
    return result


# Then tell markdown about it
class AnsiPrintExtension(Extension):
    def extendMarkdown(self, md):
        ansi_print_ext = AnsiPrinter(md)
        md.treeprocessors.register(ansi_print_ext, 'ansi_print_ext', 15)


def do_code_hilite(md, what='all'):
    """
    "inverse" mode for source code highlighting:
    the file contains mainly code and md is within docstrings
    what in  all, code, doc, mod
    """
    if what not in ('all', 'code', 'doc', 'mod'):
        what = 'all'
    code_mode, md_mode = 1, 2
    blocks, block, mode = [], [], code_mode
    blocks.append([mode, block])
    lines = ('\n' + md).splitlines()
    mdstart = '\x01'
    while lines:
        line = lines.pop(0)
        if mode == code_mode:
            if line.rstrip() in ('"""_', "'''_", '/*_'):
                mdstart = line.rstrip()[:-1]
                mode = md_mode
                block = []
                if mdstart == '/*':
                    mdstart = '*/'
                blocks.append([md_mode, block])
                continue

        elif line.rstrip() == mdstart:
            if what == 'doc':
                # only module level docstring:
                break
            mode = code_mode
            block = []
            blocks.append([code_mode, block])
            continue

        if mode == code_mode:
            if what in ('all', 'code'):
                block.append(line)

        elif what != 'code':
            block.append(line)

    out = []
    for mode, block in blocks:
        b = '\n'.join(block)
        if not b:
            continue
        if mode == code_mode:
            out.append('```\n%s\n```' % b)
        else:
            out.append('\n'.join(block))
    return '\n'.join(out)


# fmt: off
def main(
    md               = None,
    filename         = None,
    encoding         = 'utf-8',
    cols             = None,
    theme            = None,
    c_theme          = None,
    bg               = None,
    c_no_guess       = None,
    display_links    = None,
    link_style       = None,
    from_txt         = None,
    do_html          = None,
    code_hilite      = None,
    c_def_lexer      = None,
    theme_info       = None,
    no_colors        = None,
    tab_length       = 4,
    no_change_defenc = False,
    header_nrs       = False,
    **kw
):
    """ md is markdown string. alternatively we use filename and read """
    # fmt: on

    # if I don't do this here, then I'll get probs when being
    # used as a lib:
    # https://github.com/axiros/terminal_markdown_viewer/issues/39
    # If you hate it then switch it off but don't blame me on unicode errs.
    True if no_change_defenc else fix_py2_default_encoding()

    parse_header_nrs(header_nrs)

    tab_length = tab_length or 4
    global def_lexer
    if c_def_lexer:
        def_lexer = c_def_lexer
    py_config_file = os.path.expanduser("~/.mdv.py")
    if os.path.exists(py_config_file):
        exec_globals = {}
        exec(io.open(py_config_file, encoding="utf-8").read(), exec_globals)
        globals().update(exec_globals)

    args = locals()
    if not md:
        if not filename:
            print("Using sample markdown:")
            make_sample()
            md = args["md"] = md_sample
            print(md)
            print
            print("Styling Result")
        else:
            if filename == "-":
                md = sys.stdin.read()
            else:
                with io.open(filename, encoding=encoding) as f:
                    md = f.read()

    # style rolers requested?
    global term_columns
    if cols:
        term_columns = int(cols)

    if c_theme == "all" or theme == "all":
        if c_theme == "all":
            os.environ["AXC_CODE_THEME"] = os.environ["MDV_CODE_THEME"] = ""
        if theme == "all":
            os.environ["AXC_THEME"] = os.environ["MDV_THEME"] = ""
        args.pop("kw")
        themes = read_themes()
        for k, v in list(themes.items()):
            if not filename:
                yl = "You like *%s*, *%s*?" % (k, v["name"])
                args["md"] = md_sample.replace(you_like, yl)
            print(col("%s%s%s" % ("\n\n", "=" * term_columns, "\n"), L))
            # should really create an iterator here:
            if theme == "all":
                args["theme"] = k
            else:
                args["c_theme"] = k
            print(main(**args))
        return ""

    global show_links
    if display_links:
        show_links = "i"
    if link_style:  # rules
        show_links = link_style

    if bg and bg == "light":
        # not in use rite now:
        global background, color
        background = BGL
        color = T

    set_theme(theme, theme_info=theme_info)

    global guess_lexer
    guess_lexer = not c_no_guess

    if not c_theme:
        c_theme = theme or "default"

    if c_theme == "None":
        c_theme = None

    if c_theme:
        set_theme(c_theme, for_code=1, theme_info=theme_info)

    if c_theme:
        # info:
        if not have_pygments:
            errout(col("No pygments, can not analyze code for hilite", R))

    # Create an instance of the Markdown class with the new extension
    MD = markdown.Markdown(
        tab_length=int(tab_length),
        extensions=[
            AnsiPrintExtension(),
            TableExtension(),
            fenced_code.FencedCodeExtension(),
        ],
    )


    if code_hilite:
        md = do_code_hilite(md, code_hilite)
    the_html = MD.convert(md)
    reset_cur_header_state()
    # print the_html
    # html?
    if do_html:
        return the_html

    # who wants html, here is our result:
    ansi = MD.ansi

    # The RAW html within source, incl. fenced code blocks:
    # phs are numbered like this in the md, we replace back:
    PH = markdown.util.HTML_PLACEHOLDER
    stash = MD.htmlStash
    nr = -1
    tags = Tags()
    for ph in stash.rawHtmlBlocks:
        nr += 1
        raw = unescape(ph)
        if raw[:3].lower() == "<br":
            raw = "\n"
        pre = "<pre><code"
        if raw.startswith(pre):
            _, raw = raw.split(pre, 1)
            if 'class="' in raw:
                # language:
                lang = raw.split('class="', 1)[1].split('"')[0]
            else:
                lang = ""
            raw = raw.split(">", 1)[1].rsplit("</code>", 1)[0]
            raw = tags.code(raw.strip(), from_fenced_block=1, lang=lang)
        ansi = ansi.replace(PH % nr, raw)

    # don't want these: gone through the extension now:
    # ansi = ansi.replace('```', '')

    # sub part display (the -f feature)
    if from_txt:
        if not from_txt.split(":", 1)[0] in ansi:
            # display from top then:
            from_txt = ansi.strip()[1]
        from_txt, mon_lines = (from_txt + ":%s" % (term_rows - 6)).split(":")[
            :2
        ]
        mon_lines = int(mon_lines)
        pre, post = ansi.split(from_txt, 1)
        post = "\n".join(post.split("\n")[:mon_lines])
        ansi = "\n(...)%s%s%s" % (
            "\n".join(pre.rsplit("\n", 2)[-2:]),
            from_txt,
            post,
        )

    ansi = set_hr_widths(ansi) + "\n"
    if no_colors:
        return clean_ansi(ansi)
    return ansi + "\n"


# Following just file monitors, not really core feature so the prettyfier:
# but sometimes good to have at hand:
# ---------------------------------------------------------------- File Monitor
def monitor(args):
    """ file monitor mode """
    filename = args.get("filename")
    if not filename:
        print(col("Need file argument", 2))
        raise SystemExit
    last_err = ""
    last_stat = 0
    while True:
        if not os.path.exists(filename):
            last_err = "File %s not found. Will continue trying." % filename
        else:
            try:
                stat = os.stat(filename)[8]
                if stat != last_stat:
                    parsed = main(**args)
                    print(str(parsed))
                    last_stat = stat
                last_err = ""
            except Exception as ex:
                last_err = str(ex)
        if last_err:
            errout("Error: %s" % last_err)
        sleep()


def sleep():
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        errout("Have a nice day!")
        raise SystemExit


# ----------------------------------------------------------- Directory Monitor
def run_changed_file_cmd(cmd, fp, pretty):
    """ running commands on changes.
        pretty the parsed file
    """
    with io.open(fp, encoding="utf-8") as f:
        raw = f.read()
    # go sure regarding quotes:
    for ph in (
        dir_mon_filepath_ph,
        dir_mon_content_raw,
        dir_mon_content_pretty,
    ):
        if ph in cmd and not ('"%s"' % ph) in cmd and not ("'%s'" % ph) in cmd:
            cmd = cmd.replace(ph, '"%s"' % ph)

    cmd = cmd.replace(dir_mon_filepath_ph, fp)
    errout(col("Running %s" % cmd, H1))
    for r, what in (
        (dir_mon_content_raw, raw),
        (dir_mon_content_pretty, pretty),
    ):
        cmd = cmd.replace(r, what.encode("base64"))

    # yeah, i know, sub bla bla...
    if os.system(cmd):
        errout(col("(the command failed)", R))


def monitor_dir(args):
    """ displaying the changed files """

    def show_fp(fp):
        args["filename"] = fp
        pretty = main(**args)
        print(pretty)
        print("(%s)" % col(fp, L))
        cmd = args.get("change_cmd")
        if cmd:
            run_changed_file_cmd(cmd, fp=fp, pretty=pretty)

    ftree = {}
    d = args.get("monitor_dir")
    # was a change command given?
    d += "::"
    d, args["change_cmd"] = d.split("::")[:2]
    args.pop("monitor_dir")
    # collides:
    args.pop("monitor_file", 0)
    d, exts = (d + ":md,mdown,markdown").split(":")[:2]
    exts = exts.split(",")
    if not os.path.exists(d):
        print(col("Does not exist: %s" % d, R))
        sys.exit(2)

    dir_black_list = [".", ".."]

    def check_dir(d, ftree):
        check_latest = ftree.get("latest_ts")
        d = os.path.abspath(d)
        if d in dir_black_list:
            return

        if len(ftree) > mon_max_files:
            # too deep:
            print(col("Max files (%s) reached" % col(mon_max_files, R)))
            dir_black_list.append(d)
            return
        try:
            files = os.listdir(d)
        except Exception as ex:
            print("%s when scanning dir %s" % (col(ex, R), d))
            dir_black_list.append(d)
            return

        for f in files:
            fp = j(d, f)
            if os.path.isfile(fp):
                f_ext = f.rsplit(".", 1)[-1]
                if f_ext == f:
                    f_ext == ""
                if f_ext not in exts:
                    continue
                old = ftree.get(fp)
                # size:
                now = os.stat(fp)[6]
                if check_latest:
                    if os.stat(fp)[7] > ftree["latest_ts"]:
                        ftree["latest"] = fp
                        ftree["latest_ts"] = os.stat(fp)[8]
                if now == old:
                    continue
                # change:
                ftree[fp] = now
                if not old:
                    # At first time we don't display ALL the files...:
                    continue
                # no binary. make sure:
                if "text" in os.popen('file "%s"' % fp).read():
                    show_fp(fp)
            elif os.path.isdir(fp):
                check_dir(j(d, fp), ftree)

    ftree["latest_ts"] = 1
    while True:
        check_dir(d, ftree)
        if "latest_ts" in ftree:
            ftree.pop("latest_ts")
            fp = ftree.get("latest")
            if fp:
                show_fp(fp)
            else:
                print("sth went wrong, no file found")
        sleep()


def load_config(filename, s=None, yaml=None):
    fns = (filename,) if filename else ('.mdv', '.config/mdv')
    for f in fns:
        fn = os.path.expanduser('~/' + f) if f[0] == '.' else f
        if not os.path.exists(fn):
            if filename:
                die('Not found: %s' % filename)
            else:
                continue
        with io.open(fn, encoding="utf-8") as fd:
            s = fd.read()
            break
    if not s:
        return {}
    try:
        import yaml
        m = yaml.safe_load(s)
    except:
        import json
        try:
            m = json.loads(s)
        except:
            errout('could not parse config at %s. Have yaml: %s' % (fn, yaml))
            if filename:
                sys.exit(1)
            m = {}
    return m

# backwards compat - this was there before:
load_yaml_config = load_config

def merge(a, b):
    c = a.copy()
    c.update(b)
    return c


# fmt: on
def run():
    global is_app
    is_app = 1
    fix_py2_default_encoding() if not PY3 else None
    kw = load_config(None) or {}
    kw1 = parse_env_and_cli()
    fn = kw1.get('config_file')
    if fn:
        kw.update(load_config(filename=fn))
    kw.update(kw1)
    doc = __doc__[1:]
    if kw.get('sh_help'):
        d = dict(
            theme=671.1616,
            ctheme=526.9416,
            c_no_guess=True,
            c_def_lexer='md',
            header_nrs='1-',
            md=doc,
        )
        d.update(kw)
        res = main(**d)
        d['header_nrs'] = '0-0'
        d['md'] = '-----' + doc.split('# Details', 1)[0]
        res += main(**d)
        print(res if PY3 else str(res))
        sys.exit(0)
    if kw.get('monitor_file'):
        monitor(kw)
    elif kw.get('monitor_dir'):
        monitor_dir(kw)
    else:
        print(main(**kw) if PY3 else str(main(**kw)))


if __name__ == '__main__':  # pragma: no cover
    # the setup tools version calls directly run, this is for git checkouts:
    run()
