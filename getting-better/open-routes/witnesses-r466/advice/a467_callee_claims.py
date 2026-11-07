"""Advice probe (route #467, PYCSL-R467-IMPORTED-UNCLAIMED): 'Give the imported function its own
`#@ no_exception` claim covering the caller's' -- the helper's `assert` is discharged by its own
`requires`, which the caller establishes. VERIFIES."""
from x1_hc467 import g


#@ no_exception \all
#@ requires n >= 0
#@ ensures \result == n
def f(n: int) -> int:
    return g(n)
