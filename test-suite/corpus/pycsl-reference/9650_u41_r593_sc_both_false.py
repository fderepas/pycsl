r"""Test 9650 -- route #593 (expected FAIL: PROVED at base 4e6004f3b in the default model, REFUSED PYCSL-R593-IR-NODE-SUBCLASS in every model at HEAD): red team rt56 probe hd1767: `class B(ast.Name, ast.Call)` makes one CPython object an instance of both node classes, while the emit_ir model decides `isinstance(x, ast.Name)` / `isinstance(x, ast.Call)` by DISJOINT constructor tags; `Em().f(B(...))` returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import ast

def mutable_state(cls): return cls
class B(ast.Name, ast.Call):
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
