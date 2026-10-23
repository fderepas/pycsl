r"""P3 positive control — module str->str const dict read."""
_ = 0  # anchor
OP = {"a": "b"}


#@ ensures \result == "b"
#@ assigns \nothing
def g() -> str:
    return OP["a"]
