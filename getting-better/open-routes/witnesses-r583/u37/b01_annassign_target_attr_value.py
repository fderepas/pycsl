import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, module_node: ast.Module) -> int:
        for stmt in module_node.body:
            if (isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Attribute)
                    and isinstance(stmt.target.value, ast.Name) and stmt.target.value.id == "self"):
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("self.a: int = 1"))
    print("VIOLATION contract" if r != 0 else "result", r)
