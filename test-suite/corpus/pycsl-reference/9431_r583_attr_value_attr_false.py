r"""Test 9431 -- route #583 WITNESS (expected FAIL: the claim is FALSE of the program): `isinstance(x.value, ast.Attribute)` on an Attribute-tested `x` (`a.b.c`): the object is an Attribute; the false `\result == 0` PROVED at base (dead branch), NOT proved at HEAD. CPython: 1.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Attribute):
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("a.b.c", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
