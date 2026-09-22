r"""Test 1715 — ROUTE #208: `happy ... total` proved of a target that calls a
`#@ \diverges` helper — the most EXPLICIT declaration of non-termination the language has.

Route #93 rejected `#@ \diverges` ON THE TARGET; it was the very first opt-out that check
ever named. Route #206 added bodyless CALLEES (`\trusted` / `\abstract`). A `\diverges`
CALLEE is neither: it HAS a body, and it carries no termination VC because it explicitly
opted out. MEASURED: this file — 1711's shape with `#@ \diverges` in place of
`#@ \trusted` — printed "Verification SUCCESS! All contracts formally proven" TWENTY
MINUTES AFTER route #206's repair landed, which is this campaign's own lesson (i) ("name
which SPELLINGS were run") missed on my own repair.

The rule the check always meant is "every module-local function with NO termination VC",
not "every bodyless one". CPython: `Parser().parse(1)` never returns. Controls: 1712
(verified helper) and 0726 (bounded loop with a variant) both still PROVE.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ ensures \result >= 0
    #@ \diverges
    def spin(self, n: int) -> int:
        acc: int = 0
        while True:
            acc = acc + 1
        return acc

    #@ requires n >= 0
    #@ no_exception \all
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        return self.spin(n)
