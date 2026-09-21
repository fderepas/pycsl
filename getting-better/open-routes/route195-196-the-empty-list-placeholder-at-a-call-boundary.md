# ROUTES #195 and #196 — the EMPTY-LIST placeholder at a call boundary, read two different ways

**Status: CLOSED by gen #30 (battery F green: suite 3815/3833, same 18 CONFIRMED FAIL, zero XPASS;
planes --slow 40/40; 2 CHANGED mirrors whole-file prove 2/2).** Severity 1 each.
Generator: **`bin/check-argument-coercion.py`'s own baseline, swept entry by entry with ONE probe.**

## The probe, stated once because it found all three of #194, #195 and #196

> Give the callee a contract that is **TRUE of its own body** and that **READS the property the
> substitution changes**. Call it with the substituted-away shape. Run CPython.

A callee with `ensures True` hides every one of these defects completely. That is why this surface
survived 190 routes: nobody had written a callee that *looked at* the argument.

## ROUTE #195 — the placeholder became the integer 0 at an INT-ERASED param

    #@ ensures p == 0 ==> \result == 1     <- TRUE of this body
    def f(self, p) -> int:                 <- un-annotated: the val declares `p: int`
        if p == 0: return 1
        return 2

    #@ ensures \result == 1
    def probe(self) -> int: return self.f([])      PROVED   (CPython 2)

emitted `(p__f self 0)`. `[] == 0` is False in Python. The baseline had said the substitution
"loses nothing the placeholder had ... and the callee is a `\trusted` `val` with `ensures true`, so
NO property of the argument is provable on either side" — **the callee does not have to be
`\trusted` and does not have to say `ensures true`.** Repaired with `(any int)`: there is no int
that represents a list, so the model must not name one.

## ROUTE #196 — the same placeholder is 1024 ELEMENTS LONG at an `array int` param

    #@ ensures \result == \length(ns)      <- TRUE of this body
    def g(self, ns: List[int]) -> int: return len(ns)

    #@ ensures \result == 1024
    def probe(self) -> int: return self.g([])      PROVED   (CPython 0)

emitted `(p__g self (Array.make 1024 0))`. And the sharper half: **CPython's own answer, `\result
== 0`, was REFUSED.** Route #159 corrected this exact placeholder's `in_bounds` obligation with a
post-hoc regex rewrite of the emitted text — that is about INDEXING, and says nothing about LENGTH
at a call boundary.

Repaired with the genuinely EMPTY array `(Array.make 0 0)` — which is **FAITHFUL, not merely
opaque**: `[]` really does have length 0, so witness 1690 now proves what the model could not prove
before. The `array emit_ir` arm three lines above had been doing exactly this for the same
placeholder all along. `List[str]` was measured and fails closed, so no `array string` arm was
added — a repair that closes nothing measured does not belong in the repair.

## Cost

Corpus BYTE-INERT, python-reference BYTE-INERT, **two mirrors moved** (`core_ir_semantic`:
`func_get_2 <hash> 0` → `… (any int)`; `module6_whyml/statements`: `(Array.make 1024 0)` →
`(Array.make 0 0)`), each diff exactly the intended correction. The mirror's own
`_coerce_dotted_args` is `\trusted`, so no mirror edit was owed. Witnesses 1687, 1689 (XFAIL) and
1690 (PASS).

## Lesson

>>> A BASELINE ENTRY IS A CLAIM, AND A SWEEP OF THE BASELINE IS A ROUTE-FINDING METHOD. Three of the
>>> fourteen entries in a plane written the same afternoon fell to one probe within nine hours, and
>>> not one line of the emitter had changed since gen #29. What changed is that someone had to write
>>> down *why* each substitution was safe — and two of those sentences were false.
>>>
>>> A PLACEHOLDER HAS EVERY PROPERTY ITS REPRESENTATION HAS, NOT JUST THE ONE YOU WERE THINKING
>>> ABOUT. `(Array.make 1024 0)` was chosen so an empty list would type-check; it also has a
>>> LENGTH, and an ELEMENT VALUE, and an equality with 0 after int-erasure. Each of those is a
>>> question the model will answer.
