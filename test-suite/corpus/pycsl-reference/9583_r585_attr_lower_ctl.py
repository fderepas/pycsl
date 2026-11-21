r"""Test 9583 -- route #585 CONTROL (expected PASS): CONTROL: the honest bound through `.lower` of a Slice node proves.
"""
# pycsl-expected: PASS
def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 2
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "Slice":
            if x.lower.kind == "Var":
                return 2
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(__import__("types").SimpleNamespace(kind="Slice", lower=__import__("types").SimpleNamespace(kind="Var")))
    print("result", r)
