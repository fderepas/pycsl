r"""Test 9777 -- route #588 CONTROL (expected PASS): CONTROL: after `isinstance(x, ast.Subscript)` the index `.slice` is a node, truthy by the modelled arm.
"""
# pycsl-expected: PASS
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result != 2
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Subscript):
            if x.slice:
                return 1
            return 2
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("a[i]", mode="eval").body)
    print("VIOLATION contract" if r == 2 else "result", r)
