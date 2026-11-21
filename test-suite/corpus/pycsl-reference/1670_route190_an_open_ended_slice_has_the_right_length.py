r"""Test 1670 - ROUTE #190 control (gen #29): with the omitted bound read as the string's own length, an open-ended slice has the length Python gives it. FAILS at HEAD (the model decided the slice was empty, so `len(t) == 2` was unprovable).
"""
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    s: str = "abc"
    t: str = s[1:]
    return len(t)
