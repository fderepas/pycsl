# ROUTE #197 — `getattr(o, name, default)` on an object of UNKNOWN static type ANSWERED THE DEFAULT

**Status: CLOSED by gen #30 (battery J2 green: suite 3817/3835, same 18 CONFIRMED FAIL, zero XPASS;
planes --slow 42/42; 3 CHANGED mirrors whole-file prove 3/3).** Severity 1.
Generator: **`bin/check-getattr-erasure.py`'s own ratchet note**, swept the same way the
argument-coercion plane's baseline was swept nine hours earlier.

## Measured at `7b05caf1`

    class C:
        def __init__(self): self.a: int = 7

    #@ ensures \result == 1
    def peek(o: Any) -> int:
        v = getattr(o, "a", 0)
        if v == 0: return 1
        return 2                                  PROVED   (CPython peek(C()) == 2)

emitted `let v = ref 0 in v := 0;` — and Why3 says the rest out loud: **`unused variable o`**. The
object is discarded and the default is the answer. The TRUE twin (`\result == 2`) is REFUSED.

## The justification that was refuted, and why it was nearly right

`check-getattr-erasure.py` classifies every fall-through DECLARED / ABSENT / UNKNOWN, pins DECLARED
at hard zero (route #22), and holds UNKNOWN at a ratchet with this note:

> "the default is a GUESS. Not demonstrated to be exploitable — **a contract cannot name a field of
> an object whose type the model does not carry** — but it is not sound by argument either, so it is
> held by a ratchet rather than called safe."

Holding it by a ratchet was right. The reason was wrong in one word: **the CONTRACT does not have to
name the field. The BODY reads it, and the contract reads `\result`.** That is the same move that
found routes #194, #195 and #196 at the argument boundary — give something a contract that is TRUE of
its own body and that READS the property the model invented.

## Repair, and the version of it that the emission census refuted

The UNKNOWN classification was **already computed** by the emitter — inside the
`PYCSL_GETATTR_CENSUS` env gate. The emitter KNEW which case it was in and used that knowledge only
to print a line for a plane. It is now computed always (three dict lookups) and UNKNOWN answers an
opaque.

**The first version returned Why3's `(any int)` and was wrong.** The emission census showed it also
replaced route #47's EXISTING per-site opaques (`pycsl_getattr_missing_<hash>` for the no-default
form, `pycsl_getattr_default_<hash>` for a non-scalar default) — and `(any int)` is FRESH AT EVERY
EVALUATION while a per-site opaque is STABLE, so two reads of the SAME `getattr` expression would
stop agreeing. That is a real loss of faithfulness for no gain. The landed version touches only the
SCALAR-DEFAULT UNKNOWN case and uses route #47's own device: a per-site opaque hashed on the call's
IR.

ABSENT is untouched — `getattr` really does return the default when the record type is known and
does not declare the name, and that faithful answer is exactly what route #22's gate exists to
protect (witness 1692).

## Cost, and a better-than-expected side effect

Corpus BYTE-INERT (route #47's witnesses 1070-1073 stop moving once the repair is narrowed),
python-reference BYTE-INERT, **three mirrors moved**. The mirror diff shows the repair is stronger
than it looked: in `module6_whyml/functions` the body previously read **`pycsl_none`** — route #44's
SHARED `None` opaque — so two different unknown `getattr`s with a `None` default were THE SAME TERM
and therefore provably EQUAL. They are distinct per site now.

Witnesses 1691 (XFAIL carrier), 1692 (PASS control). `bin/check-getattr-erasure.py`'s ABSENT and
UNKNOWN ratchets each rose by exactly one — the two witnesses, one per bucket — with the reason
written into the gate; DECLARED stays hard zero.

## Lesson

>>> WHEN A GATE HOLDS A BUCKET AT A RATCHET "BECAUSE IT IS NOT SOUND BY ARGUMENT EITHER", THE
>>> ARGUMENT IT IS NOT SOUND BY IS WRITTEN DOWN RIGHT THERE. Read it as a claim and probe it. This
>>> one was one word too narrow, and the word was "contract".
>>>
>>> AND: AN EMITTER THAT ALREADY COMPUTES A CLASSIFICATION IN ORDER TO *REPORT* IT CAN USE IT TO
>>> *ANSWER*. The UNKNOWN/ABSENT split existed, was correct, and was spent entirely on a census line.
