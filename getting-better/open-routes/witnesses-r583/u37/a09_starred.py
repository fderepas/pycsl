import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Starred) and isinstance(x.value, ast.Name):
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("f(*a)", mode="eval").body.args[0])
    print("VIOLATION contract" if r != 0 else "result", r)
