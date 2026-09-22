r"""Test 1721 — ROUTE #212: a class invariant the OWNING module fails to establish is
believed, unchecked, by every importer.

This is route #205's shape for CLASS INVARIANTS. The owner module

    #@ class invariant self.v >= 0
    class C:
        def __init__(self) -> None:
            self.v: int = 0
        #@ assigns self.v
        def sink(self) -> None:
            self.v = 0 - 5

FAILS when compiled on its own, exactly as it should — `sink` breaks the declared
invariant. An IMPORTER of `C` then PROVED

    #@ ensures \result >= 0
    def probe() -> int:
        c = C()
        c.sink()
        return c.v

while CPython answers **-5**, and the TRUE twin `\result == 0 - 5` was REFUSED in the same
importer. The invariant rides along as a type invariant on the imported record and nothing
in the importing unit ever discharges it.

THIS FILE IS THE CARRIER FOR THE SINGLE-FILE HALF, which is what the corpus runner can
execute: compiled alone it must FAIL. The two-file half lives in the probe ledger with its
exact commands, because the runner compiles one file at a time.

STATUS: recorded as an OPEN route with its price rather than repaired in the window. The
cheap repairs are both wrong: refusing every import of an invariant-bearing class would
break legitimate multi-file programs (0441, 0443), and dropping the invariant from imported
records would weaken every honest importer. The right fix is the one route #205 used —
re-emit the obligation in the importing unit — which for an invariant means re-proving
preservation for each imported method, and that needs the method BODIES, which the
importing unit deliberately does not lower.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    def sink(self) -> None:
        self.v = 0 - 5
