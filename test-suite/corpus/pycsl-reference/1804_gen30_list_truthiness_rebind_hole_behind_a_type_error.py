r"""Test 1804 — TRIPWIRE (expected FAIL): route #31's archetype, currently unreachable
only because the emitted module does not TYPE-CHECK.

THE CONTRACT BELOW IS FALSE OF CPython. `f(0)` binds `a = []`, which is FALSY, so CPython
returns 2. The claim says 1.

WHY IT DOES NOT PROVE TODAY, and it is not the reason you would hope. The emission is

    let a = (Array.make 1024 0) in
    if (n > 0) then begin a_len := 0; a[!a_len] <- 1; ... end;
    if (Array.length a <> 0) then ...

and two separate things are wrong:

  1. `a_len` is WRITTEN AND NEVER DECLARED. The `let <tgt>_len = ref …` is emitted only for
     `.append` targets, and a list-literal REBINDING is not one. Why3 answers "unbound
     function or predicate symbol 'a_len'" and L3-tc refuses the module. THAT is what makes
     this file fail.
  2. The truthiness test is `Array.length a <> 0` over a 1024-cell shadow, i.e. ALWAYS
     TRUE — route #31's archetype verbatim, the emitter answering "a list local is truthy
     because the array is always allocated". `PYCSL-R31-UNMODELLED-LIST-TRUTHINESS` exists
     for exactly this residue and DOES NOT FIRE on this shape.

So the false claim is blocked by an unrelated type error, not by the refusal. This file is
the tripwire for the day someone declares the counter — a tidy-up that looks harmless. If
that happens this file starts PROVING, becomes an XPASS, and the suite says so loudly
instead of the hole opening in silence.

WHAT IS FAITHFUL HERE, measured, so the fix is not over-scoped: with NO rebinding,
`a: list = []` proves `\result == 2` and refuses `\result == 1`; rebinding from a
NON-literal (`a = b`) is refused with a message that explains the representation. It is
the literal-rebinding spelling alone that is unguarded.

GEN #31 — THE COUNTER IS DECLARED, AND THIS FILE STILL FAILS, WHICH IS THE POINT. The
tripwire did its job twice over.

  * The counter is now emitted for a literal-rebound list local (`let a_len = ref 0 in`,
    initialised to the FIRST literal's length), so the module type-checks.
  * Truthiness reads `!a_len <> 0` instead of `Array.length a <> 0`. With `n == 0` the list
    is empty, the test is false, and `\result == 1` is UNPROVABLE — for the right reason
    this time. The TRUE twin is corpus **1822** and it PROVES.
  * `len()` reads the counter too, and that half was PROVED NECESSARY BY A FALSE CLAIM
    rather than reasoned into existence: with the counter declared and truthiness fixed but
    `len` left alone, `a: list = [7,8,9]; if n > 0: a = [1,2]; return len(a)` PROVED
    `\result == 3` where CPython answers 2. Corpus 1823/1824/1825 pin both paths and the
    false twin. DECLARING THE COUNTER ALONE REALLY DOES OPEN A HOLE — just not the one this
    file was watching.

AND A SECOND TRIPWIRE FIRED DURING THE REPAIR, which is why the gate is narrower than
"assigned a literal twice". The first draft qualified any such name, and corpus **1013**
(route #32's negative witness — `a` bound in BOTH ARMS of an if/else and never at top
level) went XPASS: the counter had no correct initial value and a contract that is FALSE of
the program started proving. A name now qualifies only when its FIRST literal binding IN
SOURCE ORDER is UNCONDITIONAL, at depth 0 of the function body. 1013 and 1014 fall outside
and are unchanged.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 1
def f(n: int) -> int:
    a: list = []
    if n > 0:
        a = [1, 2]
    if a:
        return 1
    return 2
