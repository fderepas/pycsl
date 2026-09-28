r"""Test 1914 — gen #33 (expected FAIL): ROUTE #228, the string-fold collision.

FALSE OF THE PROGRAM: `struct.pack('<bb6x', 1, 2)` is 8 bytes and
`struct.pack('<xxxxxxxxhxLxxxxxxxx', 1, 2)` is 23, so `len(a) == len(b)` is False and
this function returns 0 in CPython. At the parent commit it PROVED `\result == 1`,
`Valid (0.00s, 156 steps)`.

A PROBABILISTIC PREMISE IN A DEDUCTIVE TCB. `module6_whyml/identifiers.py::stable_hash`
folds a string PyCSL cannot model faithfully to `int(sha256(s)[:8],16) % 2147483647`, and
its docstring justified that with "preserving the distinguishing property (distinct
strings -> distinct ints **w.h.p.**)". That was the whole of the justification. Truncated
to 32 bits, a birthday collision costs ~2^16 trials — under a second — and two
THREE-character strings collide (`'f9r'`/`'6xb'` -> 122473869).

WHY IT IS EXPLOITABLE HERE AND NOWHERE ELSE. The collapse only CONCLUDES a falsehood
where the receiving Why3 symbol is PURE. Every bare `val` destination is
non-deterministic, so two equal arguments relate nothing — measured VACUOUS, the witness
AND its non-colliding control both failed to prove. Dict keys, list literals and set
literals are faithful native strings and never fold. `struct.{pack,unpack}` lower to
`val function struct_{pack,unpack}_<slot_id> (fmt: int)`, pure on purpose — "a logical
symbol the round-trip axiom can name" — and `slot_id` encodes "only the slot types (not
prefix, not pad)", so unbounded pad/prefix variants share ONE symbol and differ only in
the folded `fmt`. Both formats below emit `(struct_pack_i2 1322019588 1 2)`: ONE TERM.

THE FIX IS NOT A WIDER HASH — that is route #227's lesson in a new costume, where an
opaque answer to a wrong value moved the falsehood from the VALUE to the TYPE. The
premise is INJECTIVITY OF THE FOLD ON THE STRINGS ONE EMISSION FOLDS, which is decidable,
so `stable_hash` now records every fold and REFUSES a collision.

Companion control: 1915, the same program with a non-colliding second format, which must
still be ACCEPTED — without it a guard that refused every struct program would pass.
"""
import struct  # noqa
# pycsl-expected: FAIL


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def go() -> int:
    a = struct.pack('<bb6x', 1, 2)
    b = struct.pack('<xxxxxxxxhxLxxxxxxxx', 1, 2)
    if len(a) == len(b):
        return 1
    return 0
