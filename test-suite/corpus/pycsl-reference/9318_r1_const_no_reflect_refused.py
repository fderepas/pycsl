r"""Test 9318 -- R1 RED TEAM (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base and HEAD, every model): (unchanged rule): without the const-reflect model (no `isinstance(_.value, (int, float))` in the file) `isinstance(elt, ast.Constant)` is not a discriminant, so it narrows as before. CPython: Constant(5) -> 1 under `ensures \result == 0`.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        if isinstance(elt, ast.Constant):
            if elt.kind == "Number":
                return 0
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("5", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
