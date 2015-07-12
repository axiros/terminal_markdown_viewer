#!/usr/bin/env python
# coding: utf-8

"""
Usage:
    mdv [-t THEME] [-T C_THEME] [-x] [-l] [-L] [-c COLS] [-m] [MDFILE]

Options:
    MDFIlE    : path to markdown file
    -t THEME  : key within the color ansi_table.json. 'random' accepted.
    -T C_THEME: pygments theme for code highlight. If not set: Use THEME.
    -l        : light background (not yet supported)
    -L        : display links
    -x        : Do not try guess code lexer (guessing is a bit slow)
    -m        : Monitor file for changes and redisplay
    -c COLS   : fix columns to this (default: your terminal width)

Notes:

    Call the main function with markdown string at hand to get a formatted one
    back

    Theme rollers:
    mdv -T all:  All available code styles on the given file.
    mdv -t all:  All available md   styles on the given file.
                 If file is not given we use a short sample file.

    So to see all code hilite variations with a given theme:
        Say C_THEME = all and fix THEME
    Setting both to all will probably spin your beach ball, at least on OSX.
"""

if __name__ == '__main__':
    # Make Py2 > Py3:
    import os, sys; reload(sys); sys.setdefaultencoding('utf-8')
    # no? see http://stackoverflow.com/a/29832646/4583360 ...


# code analysis for hilite:
try:
    from pygments import lex, token
    from pygments.lexers import get_lexer_by_name, guess_lexer
    have_pygments = True
except ImportError:
    have_pygments = False

import time
import markdown, re
from docopt import docopt
import markdown.util
from markdown.util import etree
from markdown.extensions.tables import TableExtension
from random import randint
from tabulate import tabulate
from json import loads
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension, fenced_code
from HTMLParser import HTMLParser

# ---------------------------------------------------------------------- Config
txt_block_cut, code_pref, list_pref, br_ends = '✂', '░ ', '- ', '◈'
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
# also global. but not in use, BG handling can get pretty involved, to do with
# taste, since we don't know the term backg....:
background = BG

# hirarchical indentation by:
left_indent = '  '
# normal text color:
color = T

show_links = None

# columns(!) - may be set to smaller width:
try:
    term_rows, term_columns = os.popen('stty size', 'r').read().split()
    term_columns = int(term_columns)
except:
    print '!! Could not derive your terminal width !!'
    term_columns = 80

# could be given, otherwise read from ansi_tables.json:
themes = {}


# sample for the theme roller feature:
md_sample = ''

# ------------------------------------------------------------------ End Config
# below here you have to *know* what u r doing... (since I didn't too much)

def read_themes():
    if not themes:
        with open(j(mydir, 'ansi_tables.json')) as f:
            themes.update(loads(f.read()))
    return themes


# can unescape:
html_parser = HTMLParser()

def make_sample():
    """ theme roller """
    if md_sample:
        # user has set another:
        return md_sample
    _md = []
    for hl in range(1, 7): _md.append('#' * hl + ' ' + 'Header %s' % hl)
    this = open(__file__).read().split('"""', 3)[2].splitlines()[:10]
    _md.append('```python\n""" Test """\n%s\n```' % '\n'.join(this).strip())
    _md.append("""
| Tables            | Fmt            |
| -- | -- |
| !!! hint: wrapped | 0.1 **strong** |
    """)
    for ad in admons.keys()[:1]:
        _md.append('!!! %s: title\n    this is a %s\n' % (ad, ad.capitalize()))
    globals()['md_sample'] = \
              '\n'.join(_md) + '\n\n``You`` like **__id__**, *__name__*?\n'



code_hl_tokens = {}
def build_hl_by_token():
    # replace code strs with tokens:
    for k, col in code_hl.items():
        code_hl_tokens[getattr(token, k)] = globals()[col]


ansi_escape = re.compile(r'\x1b[^m]*m')
def clean_ansi(s):
    # if someone does not want the color foo:
    return ansi_escape.sub('', s)

# markers:
code_start, code_end = '\x07', '\x08'
stng_start, stng_end = '\x09', '\x10'
emph_start, emph_end = '\x11', '\x12'
punctuationmark      = '\x13'
fenced_codemark      = '\x14'

def j(p, f):
    return os.path.join(p, f)

mydir = os.path.abspath(__file__).rsplit('/', 1)[0]

