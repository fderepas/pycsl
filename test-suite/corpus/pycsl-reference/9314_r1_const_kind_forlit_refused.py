r"""Test 9314 -- R1 RED TEAM (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base and HEAD, every model): the residual through a `for` over a display (coarse edge, exact match keeps the set). CPython: 1 under `ensures \result == 0`.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        r = 0
        for c in [elt]:
            if isinstance(c, ast.Constant) and isinstance(c.value, (int, float)):
                r = 1
        if r == 1:
            if elt.kind == "Number":
                return 0
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("5", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
