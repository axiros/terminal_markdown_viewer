# Hello

Look at next code block.

```bash
command -stdin <<EOP
first line in stdin
second line in stdin
EOP
```

This is similar code block with ${variable} highlighted. But it looks broken.

    command -stdin ${variable} <<EOP
    first line in stdin
    second line in stdin
    EOP

It looks broken even if ${variable} present anywhere in code block.

    command -stdin <<EOP
    first line in stdin
    second line in stdin
    EOP

    ${variable}

Actually it works if code block contains ${variable} and <:

    First string <
    Second string with ${var}.
    Third string.

# The end.
