r"""Test 9324 -- R1 RED TEAM (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base and HEAD, every model): in `_const_int_value`, `v.op` both as an isinstance subject AND aliased (`o = v.op`): not every occurrence is a subject, so the read stays refused. CPython: -x -> 0 under `ensures \result == 1`.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 1
    #@ assigns \nothing
    def _const_int_value(self, v: "ExprIR") -> int:
        if isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.USub):
            return 1 if v.op == "" else 0
        return 1


if __name__ == "__main__":
    r = Em()._const_int_value(ast.parse("-x", mode="eval").body)
    print("VIOLATION contract" if r != 1 else "result", r)
