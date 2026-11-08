r"""P2 — #132 carrier: `set([...])` list-arg str-set literal."""
_ = 0  # anchor
XS = set(["a", "b"])
XS.add("c")


#@ ensures \result == False
#@ assigns \nothing
def has_c() -> bool:
    return "c" in XS
