r"""Test 10268 -- run #8 u57, route #429 (expected FAIL): a constant fold of a LATIN-1 literal leaves Latin-1: `"\xff".upper()` is U+0178, handed to the solver as `(pystr_chr 376)`, outside every law of the str model; claimed `== "\xff"` (CPython False). REFUSED by the emission half: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    if "\xff".upper() == "\xff":
        return 0
    return 1


if __name__ == "__main__":
    r = f()
    print("VIOLATION contract" if r != 0 else "result", r)
