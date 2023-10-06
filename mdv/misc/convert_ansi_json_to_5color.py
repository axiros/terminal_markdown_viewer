#!/usr/bin/env python
"""
Converts the pre 1.8.0 ansi_tables.json to base16 scheme defs.

When theme and ctheme are set to those 5color files we configure mdv's style globals so that
those are used to produce backwards compat output.
"""
import os, sys
import yaml

T = """{
        "scheme": "%(n)s",
        "base00": false,
        "base01": false,
        "base02": false,
        "base03": false,
        "base04": false,
        "base05": 188,
        "base06": false,
        "base07": false,
        "base08": false,
        "base09": %(1)s,
        "base0A": %(2)s,
        "base0B": %(3)s,
        "base0C": %(4)s,
        "base0D": %(5)s,
        "base0E": %(5)s,
        "base0F": %(5)s
}
"""


def write_file(d, n, v):
    fn = d + '/' + n + '.json'
    m = {'n': v.get('name', n)}
    try:
        m.update({str(i + 1): v['ct'][i] for i in range(5)})
        s = T % m
        print(n)
    except Exception as ex:   # some (2) have less then 5. ignore.
        return
    with open(fn, 'w') as fd:
        fd.write(s)


def main():
    d = os.path.abspath('.')
    fn = d + '/ansi_tables.json'
    all = yaml.unsafe_load(open(fn).read())
    os.makedirs(d + '/5color', exist_ok=True)
    for n, v in all.items():
        write_file(d + '/5color', n, v)


if __name__ == '__main__':
    main()
