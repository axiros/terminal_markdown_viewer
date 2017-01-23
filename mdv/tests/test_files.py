from unittest import TestCase, main
try:
    import sys; reload(sys); sys.setdefaultencoding('utf-8')
except:
    pass # py3
import os
import mdv

here = os.path.abspath(__file__).rsplit('/', 1)[0]

class TestNose(TestCase):
    ''' testing the test'''
    def test_itself(self):
        self.assertTrue(True)


class TestFiles(TestCase):
    '''tests all .md files within the files directory against their build
    version'''
    def test_all(self):
        df = here + '/files'
        for f in os.listdir(df):
            if not f.endswith('.md'):
                continue
            print ('testfile: ', f)
            with open(df + '/' + f) as fd:
                src = fd.read()
            for col in 20, 40, 80, 200:
                print ('columns: ', col)
                rd = 'result.%s' % col
                res = mdv.main(src, cols=col, theme=729.8953, c_theme=729.8953)
                with open('%s/result.%s/%s.expected' % (df, col, f)) as fd:
                    tgt = fd.read()
                print (res)
                if not unicode(tgt).strip() == unicode(res).strip():
                    print ('error')
                    print ('got:\n', res)
                    print ('should:\n', tgt)
                    raise Exception("Error %s col %s" % (f, col))



if __name__ == '__main__':
    main()
