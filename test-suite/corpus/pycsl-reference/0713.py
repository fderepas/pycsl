"""Test 0713 — `#@ fresh_globals` surfaces a module-global's constructor post-state.

Why3 verifies every importer function with each shared mutable module-global in an
ARBITRARY (havoc'd) state, so a standalone driver cannot rely on the freshly-imported
initial state. `#@ fresh_globals` re-establishes, at the driver's body entry, each
module-global singleton's CONSTRUCTOR post-state (the class `__init__`'s `#@ ensures`,
`self` -> the global) as an ASSUMED fact. The assumed fact is PROOF-BACKED: the
transpiler also emits `let counter_fresh_init () : Counter ensures {...} = <ctor literal>`
which proves the post-state holds of the freshly constructed global.

Here the constructor establishes `self.n == 0`. The driver `probe` is marked
`#@ fresh_globals`, so `counter.n == 0` is assumed at entry and the assertion proves —
WITHOUT it, `counter.n` is havoc'd and the assertion fails. Module4 confines the
directive to a standalone top-level driver: it is REJECTED on a method or any callee
(`PYCSL-SEM-FRESH-GLOBALS`).
"""


class Counter:
    #@ assigns self.n
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0


counter = Counter()


#@ requires True
#@ ensures \result == 0
#@ fresh_globals
def probe() -> int:
    # `#@ fresh_globals` assumed `counter.n == 0` (the constructor post-state) at entry,
    # so this reads the freshly-imported value — provable here, havoc'd without it.
    #@ assert counter.n == 0
    return counter.n
