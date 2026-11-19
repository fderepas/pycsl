"""Test 1200 — ROUTE #81: aliasing a list that is later APPENDED to is REFUSED.

Route #59 closed the dict case and, to localise itself, stated — as a section heading —
"WHAT MAKES THIS SHARP: THE LIST CARRIER IS CORRECT", concluding "lists alias correctly (a
shared ref)". **That measurement is real and still true, but it covers only an ELEMENT
STORE.** Measured, before this refusal:

    a: List[int] = [1, 2]
    b: List[int] = a
    b.append(3)
    return len(a)
    #@ ensures \\result == 2          <-- FALSE OF THE PROGRAM (Python returns 3)

    [+] Verification SUCCESS! All contracts formally proven.

BOTH DIRECTIONS MEASURED: the TRUE twin (`\\result == 3`) was REFUSED. The ELEMENT read is a
second and sharper carrier (`a[1]` proved 1 where Python gives 9 — the alias is wrong about
the CONTENTS, not just the length), and the REVERSE direction (`a.append(3)` then `len(b)`)
proves identically, which is why the guard checks BOTH names.

THE MECHANISM: a list that is `append`ed to is SEQ-PROMOTED to a growable `ref (seq int)`,
and the alias COPIES that value together with its own length. Why3 says so on the exploit
run itself — `unused variable b_len`, the alias's own length variable, unused because
`len(a)` reads a's. That is the whole route in one warning, exactly as `unused variable xs`
was for route #77.

WHY ONLY `append`: every other length-changing list mutator on an aliased list is ALREADY a
pipeline refusal (`insert`, `clear`, `pop`, `remove`, `extend` — each measured). `append` is
the operation the array+length model was BUILT to support, and seq-promotion is TRIGGERED by
`append`, so the fence and the leak have the same cause.

WHAT BOUNDS THE REFUSAL: an element STORE through an alias IS faithful and keeps working —
that is corpus 1131, route #59's own control, which does `b = a; b[0] = 2` and still proves.
Blast radius censused: 1131 is the ONLY list-local-to-list-local alias in the repository and
it contains no `append`, so it is not hit.

THE LESSON WORTH MORE THAN THE BUG: **a closed route's "this carrier is correct" control is
evidence about the OPERATION it ran, not about the TYPE.** A control is a measurement, not a
theorem, and its scope is exactly the program that was run.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a
    b.append(3)
    return len(a)
