r"""Test 9551 -- route #584 WITNESS (expected FAIL: the claim is FALSE of the program): the dict view `.get("value", {})` of a `MapSet` node reads its value; at base this read was `IrOther ""` on this constructor and the false `\result` claim PROVED. CPython breaks the claim.
"""
# pycsl-expected: FAIL
def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.get("type") == "MapSet":
            v = x.get("value", {})
            if v.get("type") == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "MapSet", "dict": {"type": "Var", "name": "m"}, "key": {"type": "Number", "value": 1}, "value": {"type": "Var", "name": "a"}})
    print("VIOLATION contract" if r != 0 else "result", r)
