r"""Test 9652 -- route #593 (expected FAIL: PROVED at base 4e6004f3b in the default model, REFUSED PYCSL-R593-IR-NODE-SUBCLASS in every model at HEAD): u41 probe: the node classes imported by name (`from ast import Name, Call; class B(Name, Call)`); returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any

import ast

def mutable_state(cls): return cls
from ast import Name, Call
class B(Name, Call):
    pass

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Name) and isinstance(x, ast.Call):
            return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().f(B(id="a", func=ast.Name("g"), args=[], keywords=[]))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
