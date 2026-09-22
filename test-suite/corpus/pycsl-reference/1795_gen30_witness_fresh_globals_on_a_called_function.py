r"""Test 1795 — WITNESS: `#@ fresh_globals` on a function that ANOTHER verified function calls.

The directive re-establishes the module-global constructor post-state as an ASSUMED entry
fact. That is sound only for a top-level driver that runs on a freshly-imported global: a
CALLEE inherits its caller's possibly-already-mutated global, so assuming the fresh state
at its entry would be unsound. The sibling arm — the directive on a METHOD — is witness
1748; this is the CALLED-ELSEWHERE arm, which was still unwitnessed.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class Counter:
    def __init__(self) -> None:
        self.n: int = 0


g = Counter()


#@ fresh_globals
#@ ensures \result == 0
def driver() -> int:
    return g.n


#@ ensures \result == 0
def caller() -> int:
    return driver()
