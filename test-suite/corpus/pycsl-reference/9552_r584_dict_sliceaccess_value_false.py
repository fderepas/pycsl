r"""Test 9552 -- route #584 WITNESS (expected FAIL: the claim is FALSE of the program): the dict view `.get("value", {})` of a `SliceAccess` node reads its value; at base this read was `IrOther ""` on this constructor and the false `\result` claim PROVED. CPython breaks the claim.
"""
# pycsl-expected: FAIL
def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.get("type") == "SliceAccess":
            v = x.get("value", {})
            if v.get("type") == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "SliceAccess", "value": {"type": "Var", "name": "a"}, "slice": {"type": "Slice"}})
    print("VIOLATION contract" if r != 0 else "result", r)
