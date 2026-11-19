r"""Test 5685 -- gen #37 CONTROL route #400 (the advice followed) (expected PASS): the `visit_Constant` of a dispatching `ast.NodeVisitor` subclass called DIRECTLY, its contract carried; PROVED (CPython 1).
"""
# pycsl-expected: PASS
import ast


class V(ast.NodeVisitor):
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1
    def visit_Constant(self, node: ast.Constant) -> None:
        self.n = self.n + 1


#@ ensures \result == 1
def f(node: ast.Constant) -> int:
    v = V()
    v.visit_Constant(node)
    return v.n


if __name__ == "__main__":
    assert f(ast.Constant(1)) == 1