def set_theme(theme=None, for_code=None):
    """ set md and code theme """
    try:
        if theme == 'default':
            return
        theme = theme or os.environ.get('AXC_THEME', 'random')
        # all the themes from here:
        themes = read_themes()
        if theme == 'random':
            rand = randint(0, len(themes)-1)
            theme = themes.keys()[rand]
        t = themes.get(theme)
        if not t or len(t.get('ct')) != 5:
            # leave defaults:
            return
        _for = ''
        if for_code:
            _for = ' (code)'
        print >> sys.stderr, low('theme%s: %s (%s)' % (_for, theme,
                                                       t.get('name')))
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
    for _strt, _end, _col in ((code_start, code_end, H2),
                              (stng_start, stng_end, H2),
                              (emph_start, emph_end, H3)):
        if _strt in s:
            # inline code:
            s = s.replace(_strt, col('', _col, bg=background, no_reset=1))
            s = s.replace(_end , col('', c, no_reset=1))

    s =  '\033[38;5;%sm%s%s' % (c, s, reset)
    if bg:
        pass
        #s = col_bg(bg) + s
    return s

reset_col = '\033[0m'

def low(s):
    # shorthand
    return col(s, L)

def plain(s, **kw):
    # when a tag is not found:
    return col(s, T)


# --------------------------------------------------------- Tag formatter funcs
class Tags:
    """ can be overwritten in derivations. """
    # @staticmethod everywhere is eye cancer, so we instantiate it later
    def h(_, s, level):
        return '\n%s%s' % (low('#' * 0), col(s, globals()['H%s' % level]))
    def h1(_, s, **kw): return _.h(s, 1)
    def h2(_, s, **kw): return _.h(s, 2)
    def h3(_, s, **kw): return _.h(s, 3)
    def h4(_, s, **kw): return _.h(s, 4)
    def h5(_, s, **kw): return _.h(s, 5)
    def h6(_, s, **kw): return _.h(s, 5) # have not more then 5
    def h7(_, s, **kw): return _.h(s, 5) # cols in the themes, low them all
    def h8(_, s, **kw): return _.h(s, 5)

    def p (_, s, **kw): return col(s, T)
    def a (_, s, **kw): return col(s, L)
    def hr(_, s, **kw):
        # we want nice line seps:
        hir = kw.get('hir', 1)
        ind = (hir - 1) * ' '
        l = term_columns - ((2 * len(ind)) + 2)
        s = e = col(br_ends, globals()['H%s' % hir])
        return low('\n%s%s%s%s%s\n' % (ind, s, '─' * l, e, ind))

    def code(_, s, from_fenced_block = None, **kw):
        """ md code AND ``` style fenced raw code ends here"""
        lang = kw.get('lang')

        raw_code = s
        if have_pygments:
            lexer = 0
            if lang:
                try:
                    lexer = get_lexer_by_name(lang)
                except ValueError:
                    print col(R, 'Lexer for %s not found' % lang)
            try:
                lexer = guess_lexer(raw_code)
            except:
                pass
            if not lexer:
                lexer = get_lexer_by_name(def_lexer)
            tokens = lex(raw_code, lexer)
            cod = []
            for t, v in tokens:
                if not v:
                    continue
                _col = code_hl_tokens.get(t)
                if _col:
                    cod.append(col(v, _col))
                else:
                    cod.append(v)
            s = ''.join(cod)


        # outest hir is 2, use it for fenced:
        ind = ' ' * kw.get('hir', 2)
        #if from_fenced_block: ... WE treat equal.

        # shift to the far left, no matter the indent (screenspace matters):
        firstl = s.split('\n')[0]
        del_spaces = ' ' * (len(firstl) - len(firstl.lstrip()))
        s = ('\n' + s).replace('\n%s' % del_spaces, '\n')[1:]

        # we want an indent of one and low vis prefix. this does it:
        code_lines = ('\n' + s).splitlines()
        prefix = ('\n%s%s %s' % (ind, low(code_pref), col('', C, no_reset=1)))
        code = prefix.join(code_lines)
        return code + '\n' + reset_col


inlines = '<em>', '<code>', '<strong>'
def is_text_node(el):
    """ """
    # strip our tag:
    html = etree.tostring(el).split('<%s' % el.tag, 1)[1].split('>',
            1)[1].rsplit('>', 1)[0]
    # do we start with another tagged child which is NOT in inlines:?
    if not html.startswith('<'):
        return 1, html
    for inline in inlines:
        if html.startswith(inline):
            return 1, html
    return 0, 0


