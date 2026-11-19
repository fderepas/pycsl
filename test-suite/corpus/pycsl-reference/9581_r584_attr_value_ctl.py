r"""Test 9581 -- route #584 CONTROL (expected PASS): CONTROL: the honest two-sided bound through `.value` of a NamedExpr node proves.
"""
# pycsl-expected: PASS
def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 2
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "NamedExpr":
            if x.value.kind == "Var":
                return 2
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(__import__("types").SimpleNamespace(kind="NamedExpr", value=__import__("types").SimpleNamespace(kind="Var")))
    print("result", r)
