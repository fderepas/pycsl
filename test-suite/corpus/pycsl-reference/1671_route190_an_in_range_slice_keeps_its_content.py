r"""Test 1671 - ROUTE #190 control (gen #29): guarding the substring bridge's content equality by the in-range condition does not cost the in-range fact — an open-ended slice still compares equal to the string it is. The claim is discharged by the CONTENT law, not by a length: flipping the comparison to a different literal leaves it unproven.
"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s: str = "abc"
    t: str = s[1:]
    if t == "bc":
        return 1
    return 0
