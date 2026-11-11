import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, module_node: ast.Module) -> int:
        for stmt in module_node.body:
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Name):
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("x = y"))
    print("VIOLATION contract" if r != 0 else "result", r)
