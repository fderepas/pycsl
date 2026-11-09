r"""Test 9432 -- route #583 WITNESS (expected FAIL: the claim is FALSE of the program): a Subscript whose value is an Attribute, read through BOTH meanings of `.value` (`x.value.value`, `self.a[0]`): the inner read is an Attribute's object; PROVED at base, NOT proved at HEAD. CPython: 1.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Attribute):
            if isinstance(x.value.value, ast.Name):
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("self.a[0]", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
