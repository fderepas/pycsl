r"""Test 10205 -- route #614 (expected FAIL): the one equality route #614 keeps, `Path(a) == Path(b)`
with both operands a direct `Path(..)` call, must not decide two paths DIFFERENT: CPython compares
normalised parts, so `Path("a//b") == Path("a/b")` is True, and `\result == False` must NOT prove
(the model `ext_path_of_str_op` is law-free: no injectivity, no normalisation law).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == False
#@ assigns \nothing
def f() -> bool:
    return Path("a//b") == Path("a/b")


if __name__ == "__main__":
    r = f()
    print("VIOLATION contract" if r is not False else "result", r)
