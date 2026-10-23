r"""Test 1696 - ROUTE #199 completeness witness (gen #30): the repair is FAITHFUL, not opaque. #191-#198 all answered "UNKNOWN" because the true value was unavailable; here it is available and exact, so the TRUE contract - REFUSED before the repair - now PROVES. A route whose repair restores a true contract instead of leaving both twins undecided is worth a witness of its own, because a later "simplification" to an opaque would still pass 1695 and would silently lose this.
"""

_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s = f""
    if s == "":
        return 1
    return 2
