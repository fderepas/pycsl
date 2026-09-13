# ROUTE #96 — A BODYLESS `val` (`\trusted` / `\abstract`) SILENTLY DROPS AN ARRAY-REGION
# `assigns`, SO A CALLER PROVES THE ARRAY UNCHANGED ACROSS A STUB CONTRACTED TO WRITE IT

**SEVERITY 1. FOUND, REPRODUCED, CONTRADICTED BY AN EXECUTED CPYTHON RUN, BOTH ARMS MEASURED.**
Found by the `continue`-census generator that produced route #95 (a skip written for one purpose
silently narrowing a different population).

## THE MECHANISM, VISIBLE IN THE EMISSION

`module6_whyml/statements.py::_emit_frame_condition`, the `val` branch:

```python
for a in assigns_list:
    if not isinstance(a, dict) or a.get("type") not in ("Attribute", "FieldGet"):
        continue
    ...
if field_targets and not nothings:
    return [f"    writes   {{ {', '.join(field_targets)} }}"]

if self._value_semantic:
    return []
```

An `#@ assigns a[0..n]` on an ARRAY PARAMETER is an `AssignsRegion` node. It is skipped by that
`continue`, so `field_targets` is empty, control falls through, and under the default `hoare`
model the function returns `[]` — **no `writes` clause at all.** The branch's own docstring says
why that is fatal: *"A `val` … has NO body, so Why3 cannot INFER its `writes` from mutations —
they must be declared explicitly. Without them, the val is treated as pure (writes nothing)."*
It then declares exactly that for field targets, and silently does not for regions.

**THE EMITTED WhyML, verbatim:**

```
val scramble (a: array int) (n: int) : int
    requires { (n >= 0) }
    requires { ((n + 1) >= 0 && (n + 1) <= Array.length a) }
```

`a` is a mutable `array int`, there is no `writes`, and the `#@ assigns a[0..n]` has vanished
without trace. Why3 therefore treats `scramble` as not writing `a`, and every fact the caller
held about `a` survives the call.

## THE MEASUREMENTS — AND THE TWO CONTROLS THAT PIN IT EXACTLY

| driver | verdict |
|---|---|
| **N1 — ALIVENESS CONTROL: does a `\trusted` stub's array `ensures` reach the caller at all?** (`ensures a[0] == 9`, caller claims `\result == 9`) | **PROVES** — the channel is alive |
| **N2 — EXPLOIT: `\trusted` + `assigns a[0..n]`; caller `requires a[0] == 7`, `ensures \result == 7`** | **PROVES** |
| **N4 — the `\abstract` arm of the same disjunction, measured separately** | **PROVES** |
| **N3 — CONTROL: the IDENTICAL contract with a REAL BODY** | **FAILS** |
| **N5 — CONTROL: `\trusted` + `assigns self.f` (a FIELD, not a region)** | **FAILS** |
| **CPython, the stub's body doing exactly what its `assigns` says (`a[0] = 0`)** | **`driver([7,7,7]) == 0`** |

`0 == 7` is FALSE. A proved postcondition contradicted by an executed run.

**N3 AND N5 ARE WHAT MAKE THIS PRECISE.** N3 says the region frame IS enforced when the function
has a verified body. N5 says the frame IS declared when a bodyless stub assigns a FIELD. So this
is not "PyCSL ignores `assigns`" and not "trusted stubs lose their frame" — it is exactly and
only **region-assigns on a bodyless `val`**, the one cell of that 2x2 nobody wrote a test for.

## WHY THIS IS WORSE THAN AN ORDINARY FRAME BUG

`\trusted` is the DECLARED TCB boundary: the reviewer's whole job is to read the stub's contract
and certify that the real implementation satisfies it. **The `assigns` clause is part of what
they certify, and it is the part the emitter throws away.** A reviewer who approves
`assigns a[0..n]` has approved a promise the emitter never transmits — so the trust boundary is
honoured in the review and voided in the proof, which is the one failure mode a declared TCB is
supposed to make impossible.

>>> **AN OBLIGATION THE EMITTER DROPS IS INDISTINGUISHABLE FROM ONE THAT WAS DISCHARGED** —
>>> route #93's lesson, now on the FRAME rather than the termination VC. And the drop is spelled
>>> as a `continue` in a loop whose purpose is to *collect* one kind of target, which is route
>>> #95's shape exactly: **a skip written for the building silently narrowed the checking.**

## STATUS

**OPEN.** Found and fully reproduced by gen #14 at the end of its window; the repair was NOT
attempted because its blast radius (every `\trusted`/`\abstract`/imported function carrying an
array-region `assigns`, including `src/pycsl_lib/` stubs) could not be censused and gated inside
the remaining time, and a half-gated frame change is worse than an honest open route.

## THE REPAIR, SCOPED

In the `val` branch of `_emit_frame_condition`, an `AssignsRegion` whose base is an array
parameter must contribute that parameter to the `writes` set — `writes { a }`. Over-approximating
the region to the whole array is SOUND (more havoc = strictly less caller knowledge) and is the
same over-approximation Why3 would infer from a body that writes one cell.

**BUDGET FOR THE HONEST COST:** this makes callers of such stubs lose facts they currently keep,
so some corpus files that verify today will legitimately FAIL, and the byte-diff will show real
MOVED entries. **That is the cost of transmitting a frame that was being dropped, and it must be
worked, not hidden** — a file that breaks is a file that was relying on the hole. Census the
population FIRST (`\trusted`/`\abstract`/imported × `AssignsRegion`), predict the MOVED set, and
do not re-baseline anything to keep a gate green.
