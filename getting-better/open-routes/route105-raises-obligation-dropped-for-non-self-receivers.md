# ROUTE #105 — A `no_exception` OBLIGATION IS DROPPED FOR EVERY RECEIVER EXCEPT `self.`

**Severity 1. CLOSED gen #18 (2026-09-13). Found by the `continue`-census (candidate 1),
which is now SEVEN-FOR-SEVEN.**

## THE ONE-LINE STATEMENT

`_module_func_raises` is keyed on the **IR function name** (a method is `<cls>__<m>`).
Route #100's `_r100n` (`module6_whyml/expressions.py:7281`) flattened `self.<m>` into that
space and handed every OTHER receiver its **source spelling** — the literal strings `"c.f"`
and `"_h.f"`, which are never keys of that registry. The lookup missed,
`_wrap_call_with_callee_raises_assert` returned `inner` untouched, and a caller's
`#@ no_exception E` was discharged by nobody.

## BOTH DIRECTIONS MEASURED — AND READ OFF THE EMITTED WhyML

| receiver | emitted call site | verdict |
|---|---|---|
| free function `f(k)` | `assert { not ((k < 0)) }; try (f k) with ValueError -> absurd` | FAILS |
| `self.f(k)` (route #100) | same shape | FAILS |
| `c.f(k)` (record var) | **`(c_f_1 k)`** — no assert, no try | **PROVES** |
| `_h.f(k)` (module global) | inlined — see route #106 | **PROVES** |

CPython: `caller(-1)` **RAISES ValueError**. The caller's only claim was
`#@ no_exception ValueError`, so `Verification SUCCESS! All contracts formally proven.` IS
the false statement.

## THE REPAIR

Thread the receiver resolution **already computed** 600 lines above, in
`_resolve_dotted_signature` (`expressions.py:6678`, from `_current_record_var_classes` /
`_module_global_classes` — the same two maps), into `_r100n`. FAIL-CLOSED: an unresolvable
receiver falls back to the source spelling exactly as before, so every call site route #100
already handled emits unchanged.

**CAPABILITY PRESERVED AND TESTED** (witness 1295): a caller that adds `#@ requires k >= 0`
discharges the restored assert and still proves. The obligation exists and is dischargeable —
a fence, not a wall.

## THE LESSON

>>> **A REPAIR KEYED ON A RECEIVER SPELLING COVERS THE RECEIVERS ITS AUTHOR HAD IN VIEW.**
>>> The guard was written about the SYNTAX of the call site; the obligation is about WHICH
>>> CALLEE IS RESOLVED. This is routes #101/#102/#104 in a different clause, and the
>>> resolution it needed was already sitting in the same file.

## AND THE FIRST PROBE WAS VACUOUS — LOGGED VACUOUS, NOT FAIL-CLOSED

Written with a FIELDLESS `Helper`, it FAILED at baseline, which looked like confirmation the
route was closed. Reading WHICH goal failed: a fieldless class is modelled `type helper = int`,
so the callee's `ensures \result >= 0` vanished along with the wrap, and the failure was an
unrelated unprovable postcondition. The wrap's absence was already visible in the emission.

## REOPENING / CLOSING CONDITION

CLOSED: witnesses 1294 (FAIL) + 1295 (PASS), 1294 PROVED at 5795cfef. REOPENS if a new
receiver form is added (a subscripted receiver `objs[i].m()`, a chained `a.b.m()`) without
resolving it into the IR name space — note both of those are UNPROBED at the close of gen #18.
