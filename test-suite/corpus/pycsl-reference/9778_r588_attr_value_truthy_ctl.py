r"""Test 9778 -- route #588 CONTROL (expected PASS): CONTROL: after `isinstance(x, ast.Attribute)` the object `.value` is a node, truthy by the modelled IrAttr arm.
"""
# pycsl-expected: PASS
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result != 2
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute):
            if x.value:
                return 1
            return 2
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("a.b", mode="eval").body)
    print("VIOLATION contract" if r == 2 else "result", r)
