#!/usr/bin/env python2.7
import os

exe = '../mdv/markdownviewer.py'
for file in os.listdir('.'):
    if not file.endswith('.md'):
        continue
    print '\n\n'
    os.system('echo "----\nTESTFILE:\n# %s\n-----" | %s -' % (file, exe))
    print open(file).read()
    os.system('%s "%s"' % (exe, file))

