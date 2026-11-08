r"""Test 1880 — gen #31 WITNESS (expected FAIL): `#@ uses` naming no lemma is refused.

`#@ uses` is ordering-only and "emits no WhyML" (annotations.md row 17), so a name that
resolves to nothing was DROPPED IN SILENCE — this exact file reported
`[+] Verification SUCCESS! All contracts formally proven.` The proof that was meant to rest
on the cited lemma then fails for a reason the user cannot connect to anything they wrote,
and the compiler held the admissible set exactly.

THIRD MEMBER OF ONE FAMILY found the same day: a NAME THE USER WROTE THAT RESOLVES TO
NOTHING AND IS DROPPED IN SILENCE. The others are `Callable[[Rekt], int]` (an unknown class
silently becomes `int`) and `#@ verify_module leafmod` (a lowercase group name, which used
to surface as a Why3 syntax error naming a synthesized module the user never wrote).

THE COUNTER-PROGRAM SHARPENED THIS RULE RATHER THAN REFUTING IT, which is why it landed
while the `#@ datatype` exhaustiveness rule of the same afternoon did not: citing an
IMPORTED lemma also verifies, and the emitted `.mlw` contains NO TRACE of that lemma — it
is not emitted, its fact is not in scope, so refusing that too is telling the truth.
Emitting an imported cited lemma is a separate, currently unused capability.

Control: 1881, the same file with the lemma actually present.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ lemma
#@ requires n >= 0
#@ ensures n + 0 == n
#@ assigns \nothing
def triv(n: int) -> None:
    pass


#@ uses no_such_lemma
#@ ensures \result == 0
#@ assigns \nothing
def go() -> int:
    return 0
