"""Test 0997 — a GENERATOR EXPRESSION bound to a local, then used as a guard, is REFUSED.
ROUTE #25, the first of three shapes of one defect (see also 0998 set literal, 0999 tuple
literal).

A generator object is ALWAYS truthy in Python. `expressions.py` lowered a `GenExp` to the
literal `0`, and `0` is never truthy, so the model took the branch the program cannot.
Measured, before the refusal, on exactly this body with `#@ ensures \result == 0`:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 7.

The site's own comment argued "everywhere else GenExp stays exactly as inert as it was".
INERT IS NOT SOUND: an erasure to a LITERAL is one `if` away from a false proof, because
the model gets to DECIDE A BRANCH on a value it invented. An erasure to an OPAQUE value is
not, and that difference is the whole finding.

WHAT IS NOT AFFECTED, and it is what localises the defect: READING such a local is fine —
every projection off it is abstract. `if 1 in s`, `if x[0] == 1` and a field read off an
erased local all FAIL correctly. Six sibling shapes probed in the same sweep — dict
literal, list literal, str literal, list comprehension, `zip`, `enumerate`, `range`,
`.keys()` — are all sound. Only the guard on the three erased kinds is not.

REFUSED rather than made opaque. An opaque binding is better behaviour, but it moves every
one of the 261 non-empty set literals and every tuple binding in the tree, and the
unsoundness lives entirely at the guard. CENSUS
(`scratchpad/w9/census_erased_guard.py`, an AST scan of both corpora, `src/pycsl`,
`src/self-annotate/src`, `src/pycsl_lib` and `tests/`): ZERO locals of these kinds are used
as a boolean anywhere in the tree, so the refusal is byte-inert by measurement — both
corpora emit identically and every mirror emission is byte-identical, so no re-proof is
owed.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires True
#@ ensures \result == 0
def f() -> int:
    g = (i for i in [1, 2, 3])
    if g:
        return 7
    return 0


if __name__ == "__main__":
    print(f())
