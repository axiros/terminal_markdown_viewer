### Source
# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6
```
""" Test """
# Make Py2 >>> Py3:
import os, sys; reload(sys); sys.setdefaultencoding('utf-8')
# no? see http://stackoverflow.com/a/29832646/4583360 ...

# code analysis for hilite:
try:
    from pygments import lex, token
    from pygments.lexers import get_lexer_by_name, guess_lexer
```

| Tables | Fmt |
| -- | -- |
| !!! hint: wrapped | 0.1 **strong** |

!!! note: title
    this is a Note

