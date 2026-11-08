"""Test 1254 — route #93, NEGATIVE: a `total` target may not be `\trusted`.

`#@ happy availability: targets parse total` is macsl's `\context(\total)` — it NAMES PyCSL's
default-on termination guarantee so an attacker-controlled input cannot cause non-termination.
The policy EMITS NOTHING; it relies wholly on the termination VC Why3 generates for the
target's body, and its enforcement was a single check rejecting `#@ \diverges`, described in
the source as "the only opt-out".

IT WAS NOT THE ONLY OPT-OUT. `#@ \trusted` (and `#@ \abstract`, see 1255) make Module 6 emit
the function as a bodyless `val` — "contract only, no goals" — so there is no loop, no
termination VC, and the guarantee the policy names is simply ABSENT.

MEASURED BEFORE THE REPAIR: this file VERIFIED, with a body of `while True: acc = acc + 1`
that cannot terminate. It differs from 0728 by ONE annotation line, and that line flips a
FAILED verdict to SUCCESS while making the body strictly worse — 0728's loop merely lacked a
`#@ loop variant`; this one cannot terminate at all. Controls, all pre-existing and written by
the feature's own author: 0726 PROVES (bounded loop with a variant), 0727 is a PIPELINE ERROR
(the one guarded opt-out), 0728 FAILS (the termination VC demonstrably fires).

All three SIBLING happy forms already carry a trusted/abstract trust boundary — `protects`
(R1.1) and region-write (C) demand `#@ \preserves`, `reading` (iv) demands `except` membership
— so the codebase's settled convention is that a BODYLESS SUBJECT DOES NOT GET TO SATISFY A
HAPPY PROPERTY BY DEFAULT. H-D was the only form with no trust boundary at all. Unlike
preservation, totality has no meaningful opt-in (no postcondition expresses "this bodyless
`val` terminates"), so the resolution is the `reading` form's: reject.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ \trusted reviewer: demo
    #@ requires n >= 0
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        i: int = 0
        acc: int = 0
        while True:               # cannot terminate; body never checked
            acc = acc + 1
        return acc
