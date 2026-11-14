r"""W-hash advice audit: witness 9883 with the advice "derive it from a source declared with a hashable type" followed (`v: str`). Expected: VERIFIES under `no_exception \all`."""


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: str, n: int) -> int:
    if isinstance(v, str):
        n = n + 0
    s = {v}
    return n + 1
