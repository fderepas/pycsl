r"""Test 9441 -- route #583 CONTROL (expected PASS): CONTROL: the honest two-sided bound through `Subscript.value` and through a Subscript's Attribute value (`x.value.value`) proves at HEAD: the Subscript path keeps its meaning. CPython agrees ([2, 1, 1, 0]).
"""
# pycsl-expected: PASS
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 2
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name):
            if x.value.id == "List":
                return 2
            return 1
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Attribute):
            if isinstance(x.value.value, ast.Name):
                return 1
        return 0


if __name__ == "__main__":
    e = Em()
    rs = [e.f(ast.parse(s, mode="eval").body) for s in ("List[int]", "a[0]", "self.a[0]", "x")]
    print("VIOLATION" if any(r < 0 or r > 2 for r in rs) else "result", rs)
