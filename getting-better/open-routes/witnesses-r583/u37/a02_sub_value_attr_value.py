import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Attribute):
            if isinstance(x.value.value, ast.Name):
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("self.a[0]", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
