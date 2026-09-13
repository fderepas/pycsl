# pycsl-flags: --memory-model hoare
# pycsl-expected: PASS
"""1293 — (#49) ROUTE #104 CAPABILITY ARM. Over-approximating `self.xs[i]` to the whole of
`self.xs` is SOUND — more havoc is strictly LESS caller knowledge — but it must not cost the
real capability: a caller that HONESTLY DECLARES its own frame must still prove facts about
the fields the stub does not touch.

Here `poke` writes `self.xs`, `driver` declares `#@ assigns self.xs`, and `self.n` is
untouched — so `\\result == 4` must still prove. It PASSES on both sides of the change, which
is how we know the repair moved only the unsound arm.

Note what does NOT hold, and correctly so: drop `#@ assigns self.xs` from `driver` and this
FAILS — a caller promising to write nothing while calling a stub that writes is an honest
failure, and it fails identically for the whole-field spelling `#@ assigns self.xs`. The
subscript spelling now behaves EXACTLY like the field spelling; that is the whole repair.

Must PASS.
"""


class Box:
    def __init__(self) -> None:
        self.xs = [7, 7, 7]
        self.n = 0

    #@ \trusted reviewer: route104-ctl
    #@ requires \length(self.xs) > 0
    #@ assigns self.xs[0]
    def poke(self) -> None:
        self.xs[0] = 5

    #@ assigns self.xs
    #@ requires \length(self.xs) > 0
    #@ requires self.n == 4
    #@ ensures \result == 4
    def driver(self) -> int:
        self.poke()
        return self.n
