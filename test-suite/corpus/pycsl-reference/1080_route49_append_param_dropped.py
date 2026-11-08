"""Test 1080 — ROUTE #49 negative witness (a): `a.append(x)` on a list PARAMETER was
INVISIBLE to the caller.

FALSE OF THE PROGRAM: `f([])` returns 1 in Python, because `g` appends to the caller's list.

The emission said why in four lines: `g` lowered its list param to a LOCAL SNAPSHOT
(`let a = ref (snapshot a)`), appended to the COPY, and carried NO `writes` clause — so
Why3 knew `a` was unchanged across the call and the caller proved `Array.length a = 0`
afterwards. The mutation was not un-modelled, it was modelled as ABSENT. At the parent
commit b7898d0e `\\result == 0` PROVED.

`append` was the ODD ONE OUT of its own family, which is what makes the refusal the right
answer rather than a fifth special case: `pop`, `insert`, `clear` and `extend` on a list
param were ALREADY refused; an element write `a[0] = 99` and a dict write `d[1] = 5`
through a parameter ARE caller-visible and fail closed; and the SAME-FUNCTION
`a = []; a.append(1)` is modelled correctly. Only the cross-call `append` was dropped.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires True
#@ ensures True
#@ assigns a
def g(a: list) -> None:
    a.append(1)


#@ requires \length(a) == 0
#@ ensures \result == 0
#@ assigns a
def f(a: list) -> int:
    g(a)
    return len(a)
