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

**CLOSED AND GATED 2026-09-13 (gen #15), FAIL-CLOSED, AND THE DEFERRAL'S OWN PREMISE WAS
REFUTED BY MEASUREMENT.** Gen #14 left this open because the blast radius "could not be
censused and gated inside the remaining time". **The blast radius is EMPTY.**

The census was run by instrumenting the EXACT branch the repair touches (`_emit_frame_condition`,
val arm, `AssignsRegion` non-empty) and sweeping every tree — after negative- AND positive-testing
the probe itself, because a census whose population is empty looks exactly like a census that
passed:

| tree | files swept | val x region hits |
|---|---|---|
| `test-suite/corpus/pycsl-reference` | 1193 | **0** |
| `test-suite/corpus/python-reference` | 2217 | **0** |
| `src/pycsl_lib` (`--import-path src/pycsl_lib`) | 104 | **0** |
| `src/self-annotate/src` (`--import-path src/pycsl`) | 53 | **0** |
| *planted positive control, same harness* | 1 | **1 HIT** |

A textual pre-census agrees and explains it: 48 in-tree functions carry a region `assigns`, **not
one** is `\trusted`/`\abstract`, and the only three living in importable modules
(`pycsl_lib/strct::pack_into` x2, `pycsl_lib/rng::shuffle_len`) have **no in-tree importer**.

>>> **THAT EMPTINESS IS NOT A REASON THE BUG WAS HARMLESS — IT IS THE REASON IT SURVIVED.** The
>>> cell of the 2x2 nobody in-tree ever writes is exactly the cell no test ever covered, and the
>>> emitter is wrong precisely there. A population of zero made the repair CHEAP; it never made
>>> the route small, because `\trusted` is a boundary offered to USERS, whose programs are not
>>> in this tree.

The generalisable lesson: **a deferral justified by an un-measured blast radius should be
converted into a measurement before it is inherited as a cost.** Gen #14's estimate was the only
thing expensive about this route.

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

## THE REPAIR AS LANDED, AND WHY THE OVER-APPROXIMATION IS SOUND RATHER THAN MERELY STRICT

`_emit_function` records the `array`-typed parameters of the signature it is emitting by parsing
**`args_str` itself** (`_current_array_param_names`) — not by re-deriving them from the symbol
table — so a write target is a name Why3 is guaranteed to hold in scope and to consider mutable.
`_emit_frame_condition`'s val arm then contributes an `AssignsRegion` base to the `writes` set
when it is one of those parameters.

**The over-approximation to the whole array is not a penalty imposed on the val — it is EQUALITY
with the verified-body baseline.** Why3 infers the effect of a `let` from its mutations, and in
the value-semantic model a body that writes one cell yields the same whole-array write: a caller
keeps nothing about the array, not even cells outside the declared region. Measured both ways
(witnesses 1269 / 1270): the real-body program and its `\trusted` twin now BOTH refuse a claim
about an out-of-region cell. Before the repair, exactly one of them proved. So the repair did not
make a bodyless stub stricter than a verified one; it made it equal, which is the only frame a
bodyless stub was ever entitled to.

## BOTH DIRECTIONS, MEASURED

| driver | before | after |
|---|---|---|
| N2 exploit (`\trusted` + `assigns a[0..n]`) | PROVES `\result == 7` | **FAILS** |
| N4 the `\abstract` arm | PROVES | **FAILS** |
| N1 **capability twin** — the same stub with `ensures a[0] == 9`, caller claims `\result == 9` | PROVES | **STILL PROVES** |
| N3 real-body control | FAILS | FAILS |
| N5 field-assigns control (the 2026-08-26 fix) | FAILS | FAILS |
| CPython | `driver([7,7,7,7]) == 0` | unchanged |

N1 is the arm that matters most: a repair that makes every exploit refuse is worthless if it also
makes the honest program refuse. The new `writes { a }` havocs the array and the stub's OWN
`ensures` re-pins the cell the caller reads, so the trusted boundary still transmits array facts.

## THE FAIL-CLOSED RESIDUE, WITH EACH FENCE NAMED AND QUOTED FROM AN EXECUTED RUN

A base that is not an `array`-typed parameter contributes nothing. That residue is **empty**, and
not by argument:

* **a module-GLOBAL array** — refused upstream by `core_ir_semantic.py:242-258`
  (`_check_assigns_regions`, `PYCSL-SEM-ASSIGNS`): *"Assigns region references undefined variable
  'g' in function 'scramble'."* The base must be in the function's symbol table.
* **a non-list base** (`str`, `dict`, `set`, `int`) — refused by the same guard's second arm:
  the type must be one of `list` / `List` / `Any`.
* **`Any`, the third admitted type** — reaches emission as `(a: int)` and Why3 **TYPE-REJECTS**
  the caller's array argument: *"This term has type int, but is expected to have type
  array.Array.array 'xi"*. Fail-closed, the same shape as gen #13's C8 Union-narrowing verdict.

## WITNESSES

1267 (trusted exploit, xFAIL) - 1268 (`\abstract` arm, xFAIL) - 1269 (real-body baseline, xFAIL)
/ 1270 (its trusted twin, xFAIL; the pair is the standing EQUIVALENCE witness — if a future change
re-introduces region precision on one side only, exactly one of them flips) - **1271 (capability
preserved, MUST PROVE)** - 1272 (the FIELD cell of the 2x2, still refused, so the 2026-08-26 field
frame fix is pinned against regression).

## REOPENING CONDITIONS

1. Any change that lets a region base be something other than an `array`-typed parameter — a
   relaxation of `_check_assigns_regions`, or an `Any` param that starts emitting as an array —
   re-opens the fail-closed residue and must re-measure all three fences above.
2. A region `assigns` on a `self.<field>` array. The parser (`_parse_assigns_region`) accepts only
   a bare NAME, so `self.buf[0..n]` is not expressible today; making it expressible would create a
   new cell of this 2x2 that this repair does NOT cover.
3. Any future model in which `let` DOES transmit region precision to callers. The soundness
   argument here is val-equals-let; if `let` gets sharper, the val must get sharper with it or the
   equality claim in 1269/1270 becomes false in the unsound direction.
