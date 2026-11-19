r"""Test 9582 -- route #585 CONTROL (expected PASS): CONTROL: the honest bound through `.slice` of both Subscript and SliceAccess proves.
"""
# pycsl-expected: PASS
def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 3
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "Subscript":
            if x.slice.kind == "Var":
                return 3
            return 2
        if x.kind == "SliceAccess":
            if x.slice.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(__import__("types").SimpleNamespace(kind="Subscript", slice=__import__("types").SimpleNamespace(kind="Var")))
    print("result", r)
