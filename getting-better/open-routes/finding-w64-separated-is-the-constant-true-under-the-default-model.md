# FINDING w64 — `\separated` is emitted as the CONSTANT `true` under the default memory
# model, so it is a VACUOUS contract: `\separated(a, 3, a, 3)` PROVES, and an
# anti-aliasing PRECONDITION is discharged by a call that passes the same array twice

**CLASSIFIED HONESTLY: TCB-ACCOUNTING / VACUOUS-CONTRACT FINDING, *NOT* A ROUTE.**
A provable falsehood exists in isolation, but it does **not** escalate to a falsehood about
the Python program, because the only observable consequence of aliasing — mutation — is
independently blocked by Why3's region typing. **I set out to close this as a severity-1
route and the measurement refused it. That refusal is the finding.**

## THE MECHANISM

`module6_whyml/expressions.py::_handle_separated_expr` opens with

```python
if self._value_semantic:
    return "true"
```

and `_value_semantic = memory_model in ("hoare", "concurrent")` — **`hoare` is the DEFAULT**.
So under the default model every `\separated(...)`, whatever its arguments, lowers to the
constant `true`. `pycsl.py:557-560` records the justification:

> *"the one remaining `return "true"` (`_handle_separated_expr`, under the VALUE model) is
> sound, because Why3's region typing rejects an aliased array application outright ("This
> application creates an illegal alias" — probed), so two array parameters really are always
> separated there."*

## WHAT I MEASURED

| driver | verdict |
|---|---|
| `ensures \separated(a, 3, a, 3)` — a region overlapping ITSELF — under `hoare` (default) | **PROVES** |
| the same file under `--memory-model typed` / `store` | **FAILS** (the real predicate is emitted) |
| `requires \separated(p,3,q,3)`, `assigns \nothing`, called as `needs_disjoint(a, a)` | **VERIFIES** |
| **control**: same aliased call, precondition replaced by the false `\length(p) >= 9999` | **REFUSED** — so call-site preconditions demonstrably ARE checked in this exact shape |
| `requires \separated(p,3,q,3)`, **`assigns p`**, `p[0] = 99`, called as `touch(a, a)` | **REJECTED — "This application creates an illegal alias"** |
| `requires \separated(self.buf, 3, p, 3)` (a FIELD base) | **PARSE ERROR** — the grammar takes only NAME bases |

So two real defects and one real defender:
1. **A false postcondition is provable.** `\separated(a, 3, a, 3)` is false by definition and
   proves under the default model. The same source refuses under the heap models, so the two
   models DISAGREE on a contract the user can write — and the default one is the wrong side.
2. **An anti-aliasing precondition is vacuous.** It is discharged by the maximally-aliased
   call. A user who writes `requires \separated(p, n, q, n)` believing they have excluded
   overlap has excluded nothing.
3. **But it does not escalate.** Aliasing is only *observable* through mutation, and the
   moment the callee's `assigns` names an aliased array parameter, Why3's region typing
   rejects the application. **The census comment's conclusion is correct; its stated reason is
   not.** It says the guarantee comes from "two array parameters really are always separated",
   which is false — I bound both parameters to one array and the application was accepted. The
   guarantee actually comes from *mutation being the only observable, and mutation being what
   region typing refuses*. **A CORRECT CONCLUSION RESTING ON A FALSE PREMISE IS A LATENT
   ROUTE, BECAUSE THE PREMISE IS WHAT THE NEXT PERSON WILL REASON FROM.**

## HOW IT WAS FOUND

The **deferral generator** that route #92 produced: a census of every comment in `src/pycsl/`
claiming a case is "handled/rejected/checked elsewhere", checking each named guard's actual
matching rule against the deferred case. This entry's deferral was to "Why3's region typing",
and it is the first one I could test directly.

## REOPENING CONDITIONS — both narrow, both owned by OTHER subsystems

1. **If the value model ever permits an aliased application whose callee MUTATES an aliased
   parameter**, the vacuous `true` becomes a live severity-1 route immediately: the measured
   `touch(a, a)` driver would then prove `q[0] == 7` after `p[0] = 99` with `p` and `q` the
   same Python list. The defender is Why3's REGION TYPING, not PyCSL.
2. **If `\separated` ever accepts a field or global base** (today a parse error), region typing
   has no reason to relate `self.buf` to a parameter bound to it, and condition 1's protection
   does not obviously apply. This is the completeness gain most likely to be made by someone
   who has never read this file.

Both are route #89's shape: a fence owned by a different subsystem, un-armable by a
completeness gain nobody thinks of as touching this contract.

## THE HARDENING WORTH DOING ANYWAY (scoped, not yet landed)

Independently of exploitability, `ensures \separated(a, 3, a, 3)` proving is a **provable false
postcondition**, and the campaign's standard is that a contract must not be satisfiable by a
witness of its own negation. The minimal faithful emission under value semantics is: `true`
when the two bases are syntactically DIFFERENT names, and `(l1 <= 0 || l2 <= 0)` when they are
the SAME name — two ranges in one array are separated only if one of them is empty. That keeps
the distinct-parameter capability intact (so it is not a narrowing-to-nothing, the corpus-1057
mistake) and is negative-testable, since the observable is the refusal and does not depend on
exploitability.
