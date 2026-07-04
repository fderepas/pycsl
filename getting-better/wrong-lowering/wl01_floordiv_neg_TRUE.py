"""WL-01 companion — the TRUE Python value (-7)//(-2)==3 is UNPROVABLE
(PyCSL models it as Euclidean 4). Detector D3: can't-prove-true."""
_ = 0
#@ ensures \result == 3
def f() -> int:
    return (-7) // (-2)
