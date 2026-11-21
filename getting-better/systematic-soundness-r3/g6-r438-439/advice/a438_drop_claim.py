# Advice probe (route #438, PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM): witness 6601 with the claim
# dropped (the TypeError is then ambient: an abnormal exit). Expected: VERIFIES.
#@ ensures \result == n + 1
def f(t: tuple, n: int) -> int:
    s = {t}
    return n + 1
