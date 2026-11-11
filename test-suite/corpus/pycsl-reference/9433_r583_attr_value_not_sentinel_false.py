r"""Test 9433 -- route #583 WITNESS (expected FAIL: the claim is FALSE of the program): an Attribute whose object is none of Name / Attribute / Subscript / Call returns 0, otherwise 1: at base the object read `IrOther ""`, so every Attribute took the 0 path and the false `\result == 0` PROVED; NOT proved at HEAD. CPython: `f().b` -> 1.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute) and not isinstance(x.value, ast.Name):
            if not isinstance(x.value, ast.Attribute):
                if not isinstance(x.value, ast.Subscript):
                    if not isinstance(x.value, ast.Call):
                        return 0
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("f().b", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
