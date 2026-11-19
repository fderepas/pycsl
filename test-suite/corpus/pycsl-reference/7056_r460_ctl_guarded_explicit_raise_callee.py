r"""Test 7056 -- route #460 (expected PASS): CONTROL -- an un-claimed `g` with an EXPLICIT, DECLARED `raise ValueError` (`#@ raises ValueError when n < 0`: modelled, it escapes to the caller and is judged at the call site), guarded by the claiming `f` (`#@ no_exception \all`); the reached claim does not turn g's own raise into an obligation of g. PROVED at base and candidate.
"""
# pycsl-expected: PASS


#@ raises ValueError when n < 0
def g(n: int) -> int:
    if n < 0:
        raise ValueError("negative")
    return n + 1


#@ no_exception \all
def f(n: int) -> int:
    if n >= 0:
        return g(n)
    return 0


if __name__ == "__main__":
    print(f(2), f(-1))
