"""CAL good — list length is tracked separately from the 1024 backing (G5 is NOT a bug).
len([10,20,30])==3 must PROVE and ==1024 must NOT (see cal_listlen_falsetwin)."""
_ = 0
#@ ensures \result == 3
def f() -> int:
    a = [10, 20, 30]
    return len(a)
