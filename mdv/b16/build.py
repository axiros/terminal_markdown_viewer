#!/usr/bin/env python
"""
builds the .json source files for all base16 themes

$0 clone: clones them into the current directory, before building
$0 : only builds
"""


import requests
import yaml, os, sys, json
import threading

all = 'https://raw.githubusercontent.com/chriskempson/base16-schemes-source/main/list.yaml'


def get_yaml(url):
    s = requests.get(url).text
    return yaml.unsafe_load(s)


def clone(r):
    os.system(f'git clone "{r}"')


def collect(d):
    for fn in os.listdir(d):
        if fn.rsplit('.', 1)[-1] in {'yaml', 'yml'}:
            sr = open(f'{d}/{fn}').read()
            s = yaml.unsafe_load(sr)
            fnr = fn.rsplit('.', 1)[0] + '.json'
            if 'base00' in s and 'base0F' in s:
                with open(fnr, 'w') as fd:
                    fd.write(json.dumps(s, indent=2, sort_keys=True))


def main(clone=True):
    if clone:
        clone_all()

    for d in os.listdir('.'):
        if os.path.exists(f'./{d}/.git'):
            collect(d)


def clone_all():
    y = get_yaml(all)
    t = [threading.Thread(target=clone, args=(r,)) for r in y.values()]
    [i.start() for i in t]
    [i.join() for i in t]


if __name__ == '__main__':
    main(clone='clone' in sys.argv)
