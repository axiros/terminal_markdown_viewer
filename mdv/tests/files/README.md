# Test runner

Currently not much tested except a few simple use cases but its easy to add new
tests by just adding a "mud" (markdown under test) file with extension ".md"
and do `run build` to generate and visually inpect if the rendered result of all
muds comply with how it should be / if code changes break existing tests.

The travis verification is then simply based on diffs against the "<mud>.expected" files.

This README is also a mud, you have to `run build` if you change it.

# Columns

We verify correct output for certain terminal column available, resulting in
files ending with e.g. '.80'

## `run build`: building the expected results files
- execute `run build` to generate mdv output for all ".md" files within this folder.
- git diff to see any changes
- commit if all is good


## `run test`: testing new mdv versions

- travis will execute `run test` to diff the current mdv output with the expected
  results


## Notes

Some day I'll make the line seps a bit smarter, e.g. min one line sep after lists
