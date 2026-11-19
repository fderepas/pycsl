# Route #583 exemplar (PRE-EXISTING): ast.Attribute is an IR class (`_AST_CLASS_TO_IR_KIND`, never narrowed); its
# `.value` (the object) lowers to `svalue_of`, the SUBSCRIPT projector, which is `IrOther ""` on an IrAttr,
# so `x.value.id == "self"` is false in the model. CPython: `self.a` -> 1 under `ensures \result == 0`.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name):
            if x.value.id == "self":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("self.a", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
