r"""Test 10175 -- route #612 (expected FAIL): an annotated local alias `g: Callable[[int], int] = f` of a `Callable` parameter, then `g(x) == g(x)`. The alias is itself `Callable`-typed. At base 0057c8b94 it was NOT proved: the emission declared the alias `let g = ref 0` (an `int`) and Why3's typecheck rejected `g := f` (hoare / typed / store), so the only thing holding it was the backend's type error, not a rule; this is a fail-closed HARDENING witness. CPython with `itertools.count` returns False (the driver prints VIOLATION). Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable


#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], x: int) -> bool:
    g: Callable[[int], int] = f
    return g(x) == g(x)


if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), 0)
    print("VIOLATION" if r is not True else "result", r)
