# pycsl-flags: --memory-model hoare
# pycsl-expected: PASS
"""1297 — (#49) ROUTE #106 CAPABILITY ARM. The repair suppresses INLINING for exactly one
(caller, callee) pair — the one whose obligation was being deleted — and must not otherwise
change what a module-global program can prove.

`caller` adds `#@ requires k >= 0`, which discharges the restored
`assert { not ((k < 0)) }`. The call is no longer inlined for this caller; it lowers to the
callee's contract and the whole file proves.

CENSUS THAT SIZED THE REPAIR: across the 71 corpus/source files declaring `#@ no_exception`,
NOT ONE also declares a module-global instance — so the change is byte-inert on the corpus
today. It is a fence for the shape, not a migration. A guard whose population is empty has
checked nothing and looks exactly like a guard that passed, which is why 1296 negative-tests
it directly.

Must PASS.
"""


class Helper:
    def __init__(self) -> None:
        self.tag = 0

    #@ raises ValueError when x0 < 0
    #@ ensures \result >= 0
    def f(self, x0: int) -> int:
        if x0 < 0:
            raise ValueError("neg")
        return x0


_h = Helper()


#@ requires k >= 0
#@ no_exception ValueError
def caller(k: int) -> int:
    return _h.f(k)