# ----------------------------------------------------- Text Termcols Adaptions
def rewrap(el, t, ind, pref):
    """ Reasonably smart rewrapping checking punctuations """
    global term_columns
    cols = term_columns - len(ind + pref)
    if el.tag == 'code' or len(t) <= cols:
        return t
    # wrapping:
    # we want to keep existing linebreaks after punctuation
    # marks. the others we rewrap:

    puncs =  ',', '.', '?', '!', '-', ':'
    parts = []
    origp = t.splitlines()
    if len(origp) > 1:
        pos = -1
        while pos < len(origp) - 1:
            pos += 1
            # last char punctuation?
            if origp[pos][-1] not in puncs and \
                    not pos == len(origp) -1:
                # concat:
                parts.append(origp[pos].strip() + ' ' + \
                            origp[pos+1].strip())
                pos += 1
            else:
                parts.append(origp[pos].strip())
        t = '\n'.join(parts)
    # having only the linebreaks with puncs before we rewrap
    # now:
    parts = []
    for part in t.splitlines():
        parts.extend([part[i:i+cols] \
                        for i in range(0, len(part), cols)])
    # last remove leading ' ' (if '\n' came just before):
    t = []
    for p in parts:
        t.append(p.strip())
    return '\n'.join(t)




def split_blocks(text_block, w, cols, part_fmter=None):
    """ splits while multiline blocks vertically (for large tables) """
    ts = []
    for line in text_block.splitlines():
        parts = []
        # make equal len:
        line = line.ljust(w, ' ')
        # first part full width, others a bit indented:
        parts.append(line[:cols])
        scols = cols-2
        # the txt_block_cut in low makes the whole secondary tables
        # low. which i find a feature:
        # if you don't want it remove the col(.., L)
        parts.extend([' ' + col(txt_block_cut, L, no_reset=1) + \
                line[i:i+scols] \
                    for i in range(cols, len(line), scols)])
        ts.append(parts)

    blocks = []
    for block_part_nr in xrange(len(ts[0])):
        tpart = []
        for lines_block in ts:
            tpart.append(lines_block[block_part_nr])
        if part_fmter:
            part_fmter(tpart)
        tpart[1]  = col(tpart[1], H3)
        blocks.append('\n'.join(tpart))
    t = '\n'.join(blocks)
    return('\n%s\n' % t)




# ---------------------------------------------------- Create the treeprocessor
class AnsiPrinter(Treeprocessor):
    header_tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')

    def run(self, doc):
        tags = Tags()
        def get_attr(el, attr):
            for c in el.items():
                if c[0] == attr:
                    return c[1]
            return ''

        def formatter(el, out, hir=0, pref='', parent=None):
            """
            debugging:
            # if el.tag == 'div':
            # for c in el.getchildren()[3].getchildren(): print c.text, c
            """
            ss = etree.tostring
            done_inline = 0

            if el.tag == 'hr':
                return out.append(tags.hr('', hir=hir))

            if el.text or el.tag == 'p':
                el.text = el.text or ''
                # <a attributes>foo... -> we want "foo....". Is it a sub
                # tag or inline text?
                done_inline, html = is_text_node(el)

                if done_inline:
                    t = html.rsplit('<', 1)[0]
                    t = t.replace('<code>'  , code_start).replace(
                                 '</code>'  , code_end)
                    t = t.replace('<strong>', stng_start).replace(
                                 '</strong>', stng_end)
                    t = t.replace('<em>'    , emph_start).replace(
                                 '</em>'    , emph_end)
                    t = html_parser.unescape(t)
                else:
                    t = el.text

                t = t.strip()
                admon = ''
                pref = body_pref = ''
                if t.startswith('!!! '):
                    for k in admons:
                        if t[4:].startswith(k):
                            pref = body_pref = '┃ '
                            pref +=  (k.capitalize())
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
                    pref      = col(pref     , globals()[admons[admon]])
                    body_pref = col(body_pref, globals()[admons[admon]])


                if pref == list_pref:
                    pref = col(pref, H4)
                if pref.split('.', 1)[0].isdigit():
                    pref = col(pref, H3)

                t = ('\n' + ind + body_pref).join((t).splitlines())
                t = ind + pref + t


                # headers outer left: go sure.
                # actually... NO. commented out.
                # if el.tag in self.header_tags:
                #    pref = ''

                # calling the class Tags  functions
                out.append(getattr(tags, el.tag, plain)(t, hir=hir))
                if show_links:
                    for l in 'src', 'href':
                        if l in el.keys():
                            out[-1] += low('(%s) ' % get_attr(el, l))

                if admon:
                    out.append('\n')

            # have children?
            #    nr for ols:
            if done_inline:
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
                    for Row in el[he_bo].getchildren():
                        row = []
                        t.append(row)
                        for cell in Row.getchildren():
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
                if el.tag == 'ul' or el.tag == 'li':
                    c.set('pref', list_pref)
                elif el.tag == 'ol':
                    nr += 1
                    c.set('pref', str(nr) + ' ')

                # handle the ``` style unindented code blocks -> parsed as p:
                is_code = None
                formatter(c, out, hir+1, parent=el)
            if el.tag == 'ul' or el.tag == 'ol' and not out[-1] == '\n':
                out.append('\n')

        out = []
        formatter(doc, out)
        self.markdown.ansi = '\n'.join(out)


