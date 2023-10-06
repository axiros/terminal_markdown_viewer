import io, sys
from unittest import TestCase, main
import pdb

breakpoint = pdb.set_trace
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass  # py3
import os
import mdv
import sys

if sys.version_info[0] > 2:
    unicode = str

here = os.path.split(os.path.abspath(__file__))[0]
readfile = mdv.markdownviewer.readfile


class TestNose(TestCase):
    """testing the test"""

    def test_itself(self):
        self.assertTrue(True)


class TestFiles(TestCase):
    """tests all .md files within the files directory against their build
    version"""

    def test_all(self):
        df = os.path.join(here, 'files')
        for f in os.listdir(df):
            if not f.endswith('.md'):
                continue
            print('testfile: ', f)
            src = readfile(df + '/' + f)
            for col in 200, 80, 40, 20:
                print('columns: ', col)

                res = mdv.main(
                    src,
                    cols=col,
                    theme=729.8953,
                    c_theme=729.8953,
                    c_no_guess=True,
                    c_def_lexer='python',
                    keep_bg=True,
                )
                _ = '%s/result.%s/%s.expected'
                tgt = unicode(readfile(_ % (df, col, f))).strip()
                res = unicode(res).strip()
                if res.startswith(bgstart):
                    res = res.split(bgstart, 1)[1]
                res = res.strip()

                # print(res)
                if not tgt == res:
                    print('error')
                    mdv.markdownviewer.write_file('/tmp/got', res)
                    mdv.markdownviewer.write_file('/tmp/should', tgt)
                    os.system('diff /tmp/got /tmp/should')
                    print('got:\n', res)
                    print('should:\n', unicode(tgt))
                    if sys.stdin.isatty() and sys.stdout.isatty():
                        os.system('vi -d /tmp/got /tmp/should')
                    raise Exception('Error %s col %s' % (f, col))


bgstart = '\x1b[0m'
if __name__ == '__main__':
    main()
