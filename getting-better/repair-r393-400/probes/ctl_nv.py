import ast
class V(ast.NodeVisitor):
    def __init__(self) -> None:
        self.n: int = 0
#@ ensures \result == 0
def f() -> int:
    v = V()
    v.visit(ast.parse("1"))
    return v.n
if __name__ == "__main__":
    assert f() == 0
