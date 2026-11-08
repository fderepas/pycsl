r"""P6 — #132 ref-walk carrier: the folded dict mutated through `globals()["OP"]`."""
_ = 0  # anchor
OP = {"a": "b"}
globals()["OP"]["a"] = "c"


#@ ensures \result == "b"
#@ assigns \nothing
def g() -> str:
    return OP.get("a", "")
