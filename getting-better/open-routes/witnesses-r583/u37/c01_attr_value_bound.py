import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 2
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name):
            if x.value.id == "self":
                return 2
            return 1
        return 0


if __name__ == "__main__":
    e = Em()
    rs = [e.f(ast.parse(s, mode="eval").body) for s in ("self.a", "o.a", "a[0]", "x")]
    print("VIOLATION" if any(r < 0 or r > 2 for r in rs) else "result", rs)
