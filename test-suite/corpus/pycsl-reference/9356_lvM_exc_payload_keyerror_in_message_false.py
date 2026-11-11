r"""Test 9356 -- cap-exception-payload-model (expected FAIL: refused PYCSL-R506-TRIGGER-SITE-UNLOWERED, the
claim is FALSE of the program): the message of `raise Oops(d["k"])` reads a MISSING key, so CPython raises
KeyError while building the exception and the `except Oops` handler never runs; `probe()` raises KeyError
instead of returning 1. The argument is not classified string-typed, so it is not the payload (which is
then unconstrained) and route #506 refuses the unlowered subscript, before and after the payload model.
"""
# pycsl-expected: FAIL
from typing import Dict


class Oops(Exception):
    pass


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    d: Dict[str, str] = {"a": "x"}
    try:
        raise Oops(d["k"])
    except Oops:
        return 1


if __name__ == "__main__":
    try:
        r = probe()
        print("VIOLATION contract" if r != 1 else "ok", r)
    except KeyError as e:
        print("VIOLATION KeyError", e)
