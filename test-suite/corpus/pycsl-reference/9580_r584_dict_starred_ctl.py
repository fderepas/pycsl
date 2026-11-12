r"""Test 9580 -- route #584 CONTROL (expected PASS): CONTROL: the honest two-sided bound through the dict view `.get("value", {})` of a Starred node proves (no refusal).
"""
# pycsl-expected: PASS
def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 2
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.get("type") == "Starred":
            v = x.get("value", {})
            if v.get("type") == "Var":
                return 2
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "Starred", "value": {"type": "Var", "name": "a"}})
    print("result", r)
