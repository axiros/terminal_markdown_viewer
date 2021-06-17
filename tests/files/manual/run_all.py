#!/usr/bin/env python2.7
print 'Please inspect visually.'
import os, sys
sys.argv.append('')
# substring match on filenames, if not given run all:
match = sys.argv[1]

exe = '../../mdv/markdownviewer.py'
for file in os.listdir('.'):
    if not file.endswith('.md') or not match in file:
        continue
    print '\n\n'
    os.system('echo "----\nTESTFILE:\n# %s\n-----" | %s -' % (file, exe))
    print open(file).read()
    os.system('%s "%s"' % (exe, file))

