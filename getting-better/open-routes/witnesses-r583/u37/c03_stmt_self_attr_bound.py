import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def f(self, module_node: ast.Module) -> int:
        for stmt in module_node.body:
            if (isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Attribute)
                    and isinstance(stmt.target.value, ast.Name) and stmt.target.value.id == "self"):
                return 1
        return 0


if __name__ == "__main__":
    e = Em()
    rs = [e.f(ast.parse(s)) for s in ("self.a: int = 1", "x: int = 1", "x = 2")]
    print("VIOLATION" if any(r < 0 or r > 1 for r in rs) else "result", rs)
