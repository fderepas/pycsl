# Completeness of system calls

The Goal is to implement system calls used in `src/pycsl` so that we can proceed to self annotations.

## Storing the information

Two files are to store the coverage of system calls:
- `calls-english.md`: stores the english description of system calls
- `calls-pycsl.md`: store the PyCSL translation of previous description.

## Check loop

1/ List all system calls in `src/pycsl/*.py` and  `src/pycsl/module6_whyml/*.py`
2/ Make sure they are in `calls-english.md`, if not add them with english description from `cpython/Doc/library`
3/ Make sure that all function in`calls-english.md` has its counterpart in `calls-pycsl.md`. The PyCSL should reflect the english text. To check it's simple read the PyCSL and try to guess the english.
4/ Make sure all system calls in `calls-pycsl.md` have a stubbed version in `Lib` where PyCSL reads from. The contact of functions in `Lib/*.py` should be the one from `calls-pycsl.md`
5/

## Example

File `cpython/Doc/library/string.rst` is an english description of what a string is.

In this file class `Formatter` is defined. If this type is returned by a function in `src/pycsl/*.py` and  `src/pycsl/module6_whyml/*.py` a stub of this class should be added in `Lib/string.py` with fields and abstracted methods (just the contracts) so that it can be read by PyCSL.

In this case `Formatter` is not returned, so it's not included in `Lib/string.py`




