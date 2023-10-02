import io
from unittest import TestCase, main
import pdb

breakpoint = pdb.set_trace
try:
    import sys

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


class TestNose(TestCase):
    """ testing the test"""

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
            with open(df + '/' + f) as fd:
                src = fd.read()
            for col in 20, 40, 80, 200:
                print('columns: ', col)

                res = mdv.main(
                    src,
                    cols=col,
                    theme=729.8953,
                    c_theme=729.8953,
                    c_no_guess=True,
                    c_def_lexer='python',
                )

                with io.open('%s/result.%s/%s.expected' % (df, col, f), encoding='utf-8') as fd:
                    tgt = fd.read()

                # print(res)
                if not unicode(tgt).strip() == unicode(res).strip():
                    print('error')
                    print('got:\n', res)
                    print('should:\n', unicode(tgt))
                    raise Exception('Error %s col %s' % (f, col))


if __name__ == '__main__':
    main()
