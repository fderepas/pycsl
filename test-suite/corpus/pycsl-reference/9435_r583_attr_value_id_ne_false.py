r"""Test 9435 -- route #583 WITNESS (expected FAIL: the claim is FALSE of the program): `x.value.id != ""` on an Attribute whose object is a Name (`self.a`): at base the id read `name_of (IrOther "")` = `""`; PROVED at base, NOT proved at HEAD. CPython: 1.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name):
            if x.value.id != "":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("self.a", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
