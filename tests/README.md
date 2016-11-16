# Test runner

Currently not much tested except a few simple use cases but its easy to add new
tests by just adding a "mud" (markdown under test) file with extension ".md"
and do `run build` to generate and visually inpect if the rendered result of all
muds comply with how it should be / if code changes break existing tests.

The travis verification is then simply based on diffs against the "<mud>.expected" files.



## building the expected results files
- execute `run build` to generate mdv output for all ".md" files within this folder.
- commit


## testing new mdv versions

- travis will execute `run` to diff the current mdv output with the expected
  results


## Notes

Some day I'll make the line seps a bit smarter, e.g. min one line sep after lists
