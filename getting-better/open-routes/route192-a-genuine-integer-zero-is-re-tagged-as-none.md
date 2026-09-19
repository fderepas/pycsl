# ROUTE #192 — a genuine integer `0` is silently re-tagged as the Python `None` at an `Optional[<record>]` / union parameter slot

**Status: CLOSED by gen #30 (battery B green: suite 3808/3826, same 18 CONFIRMED FAIL, zero XPASS;
planes --slow 39/39; emission BYTE-INERT in all three directions).** Severity 1.
Generator: route #191's own repair — the moment `None` stopped sharing a spelling with the integer 0,
the arm that recognised it by that spelling became discriminating, and wrong.

## Measured at `0c481f0a` (i.e. WITH route #191 landed)

    class Parser:                                  # @mutable_state, records Tok
        #@ ensures start == None ==> \result == 1
        def tag(self, start: Optional[Tok]) -> int:
            if start is None: return 1
            return 2

        #@ ensures \result == 1
        def probe(self) -> int:
            return self.tag(0)                     PROVED   (CPython 2)

and the synthesized-union twin:

        #@ ensures value == None ==> \result == 1
        def expect(self, kind: str, value: Optional[str] = None) -> int: ...

        #@ ensures \result == 1
        def probe(self) -> int:
            return self.expect("RPAREN", 0)        PROVED   (CPython 2)

The emitted call sites say it outright:

    (parser__tag self (None: option tok))
    (parser__expect self "RPAREN" (Arm_0_None : _union_expect_0))

The callee's contract is TRUE of its own body — it really does return 1 exactly when the argument is
the `None` singleton — so nothing here is vacuous. The wrongness is entirely in the ACTUAL: a genuine
integer `0` arrives at the slot and is handed to the callee as `None`. The TRUE twin (`\result == 2`,
which is CPython's answer) is REFUSED, which is the decisive signature.

## Why the guard that was supposed to prevent this did not

`expressions.py`'s `option <record>` lift and the `_union_*` twin beside it both test the ALREADY-LOWERED
argument TEXT:

    if _s in ("0", "(0)"):  coerced.append(f"(None: {ptype})")

with the stated premise, in the code, that this is

> "Restricted to a literal `0` actual, so a genuinely int-valued expression flowing into a union slot
> still fails LOUDLY rather than being silently re-tagged as None."

A literal `0` actual **is** a genuinely int-valued expression. The premise was only ever true because,
before route #191, the Python `None` ALSO lowered to `"0"` — the spelling was shared, so the arm could
not tell the two apart and the comment described the intent rather than the rule.

## Repair

Drop the `"0"` / `"(0)"` spellings from both tests; keep only `pycsl_none` / `(pycsl_none)`. After route
#191 that is exactly the set of actuals that really ARE `None`:

* an OMITTED optional argument, filled from the Python `None` default — still lifts (witness 1681);
* an EXPLICIT `None` actual — still lifts (witness 1682);
* a genuine integer `0` — now falls through and the call is ILL-TYPED (`This expression has type int,
  but is expected to have type option tok` / `_union_expect_0`), i.e. REFUSED rather than answered
  wrongly (witnesses 1679, 1680).

Emission byte-inert: corpus 0 MOVED, python-reference 0 MOVED, **mirrors 0 MOVED** — so no mirror
whole-file re-proof was owed, which is what made this route cost one battery instead of eight hours of
prover time.

## Lesson

>>> A LOWERING THAT RECOGNISES A PYTHON VALUE BY ITS WHYML SPELLING IS SOUND ONLY AS LONG AS THAT
>>> SPELLING IS UNIQUE TO THAT VALUE, AND NOTHING IN THE CODE ENFORCES THAT. Two values sharing one
>>> spelling makes the test a COINCIDENCE; the comment beside it will describe the value ("a literal
>>> `0` actual", meaning the `None` default) while the predicate matches the spelling. Route #191 broke
>>> the coincidence in the SAFE direction — the lift missed and the file failed to type-check, loudly —
>>> and the SAME break, read the other way, is this route. Every fix that changes what something lowers
>>> to should be followed by a census of who was reading the old spelling.
