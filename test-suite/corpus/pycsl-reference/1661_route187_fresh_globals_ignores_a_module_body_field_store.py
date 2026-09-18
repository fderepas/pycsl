r"""Test 1661 - ROUTE #187 (gen #29): `#@ fresh_globals` assumes the module-global's CONSTRUCTOR post-state, and the module body's own `counter.n = 7` — which the IR does not record at all — is invisible to it, so `\result == 0` PROVED while CPython returns 7. A module body that is not imports, definitions and simple bindings is now refused (PYCSL-R187-FRESH-GLOBALS-MODULE-BODY).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Counter:
    #@ assigns self.n
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0


counter = Counter()
counter.n = 7


#@ ensures \result == 0
#@ fresh_globals
def probe() -> int:
    return counter.n
