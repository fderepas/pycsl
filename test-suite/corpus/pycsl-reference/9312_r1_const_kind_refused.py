r"""Test 9312 -- R1 RED TEAM (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base and HEAD, every model): `.kind` of an ast.Constant is its own str|None field; `kind_of` reads the IR tag ("Number"), so `ensures \result == 0` would be a theorem. CPython: Em().f(Constant(5)) == 1.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float)):
            if elt.kind == "Number":
                return 0
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("5", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
