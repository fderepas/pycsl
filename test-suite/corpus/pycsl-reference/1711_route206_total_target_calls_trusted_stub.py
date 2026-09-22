r"""Test 1711 — ROUTE #206: `happy ... total` proved of a target whose work is ONE CALL to
a `\trusted` stub that cannot terminate.

Route #93 closed "the TARGET is bodyless" (`\trusted` / `\abstract` on the target itself,
witnesses 1254/1255). This is the same hole ONE HOP AWAY: the target has a perfectly good
body, and all of it is a call to a bodyless stub. A call to a `val` is ASSUMED to return,
so the target's termination VC is discharged while the program never terminates.

MEASURED BEFORE THE REPAIR: this file printed "Verification SUCCESS! All contracts formally
proven" — an AVAILABILITY policy, whose stated purpose is that an attacker-controlled input
cannot cause non-termination, proved of a function that hangs. CPython: `Parser().parse(1)`
never returns.

The repair extends route #93's check to the target's whole module-local call graph.
Controls, all unchanged: 0726 PROVES (bounded loop with a variant), 0727 is a PIPELINE
ERROR (`\diverges`), 0728 FAILS (the termination VC fires), 1254/1255 stay PIPELINE ERRORs.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ ensures \result >= 0
    #@ \trusted
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
