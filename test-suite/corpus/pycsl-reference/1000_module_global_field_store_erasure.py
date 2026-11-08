"""Test 1000 — a MODULE-GLOBAL singleton field store `g.v = n` was a SILENT NO-OP, and the
no-op proved a false postcondition. ROUTE #28.

`Module5_IREmitter._py_stmt_assign` handled `self.f = v` and `p.f = v` (p in the function
symbol table) and, for a Name base NOT in the symbol table, fell off the end of its `elif`
chain with a comment: "keep the prior no-op (byte-identical; separate boundary from the
record/list PARAM class handled above)". A documented no-op, carried for windows, never
probed. Measured, before the fix, on exactly this body:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 7. The store vanished and the read returned the initialiser.

IT WAS NEVER A MODELLING LIMIT. A module-level `g = C()` already emits a real global
mutable record — `let g : c = { v = 0 }` — so `g.v <- n` has always been expressible. The
arm simply never emitted anything. So this is a CAPABILITY: the companion contract
`#@ assigns g.v` + `#@ ensures \result == 7` on the same body now PROVES, and a function
that writes a global WITHOUT declaring it is rejected by Why3's own frame check rather
than silently believed.

CENSUS: four module-global field stores exist tree-wide, all in the HAPPY ownership tests
0611/0612/0613, and all three keep their expected verdicts (0611 PASSES, 0612 FAILS at its
injected `#@ check False`, 0613 is still rejected at weave time for aliasing a protected
base). Exactly TWO corpus emissions move — 0611 and 0612 — and `python-reference` is
2142/2142 byte-identical.

*** AND THE MIRROR HALF OF THIS IS THE LESSON. *** The mirror's `_py_stmt_assign` is
CONVERTED, and its WhyML model is a HAND-SYNTHESIZED bespoke lowering keyed on the method
NAME (`_emit_py_stmt_assign_bespoke`). Changing the live body and syncing the mirror source
left `check-self-annotate-sync.sh` GREEN, L3-tc GREEN, and the mirror emission
BYTE-IDENTICAL — while the emitted model still read `else ()` where the source now
appends a `FieldAssign`. The model had silently stopped being the body, and no plane in the
battery could see it; only reading the emitted `.mlw` did. The bespoke lowering had to move
in the same increment, and after it does, four mirror emissions change by the identical two
lines.

This file is `pycsl-expected: FAIL`: the postcondition is FALSE of the program.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires g.v == 0
#@ assigns g.v
#@ ensures \result == 0
def f() -> int:
    g.v = 7
    return g.v


if __name__ == "__main__":
    print(f())
