# coding: utf-8
from unittest import TestCase, main

try:
    import sys

    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass  # py3
import os
import mdv

here = os.path.abspath(__file__).rsplit('/', 1)[0]


def clean(s):
    return mdv.markdownviewer.clean_ansi(s).strip()


class TestInlines(TestCase):
    def test_table(self):
        st = '''
| Item     | Value | Qty   |
|  --- | --- | --- |
| Computer | $1600 |  5    |
| Phone    | $12   |  12   |
| Pipe     | $1    |  234  |
'''
        s = mdv.main(st)
        assert clean(s) == clean(
            '''
  ────────  ─────  ───
  Item      Value  Qty
  Computer  $1600  5
  Phone     $12    12
  Pipe      $1     234
  ────────  ─────  ───
'''
        )


if __name__ == '__main__':
    main()
