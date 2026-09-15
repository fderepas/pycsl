r"""P0 positive control — plain set literal, no mutation: `in` must PROVE."""
_ = 0  # anchor
XS = {"a", "b"}


#@ ensures \result == False
#@ assigns \nothing
def has_c() -> bool:
    return "c" in XS
