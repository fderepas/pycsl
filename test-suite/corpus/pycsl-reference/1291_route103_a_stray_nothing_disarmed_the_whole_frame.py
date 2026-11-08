# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1291 — (#49) ROUTE #103 EXPLOIT ARM: a stray `#@ assigns \\nothing` written BESIDE a real
target disarmed BOTH the frame AND route #98's refusal.

`Module5_IREmitter` flattens EVERY `#@ assigns` clause of a function into ONE list, so the
pair below arrives at `_emit_frame_condition` with `nothings` NON-EMPTY *and* a real region
target. Both guards there were written `... and not nothings`:

    if _unframed_regions and not nothings:   -> route #98's refusal SKIPPED
    if _val_targets     and not nothings:    -> the real `writes` DROPPED

so the val came out PURE and the caller proved `\\result == 7` across a stub contracted to
write `g`. CPython returns 5.

ORDER 2 — the carrier is THE CAMPAIGN'S OWN ARTEFACT. `and not nothings` was written by route
#96's repair to keep `\\nothing` meaning "writes nothing". The intent was right and the scope
was one conjunct too wide: it let ONE clause silence the OTHERS. It also SURVIVED route
#101's repair, measured, which is why it is a route and not a footnote.

THE REPAIR IS A REFUSAL, NOT A PRECEDENCE RULE: the two clauses CONTRADICT, and any winner
the emitter picks is a guess about what the reviewer meant. A repo-wide census of every
contiguous `#@ assigns` block found ZERO functions mixing the two, so the refusal has an
empty live population — and a guard whose population is empty has checked nothing and looks
exactly like a guard that passed, which is why this negative test exists.

Must FAIL, with `PYCSL-CONTRADICTORY-ASSIGNS`.
"""


#@ \trusted reviewer: route103
#@ requires \length(g) > 0
#@ assigns g[0..1]
#@ assigns \nothing
def scramble(g: list) -> None:
    g[0] = 5


#@ requires \length(a) > 0
#@ requires a[0] == 7
#@ ensures \result == 7
def driver(a: list) -> int:
    scramble(a)
    return a[0]