# Then tell markdown about it
class AnsiPrintExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        ansi_print_ext = AnsiPrinter(md)
        md.treeprocessors.add('ansi_print_ext', ansi_print_ext, '>inline')






def main(md=None, filename=None, cols=None, theme=None, c_theme=None, bg=None,
         c_guess=-1, display_links=None, **kw):
    """ md is markdown string. alternatively we use filename and read """

    args = locals()
    if not md:
        if not filename:
            print 'Using sample markdown:'
            make_sample()
            md = args['md'] = md_sample
            print md
        else:
            with open(filename) as f:
                md = f.read()

    global term_columns
    # style rolers requested?
    if c_theme == 'all' or theme == 'all':
        args.pop('kw')
        themes = read_themes()
        for k, v in themes.items():
            if not filename:
                args['md'] = md_sample.replace('__id__', k).\
                                       replace('__name__', v['name'])
            print col('%s%s%s' % ('\n\n', '=' * term_columns,'\n'), L)
            # should really create an iterator here:
            if theme == 'all':
                args['theme'] = k
            else:
                args['c_theme'] = k
            print main(**args)
        return ''

    if cols:
        term_columns = int(cols)

    global show_links
    show_links = display_links

    if bg and bg == 'light':
        # not in use rite now:
        global background, color
        background = BGL
        color = T

    set_theme(theme)

    if not c_guess == -1:
        global guess_lexer
        guess_lexer = c_guess

    if not c_theme:
        c_theme = theme or 'default'

    if c_theme == 'None':
        c_theme = None

    if c_theme:
        set_theme(c_theme, for_code=1)

    if c_theme or c_guess:
        # info:
        if not have_pygments:
            print col('No pygments, can not analyze code for hilite', R)


    # Create an instance of the Markdown class with the new extension
    MD = markdown.Markdown(extensions=[AnsiPrintExtension(),
                                       TableExtension(),
                                       fenced_code.FencedCodeExtension()])
    # html?
    MD.convert(md)

    # who wants html, here is our result:
    out = MD.ansi

    # The RAW html within source, incl. fenced code blocks:
    # phs are numbered like this in the md, we replace back:
    PH = markdown.util.HTML_PLACEHOLDER
    stash = MD.htmlStash
    nr = -1
    tags = Tags()
    for ph in stash.rawHtmlBlocks:
        nr += 1
        raw = html_parser.unescape(ph[0])
        pre = '<pre><code'
        if raw.startswith(pre):
            pre, raw = raw.split(pre, 1)
            raw = raw.split('>', 1)[1].rsplit('</code>', 1)[0]
            if 'class="' in pre:
                # language:
                lang = pre.split('class="', 1)[1].split('"')[0]
            else:
                lang = ''
            raw = tags.code(raw.strip(), from_fenced_block=1, lang=lang)
        out = out.replace(PH % nr, raw)

    # don't want these: gone through the extension now:
    # out = out.replace('```', '')
    return out

    #return '%s%s%s' % (col_bg(background), MD.ansi, reset_col)


def run_args(args):
    return main(filename      = filename
               ,theme         = args.get('-t', 'random')
               ,cols          = args.get('-c')
               ,c_theme       = args.get('-T')
               ,c_guess       = args.get('-x')
               ,display_links = args.get('-L'))

if __name__ == '__main__':
    args = docopt(__doc__, version='mdv v0.1')
    filename = args.get('MDFILE')
    if not args.get('-m'):
        print run_args(args)
        raise SystemExit

    # monitor mode:
    if not filename:
        print col('Need file argument', 2)
        raise SystemExit

    last_err = ''
    last_stat = 0
    while True:
        if not os.path.exists(filename):
            last_err = 'File %s not found. Will continue trying.' % filename
        else:
            try:
                stat = os.stat(filename)[8]
                if stat != last_stat:
                    parsed = run_args(args)
                    print parsed
                    last_stat = stat
                last_err = ''
            except Exception, ex:
                last_err = str(ex)
        if last_err:
            print 'Error: %s' % err
        time.sleep(1)



