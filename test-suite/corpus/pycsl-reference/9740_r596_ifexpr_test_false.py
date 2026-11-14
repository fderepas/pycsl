r"""Test 9740 -- route #596 WITNESS (expected FAIL: the claim is FALSE of the program): `.test` of a node tested `IfExpr` (no constructor arm: the IfExpr node is not modelled with its test) reads an opaque value, not the `IrOther ""` placeholder. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "IfExpr":
            if x.test.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().f(NS(kind="IfExpr", test=NS(kind="Var", name="a", value=0), body=NS(kind="Number", value=0), orelse=NS(kind="Number", value=0)))
        print("VIOLATION contract" if r != 0 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
