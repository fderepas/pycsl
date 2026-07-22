"""NEGATIVE twin of 0936 — this file MUST NOT prove.

It claims the CONVERSE of `any`: that a FALSE result implies some element is big. That is
false, and the bounded fold's iff postcondition is exactly what refutes it. If this ever
proves, the fold has become vacuous and 0936's green is worthless.

Non-vacuity here is the EVIL TWIN, not a mutation test: an int-hash-erased body still moves
the emitted .mlw when a literal changes, so a mutation test cannot see this failure mode
(wall-lessons (l))."""
from typing import List


#@ requires n >= 0 and \length(xs) == n
#@ ensures \result == False ==> (\exists k; 0 <= k and k < n and xs[k] > 10)
#@ assigns \nothing
def evil(xs: List[int], n: int) -> bool:
    return any(x > 10 for x in xs)
