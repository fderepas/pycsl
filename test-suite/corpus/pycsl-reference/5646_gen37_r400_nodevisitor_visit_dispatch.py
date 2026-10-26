r"""Test 5646 -- gen #37 route #400 (expected FAIL): `V(ast.NodeVisitor)` with a contracted `visit_Constant` (`self.n += 1`); `v.visit(ast.parse("1")); return v.n` proved 0; PROVED at base 3b2d2e763 (CPython 1). REFUSED (PYCSL-R400-NODEVISITOR-DISPATCH).
"""
# pycsl-expected: FAIL
import ast


class V(ast.NodeVisitor):
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1
    def visit_Constant(self, node: ast.Constant) -> None:
        self.n = self.n + 1


#@ ensures \result == 0
def f() -> int:
    v = V()
    v.visit(ast.parse("1"))
    return v.n


if __name__ == "__main__":
    r = f()
    print("VIOLATION f =", r) if r != 0 else print("no violation")
