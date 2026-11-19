# R1 REFUSE: ast.ClassDef tested on an emit_ir value (not a pyast_stmt local / TParamNode param): not
# a discriminant there, so it narrows. CPython: ClassDef "C" -> 1 under `ensures \result == 0`.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.ClassDef):
            if x.name == "C":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("class C: pass").body[0])
    print("VIOLATION contract" if r != 0 else "result", r)
