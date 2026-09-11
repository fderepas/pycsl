# ROUTE #81 — A LIST ALIAS TRACKS ELEMENT STORES BUT LOSES A LENGTH-CHANGING MUTATION

**STATUS: FOUND AND REPRODUCED 2026-09-11 (gen #8). BOTH DIRECTIONS MEASURED. OPEN.**

**CLASS: the #69 class, the serious one** — a FALSE POSTCONDITION about ordinary, TOTAL Python.
No `no_exception`, no opt-in.

## WHY THIS ONE MATTERS OUT OF PROPORTION TO ITS SIZE

**IT REFUTES A REASSURING SENTENCE IN A CLOSED ROUTE'S OWN FILE.** Route #59
(`route59-dict-assignment-is-a-value-copy.md`) closed the dict case, and to localise it, it
states — as a section heading —

> ## WHAT MAKES THIS SHARP: THE LIST CARRIER IS CORRECT
> The identical program over a `List[int]` is FAITHFUL — measured in the same session:
> `a: List[int] = [1];  b: List[int] = a;  b[0] = 2;  return a[0]`
> So this is not "reference semantics are unmodelled". Lists alias correctly (a shared ref).

**That measurement is real and it is still true — but it covers only an ELEMENT STORE.** The
list model is an `array int` plus a separate length. A store writes through the shared
reference and is seen. **A LENGTH-CHANGING mutation is not**, because the length is not the
thing the alias shares. One operation over, the "lists alias correctly" conclusion fails.

**THE LESSON, AND IT IS THE MOST TRANSFERABLE THING IN THIS FILE: A CLOSED ROUTE'S
"THIS CARRIER IS CORRECT" CONTROL IS EVIDENCE ABOUT THE OPERATION IT RAN, NOT ABOUT THE TYPE.**
The campaign already banks "probe every carrier of a closed route". This adds: **probe every
OPERATION on the carrier that was declared safe.** A control is a measurement, not a theorem,
and its scope is exactly the program that was run.

## THE EXPLOIT

```python
from typing import List
#@ ensures \result == 2
def f() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a        # b aliases a
    b.append(3)             # length-changing mutation through the alias
    return len(a)
```

    CPython:  3
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## BOTH DIRECTIONS, MEASURED, AND THE CARRIER CENSUS

| driver | shape | claim | CPython | PyCSL |
|--------|-------|-------|---------|-------|
| n01 | `b.append(3)`, read `len(a)` | `\result == 2` | **3** | **PROVED** ❌ |
| n01 twin | the TRUE claim | `\result == 3` | 3 | refused (Unknown) |
| n01_elem | `b.append(9)`, read the **ELEMENT** `a[1]` | `\result == 1` | **9** | **PROVED** ❌ |
| n01_param | append through a **CALL** `g(a)` | `\result == 2` | 3 | refused (PIPELINE ERROR) |
| **#59's control** | `b[0] = 2`, read `a[0]` (ELEMENT STORE) | — | — | **FAITHFUL** ✅ |

Two carriers prove a false claim, and the true twin of the headline one is refused — so it is a
route, not a gap. **The element READ carrier (n01_elem) is the sharper of the two**: the alias
is wrong not only about `len` but about the *contents*, because the appended element never
lands in the array the alias reads.

The CALL carrier fails closed with a pipeline refusal, which is consistent with routes
#49/#62's append-through-a-parameter work having already fenced that boundary.

## RELATION TO THE EXISTING LEDGER

* **#59** (dict assignment is a value copy) — CLOSED; this is the list-side complement it
  explicitly ruled out.
* **#49** (`append` through a parameter dropped) — the CALL carrier; refused here.
* **#63** ("no aliasing is possible" is true for lists and false for sets) — the same
  list/set/dict asymmetry seen from a third angle. #63 says a list *cannot* alias two
  parameters; #81 says a list *can* alias two locals and the model then loses `append`.

## REPAIR SHAPE (not yet built)

The honest options, in the campaign's usual order of preference:
1. **Refuse** a length-changing mutation (`append`, and the same family `insert`/`pop`/
   `remove`/`clear`, already refused elsewhere) on a list local that has been **aliased** —
   i.e. that appears as the RHS of another list-typed local binding. Census the corpus for
   `b = a` between two `List[...]` locals first; that is the blast radius.
2. Make the length part of what the alias shares (a `ref` to a record of array+length), which
   is the value-model capability route #13's list-mutator family has wanted for several
   generations. Larger, and it would re-price a great deal of the corpus.

Option 1 is the right first move, and **THE CENSUS IS DONE AND THE BLAST RADIUS IS ONE SITE.**

    list-local := list-local aliasing sites across test-suite/corpus, src/self-annotate,
    src/pycsl, src/pycsl_lib  ->  1
      test-suite/corpus/pycsl-reference/1131_route59_list_control_faithful.py :: f :: `b = a`

**THE ONLY `b = a` BETWEEN TWO LIST LOCALS IN THE ENTIRE REPOSITORY IS ROUTE #59's OWN CONTROL
WITNESS** — the file that encodes the very sentence this route refutes. And it is *not* hit by
the repair: 1131 does an ELEMENT STORE (`b[0] = 2`), which stays faithful; only a
length-changing mutation on an aliased list would be refused. **So a guard keyed on
`append`/`insert`/`pop`/`remove`/`clear` after an alias binding has a measured blast radius of
ZERO and leaves 1131 green.**

(I checked the #79 precedent before assuming — #79's obvious refusal was refuted by a 70%
census, so this census was run rather than guessed. It happens to come out the other way.)

## WITNESSES

`scratchpad/w58/n/n01_list_alias_append.py`, `n01_truetwin.py`, `n01_elem_carrier.py`,
`n01_param_carrier.py`, `n02_list_alias_store.py` (the #59 control, re-measured: refused/Timeout
in this spelling).
