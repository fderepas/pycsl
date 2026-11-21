r"""Test 10221 -- run #8 u55, review rt66 g02 (PASS control). Declared `--as-package-module test-suite/corpus`
as in 10220, but the program's only import, `json`, resolves to the same file in both orders (CPython's
-m order, test-suite/corpus first, and pycsl's, the program directory first): neither directory holds a
`json`, and both then reach cwd's admitted ./json/ copy. Emitted exactly as at ff03f178c.
run #8 u58 (review rt69): `--as-package-module` is WITHDRAWN (rc 2), so the flag is dropped and this is now a
SCRIPT-mode control: `json` is the cwd's admitted ./json/ copy, which the G7 rule admits (CPython loads the
interpreter's identical Lib/json). Its emission does not depend on the mode and is unchanged.
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
