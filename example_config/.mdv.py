#!/usr/bin/env python2.7
# this file is execed in global and local namespace of def main.
# => you can also patch functions here.
import os
env = os.environ.get

# Global Config for mdv

# This file is execed and overrides globals, plus provides defaults for not
# given CLI switches.
# Location for this file: $HOME/.mdv.py
# Syntax hilite theme. `mdv -t all` shows all.
theme = env('MDV_THEME', '965.9469')
# Code hilite theme. `mdv -T all` shows all.
c_theme='1016.9868' # overridden by $MDV_CTHEME

# You have the args, so you can act differently depending on file:
# if filename == 'README.md':
#    theme = '1016.9868'

# You can override the app's globals, see config section in mdv.py for
# available options:
global code_pref
code_pref='|'

# Uncomment to switch off the theme info:
# show_theme_info = False

# Calculate your term cols smarter / for windows:
# term_columns = <your code >

# You can also override/patch functions of the main module here:
# e.g. the make_sample function, as shown:
#def my_sample():
#    globals()['md_sample'] = '# H1 sample\n## my h2 sample\nHi there'
# Uncomment to activate the patch. mdv w/o args displays your sample then.
# make_sample = my_sample

