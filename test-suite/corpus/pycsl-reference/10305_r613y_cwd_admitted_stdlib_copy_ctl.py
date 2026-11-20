r"""Test 10305 -- run #8 u58, review rt69 G7 (PASS control). `json` is found first in pycsl's working directory
(the tree root's admitted byte-identical copy of the interpreter's Lib/json, routes #326 / #611). CPython never
searches the cwd and loads the interpreter's own json, which is the same source file for file, so the G7 rule
admits it. Emitted exactly as at int72.
"""
# pycsl-expected: PASS
import json


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = json.dumps("a")
    return 1


if __name__ == "__main__":
    print("result", f())
