import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, module_node: ast.Module) -> int:
        for stmt in module_node.body:
            if isinstance(stmt, ast.ClassDef):
                for cstmt in stmt.body:
                    if isinstance(cstmt, ast.FunctionDef):
                        for sub in ast.walk(cstmt):
                            if (isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Attribute)
                                    and isinstance(sub.target.value, ast.Name)
                                    and sub.target.value.id == "self"):
                                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("class C:\n    def __init__(self):\n        self.a: int = 1\n"))
    print("VIOLATION contract" if r != 0 else "result", r)
