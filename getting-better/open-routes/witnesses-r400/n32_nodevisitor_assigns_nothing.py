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
