# ROUTE #106 — INLINING DELETES THE CALL, AND WITH IT THE OBLIGATION

**Severity 1. CLOSED gen #18 (2026-09-13). Found because it SURVIVED route #105's repair.**

## THE ONE-LINE STATEMENT

A method call on a **module-global instance** is inlined by `frontend/ir_inline.py`, which
runs on the IR **before** Module 6. The callee body is spliced in, so there is no call left
for `_wrap_call_with_callee_raises_assert` to wrap — and the callee's raise becomes the
CALLER's own emitted `raises { ValueError }` while the caller declares
`#@ no_exception ValueError`.

## THE EMITTED WhyML STATES THE CONTRADICTION OUT LOUD

```
  let caller (k: int) : int
    raises { ValueError }            <- Why3 is TOLD the function raises
  =
    let _inl_res__inl1 = ref 0 in
    if (k < 0) then begin raise ValueError end; ...
```

…and PyCSL reported `Verification SUCCESS! All contracts formally proven.` **Nothing compared
the emitted signature with the source directive.** CPython `caller(-1)` RAISES.

**IT WAS INLINED EVEN WHEN THE CALLEE WAS `\trusted`:** `val helper__f` was emitted and never
called, so the trust boundary was spliced straight through. That is worth its own attention —
a `\trusted` stub whose body is inlined is not an abstraction at all.

## WHY IT IS ITS OWN ROUTE

It survived #105's repair. #105 fixes the key handed to a wrap that lives at a CALL SITE;
#106 is about there being no call site. Same clause, different stage, different fix.

>>> **A TRANSFORMATION THAT REMOVES A SYNTACTIC FORM REMOVES EVERY OBLIGATION KEYED ON THAT
>>> FORM.** Inlining is semantics-preserving for the VALUE and silently not for the CHECK,
>>> because the check was attached to the CALL NODE rather than to the CALLEE.

## THE REPAIR PRESERVES THE CAPABILITY INSTEAD OF REFUSING

Such a callee is treated as `#@ no_inline` **for this caller only**, so the call survives to
Module 6 and lands on the existing, already-gated wrap. Nothing that used to be accepted is
rejected — the obligation simply becomes visible, which is what the user asked for by writing
`no_exception`. After the repair all FIVE receiver spellings agree and emit the same
`assert { not ((k < 0)) }; try (_h_f_1 k) with ValueError -> absurd end`.

**CENSUS THAT SIZED IT:** across the **71** files declaring `#@ no_exception`, **NOT ONE**
also declares a module-global instance — so the change is byte-inert on the corpus today. It
is a fence for the shape, not a migration, and 1296 negative-tests it because a guard whose
population is empty looks exactly like a guard that passed.

## A NEAR-MISS RECORDED SO IT IS NOT RE-PROBED AS A ROUTE

A function that ITSELF does `raise ValueError` while declaring `#@ no_exception ValueError`
also reports SUCCESS. That is **DOCUMENTED semantics**, not a route: `test-suite/annotations.md`
row 13 and §2.1.13 define `no_exception` as turning **IMPLICIT** Python exceptions into
obligations. Logged `OUT-OF-SCOPE` in `probes.tsv`. Reading the spec is part of the probe.

## REOPENING / CLOSING CONDITION

CLOSED: witnesses 1296 (FAIL) + 1297 (PASS), 1296 PROVED at 5795cfef. REOPENS if any new
IR-level rewrite (a further inliner, a desugaring, a specialiser) removes a call node that a
Module 6 consumer keys an obligation on. **The general question this route raises and does NOT
answer: which OTHER obligations are keyed on a call node that inlining deletes?** The frame
(`writes`), the callee's `requires`, and the UB gates are all candidates and are UNPROBED.
