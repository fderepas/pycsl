import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Attribute):
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("a.b.c", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
