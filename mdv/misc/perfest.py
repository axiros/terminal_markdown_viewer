import sys
from time import time as t
from paka import cmark
import mistletoe
from mistletoe.latex_renderer import LaTeXRenderer

import commonmark
import markdown

from ansi_renderer import AnsiRenderer

from markdown.extensions import fenced_code

from markdown.extensions.tables import TableExtension

md = sys.argv[1] if len(sys.argv) > 1 else "test_md.md"
s = open(md).read()


def w(func, *a, **kw):
    fn = kw.pop("fn")
    count = kw.pop("count", 10)
    t1 = t()
    for i in range(count):
        m = func(*a, **kw)
    print("%.2f" % (t() - t1), fn)
    m = "<html>\n<body>" + m + "</body></html>"
    with open("./results_perftests/out_" + fn + ".html", "w") as fd:
        fd.write(str(m))
    # print(m)


# w(mistletoe.markdown, s, LaTeXRenderer, fn="mistletoe_ansi", count=1)
# w(mistletoe.markdown, s, AnsiRenderer, fn="mistletoe_ansi", count=1)
# import sys
# sys.exit(0)

MD = markdown.Markdown(
    extensions=[TableExtension(), fenced_code.FencedCodeExtension()]
)

# fmt: off
w(cmark.to_html         , s , fn="paka")
w(cmark.to_html         , s , fn="paka_breaks" , breaks="hard")
w(cmark.to_xml          , s , fn="paka_xml")
w(mistletoe.markdown    , s , fn="mistletoe")
w(commonmark.commonmark , s , fn="commonmark")
w(MD.convert            , s , fn="markdown")
