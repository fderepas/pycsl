# pycsl-flags: --memory-model hoare
# pycsl-expected: PASS
"""1295 — (#49) ROUTE #105 CAPABILITY ARM. Restoring the obligation must not refuse every
call through a record variable — only the ones that cannot discharge it.

`caller` adds `#@ requires k >= 0`, which is exactly what the emitted
`assert { not ((k < 0)) }` needs. The obligation now EXISTS and is DISCHARGED.

This is the arm that separates a fence from a wall. Must PASS.
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


#@ requires k >= 0
#@ no_exception ValueError
def caller(k: int) -> int:
    c = Helper()
    return c.f(k)
