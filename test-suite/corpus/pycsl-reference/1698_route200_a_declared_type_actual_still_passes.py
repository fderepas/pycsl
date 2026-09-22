r"""Test 1698 - ROUTE #200 control (gen #30): the refusal is keyed on the DECLARED annotation and on a STRING literal actual, so a genuine int into an `int` parameter and a genuine string into a `str` parameter both still verify. Without this control the #200 refusal could have been the blunt one - refusing every literal at a call boundary, or every string anywhere - and the corpus would not have noticed.
"""

_ = 0  # anchor


#@ requires True
#@ ensures p == 5 ==> \result == 1
#@ ensures p != 5 ==> \result == 2
def callee(p: int) -> int:
    if p == 5:
        return 1
    return 2


#@ requires True
#@ ensures True
def takes_str(s: str) -> int:
    return 7


#@ ensures \result == 1
def probe() -> int:
    _ = takes_str("a")
    return callee(5)
