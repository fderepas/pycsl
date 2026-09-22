r"""ROUTE #215 CARRIER — an erased local REBOUND collapses two different values into one.

Not in the corpus, for the standing reason: it PROVES today, so `# pycsl-expected: FAIL`
would be an XPASS (a red suite) and `PASS` would write "this false proof is expected" into
the corpus. `bin/check-open-route-carriers.py` runs it and asserts the recorded verdict.

MEASURED: `probe()` PROVES `#@ ensures \result == 0`. CPython answers **-1**.
The TRUE twin (`\result == 0 - 1`) is REFUSED.
"""
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == n
def ident[T](n: int) -> int:
    return n


#@ ensures \result == 0
def probe() -> int:
    a = ident[int](1)
    x = a
    a = ident[int](2)
    return x - a


if __name__ == "__main__":
    print("probe() =", probe())
