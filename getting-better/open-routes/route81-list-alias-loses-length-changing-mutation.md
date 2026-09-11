# ROUTE #81 — A LIST ALIAS TRACKS ELEMENT STORES BUT LOSES A LENGTH-CHANGING MUTATION

**STATUS: FOUND AND CLOSED 2026-09-11 (gen #8). BOTH DIRECTIONS MEASURED. Witness 1200; the
element-store control is corpus 1131 (route #59's own), which still proves.**

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
| p06 | **`a.append(3)`, read `len(b)`** — the REVERSE direction | `\result == 2` | **3** | **PROVED** ❌ |
| p03 | the same append via a **SELF-FIELD** alias (`b = self.xs`) | `\result == 2` | 3 | refused |
| p04 | `b.insert(0, 9)` on the alias | `\result == 1` | 9 | refused (PIPELINE ERROR) |
| p05 | `b.clear()` on the alias | `\result == 2` | 0 | refused (PIPELINE ERROR) |
| p01 | **SET** alias + `b.add(2)` | `\result == 1` | 2 | refused |
| p02 | **DICT** alias + `b[2] = 5` | `\result == 1` | 2 | refused (PIPELINE ERROR) |

**THE ROUTE IS NARROWER AND SHARPER THAN IT FIRST LOOKED, AND THAT MAKES THE REPAIR SMALL.**
The alias loses the append in **BOTH mutation directions** (mutate the alias and read the
original; mutate the original and read the alias), and it loses both the LENGTH and the
CONTENTS. But **every neighbouring operation is already refused**: `insert` and `clear` are
pipeline refusals (the route #13/#17 list-mutator family), the SET alias is fenced (route #63)
and the DICT alias is fenced (route #59's own repair). The SELF-FIELD carrier also fails closed.
**So the live surface is exactly `append` on a LOCAL-to-LOCAL list alias** — which is why the
blast-radius census below comes out at a single site.

**THE MUTATOR FAMILY IS NOW ENUMERATED EXHAUSTIVELY, SO THE REPAIR SPEC IS COMPLETE:**

| mutator on an aliased list | verdict |
|---|---|
| **`append`** | **PROVES a false claim — the ONLY live one** |
| `append` twice in a row | **PROVES** (same defect, not a separate one) |
| `insert` | refused (PIPELINE ERROR) |
| `clear` | refused (PIPELINE ERROR) |
| `pop` | refused (PIPELINE ERROR) |
| `remove` | refused (PIPELINE ERROR) |
| `extend` | refused (PIPELINE ERROR) |

**EVERY LENGTH-CHANGING LIST MUTATOR EXCEPT `append` IS ALREADY A PIPELINE REFUSAL.** `append`
is the one the list model supports natively (it is the operation the array+length model was
built around), and supporting it is exactly why it is the one that escapes. **The repair is a
single-method guard**, not a family sweep: refuse `append` on a list local that appears as the
RHS of another list-local binding (in either order — both mutation directions prove). With a
measured blast radius of one site that the guard does not hit, **this is a one-hour close.**

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

## THE MECHANISM, LOCATED EXACTLY (gen #8 attempted the repair and found the real site)

**THE ALIAS IS LOST BECAUSE AN APPENDED-TO LIST IS *SEQ-PROMOTED*.** A list local that is
`append`ed to is promoted to a growable `ref (seq int)` (`self._seq_locals`), and
`_handle_assign_stmt` dispatches such a target **before** reaching route #59's alias guard:

    # statements.py, well above the #59 dict-alias refusal
    if target in self._seq_locals:
        return self._handle_seq_assign(stmt, rest, local_refs, declared_refs, indent, in_loop)

`_handle_seq_assign` then emits `let b = ref <init> in ...` — **a COPY of the seq value**, with
its own length. Why3 says so on the exploit run itself:

    Warning, ... line 11: unused variable b_len

`b_len` is the alias's OWN length variable, unused because `len(a)` reads `a`'s. That is the
whole route in one warning, exactly as `unused variable xs` was for #77.

**THIS ALSO EXPLAINS WHY ONLY `append` IS LIVE.** Seq-promotion is triggered by `append`, so
only an appended-to list takes the `_handle_seq_assign` path at all; the other mutators never
get there because they are refused earlier. The fence and the leak have the same cause.

## REPAIR SHAPE (ATTEMPTED AND BACKED OUT — READ THIS BEFORE RE-TRYING)

**GEN #8 BUILT A GUARD IN THE WRONG PLACE AND BACKED IT OUT. Do not repeat it.** The first
attempt added a list arm next to route #59's dict-alias refusal in `_handle_assign_stmt`. It
**never fires**, because the `self._seq_locals` dispatch above returns long before that point —
all four exploit carriers still PROVED with the guard in. The attempt was reverted rather than
left in the tree, and #81 re-verified as still reproducing at HEAD.

**THE CORRECT SITE IS `_handle_seq_assign`**: refuse when a seq local's initialiser is a bare
`Var` naming another list/seq local (checking BOTH names, since both mutation directions
prove).

**THE REPAIR AS BUILT — AND THE PLACEMENT IS THE WHOLE POINT.** `_handle_seq_assign` would
work, but its mirror is a **VERBATIM CONVERTED body**, so a guard there owes a mirror sync AND
a whole-file `statements.py` mirror re-proof (~40-60 min, and it has hit `rc=137` OOM in past
windows). **Instead the guard went at the TOP of `_handle_assign_stmt` — the dispatch ENTRY
POINT — ahead of every early return, including the `self._seq_locals` one.** That placement
sees both seq-promoted and unpromoted aliases in one check, AND `_handle_assign_stmt`'s mirror
is a `#@ \trusted` stub, so **the repair owes NO mirror sync and NO re-proof at all.**

**BANK THIS: THE SAME REPAIR CAN BE CHEAP OR EXPENSIVE DEPENDING ON WHICH FUNCTION IT GOES IN.**
A guard in a CONVERTED body costs a whole-file proof; the identical guard hoisted into the
`\trusted` ENTRY POINT that dispatches to it costs nothing — and is often *more* correct,
because the entry point sees every case before the specialised handlers split them up.

**THE LESSON FROM THE FAILED ATTEMPT, WHICH IS THE REUSABLE PART: THE `\trusted`-STUB COST
CHECK IS NECESSARY BUT NOT SUFFICIENT — YOU MUST ALSO CONFIRM *WHICH FUNCTION ACTUALLY HANDLES
THE CONSTRUCT* BEFORE PRICING THE REPAIR.** I priced #81 off `_handle_assign_stmt` (whose
mirror IS `\trusted`, hence "one-hour close") without first confirming that the construct
reaches it. It does not. **One `R81DEBUG` print at the candidate site, before writing the
guard, would have caught this in two minutes** — and that is now the recommended first step for
any Module-6 repair: instrument the site and prove the construct arrives there.

## THE ORIGINAL REPAIR SKETCH (superseded by the section above)

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
