# faithfulness-bugs-found.md — latent live-tool lowering bugs surfaced by the self-tcb-reduction driver (2026-07-20)

Two independent driver-run conversion attempts each surfaced a **latent faithfulness bug in the LIVE emitter**
(`src/pycsl/`): a construct that lowers to a **consistent-but-WRONG** WhyML value, passing proof vacuously
(under `ensures True`) and byte-diff-0 (stable across the corpus) yet semantically unfaithful. Each has a
**verified working fix**, but each fix **cannot co-land in the self-tcb loop** because the mirror method that
carries it cannot self-prove the fixed body (the emit_ir / generic-dict value-model wall) — so keeping the fix
would introduce a mirror body-staleness (fidelity divergence) for a change that converts NO `\trusted` stub.
Both were therefore REVERTED from the driver run and recorded here as **flagged tickets** for proper landing
once the value model closes (or as an explicit user decision to accept a live-only tool fix + documented mirror
staleness). **Neither currently poisons a green result** (audited: zero verified-corpus occurrences of the
dict-literal case; the slice case affects 3 real corpus programs' fidelity but they were already
consistently-wrong, not falsely-green).

## Bug 1 — variable-valued dict-literal construction DROPPED (empty map)
**FIXED 2026-07-20 (commit 805e9330)** — `_emit_first_assign`+`_build_dict_literal_map` now construct the real map; corrected corpus 0751; mirror-neutral; M1-sanctioned. The hard-reject proposal below is superseded.

`d: Dict[str,τ] = {"k": var}` (a str-literal key with a VARIABLE value) emits `ref (const (None: option int))`
— an EMPTY map; the `"k": var` entry is never constructed and `var` is unused. A method returning it returns an
empty map. **Confirmed a false-theorem generator** (fable review, full SMT run): a FALSE postcondition
`ensures \result == 0` on a function that really returns `{"k": var}` proves **Valid**. Audit: **zero**
occurrences in the 900-file verified corpus / `src/pycsl_lib/` → latent. Short-term hardening (recommended):
make the emitter **hard-REJECT** (fail-closed error) a variable-valued dict-literal instead of silently emitting
the empty map — turns a latent unsoundness into a loud compile error. Full fix: faithful `Dict[str,τ]`
construction (the value-model build). Blocks: `_collect_typevar_registry`, `_collect_type_params`,
`_collect_class_fields`.

## Bug 2 — negative-index string slice `s[1:-1]` → always-empty facade
`inner[1:-1]` lowered to `str_sub_op inner 1 ((-1)-1)` = `substring inner 1 (-2)`, which Why3's
`substring_of_length_zero_or_less` axiom collapses to `""` for EVERY input. Passed proof vacuously + byte-diff.
**Verified fix (works, reverted):** `module6_whyml/expressions.py::_handle_slice_access_expr` string branch —
resolve a syntactically negative bound `-N` to `len − N` (`s[1:-1]` → `str_sub_op inner 1 ((str_length_op inner
− 1) − 1)` = `len−2`, faithful; `str_length_op` emitted lazily so non-negative slices stay byte-identical).
Gate-S spike PROVED axiom-free (Z3: `startswith=prefixof`, `endswith=suffixof`, slice=`substring s 1 (len-2)`;
6 non-vacuous drivers Valid, evil-twin Unknown). Mutation test PASS; whole-file proof SUCCESS; byte-diff changed
`0885.mlw`/`0887.mlw` (the SAME faithful correction — both RE-PROVE SUCCESS). **Co-landing blocker:** the fix
lives in the tool method `_handle_slice_access_expr`, whose OWN mirror is un-trusted+self-proven and CANNOT
re-prove the fixed body (`hi_ir["expr"]` yields `emit_ir` where the value model expects `int` — the V1
generic-dict/emit_ir wall). Marking that mirror `\trusted` would regress the count + downgrade a proven method.
The fix's frame proof is identical for old/new body, so the divergence is frame-invisible — but it is still a
fidelity gap, so it stays reverted pending the emit_ir value model (or a user decision).

## Common root + the unlocking build
Both are the **value model / emit_ir-ADT wall** in different guises. The single build that closes both cleanly
(faithful co-landing, no mirror staleness) is the emit_ir-typed value model for tool-method sub-node reads
(`hi_ir["expr"]` etc. typed as `emit_ir`, not int) — the same wall behind the Dict/List collectors
(`value-model-return-wall.md` §3, `ast-modeling-scope.md` §8c/§8d). Until then: land Bug 1's hard-reject as a
standalone soundness hardening (byte-diff-inert, zero corpus uses) if authorized; keep Bug 2's fix ready.

## Count note
Canonical `\trusted` stub count = **1029** via `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py'
| wc -l` (the annotation form). The broad `grep -F '\trusted'` = 1058 OVER-counts by ~29 PROSE-COMMENT mentions
of the word (`# … stays \trusted …`); it is NOT the stub count.

## Bug 3 — self-field `.append` is a shadow-local facade (never writes back)
**Found 2026-07-21 (pyval cascade R3 spike).** `self._field.append(x)` lowers to a FRESH local
`let self__field = Array.make 1024 0` that SHADOWS the field, then `self__field[len] <- x` — the real
`self._field` is NEVER written back (evidence: `src/pycsl_lib/proc/__init__.mlw:133,150,154`, `setenv`'s
`_env_keys`). So a method's self-field-append EFFECT is unmodeled (the post-state field is unchanged in the model).
LATENT (the affected methods — proc setenv etc. — are `\trusted`, so not a live soundness hole), but it BLOCKS
converting any collector that appends to a self-field (`_collect_final_registry` etc.). The faithful fix = a
self-field seq-append emission subsystem (write-back to the field) + for the heterogeneous case a `seq pyval` field
(the R3 MODELING cert is PROVEN axiom-free + banked, ready to co-land). This is the ≥4-collector leverage node +
the pyval cascade's terminal prerequisite. Related: [[pyval_value_model_built]]; build order in
`getting-better/pyval-value-model-wall-impl.md`.

## Bug 4 — a function returning `[]` CERTIFIED `\length(\result) == 1024`
**FIXED 2026-09-24 (gen #31)** — corrected in `_run_pipeline`'s post-emission pass beside
route #159's; witnesses `1869` (false twin, FAIL) / `1870` (true claim, PASS) / `1871` (the
append path, PASS and unmoved).

```python
#@ ensures \length(\result) == 1024
#@ assigns \nothing
def mk() -> list:
    return []
```
`[+] Verification SUCCESS! All contracts formally proven.` — Python returns 0, and the TRUE
clause `== 0` was REFUSED. Ordinary total Python: no `no_exception`, no opt-in, no
`\trusted` anywhere. `xs = []; return xs` behaved identically on both halves.

MECHANISM: `[]` lowers to `(Array.make 1024 0)` and a Why3 array's length is immutable, so
the model of the empty list has length 1024. Route #159 found this MECHANISM and repaired it
for a LOCAL, on the emitted text, for ONE obligation (`in_bounds`) inside ONE syntactic
scope — and that repair is correct; the local path measures faithful today. The RETURN
carries the false length ACROSS THE FUNCTION BOUNDARY, where a caller ASSUMES it, and
`1024 = <the real length>` is contradictory, so every downstream goal becomes vacuously
provable — the same modular false-green as
`20260718-0633-stmt-list-append-mutation-wall-response.md`, which `--check-vacuity` also
missed. **A repaired mechanism is not a repaired route** (wall-lesson (s4)).

Unlike bugs 1 and 2 this one landed immediately: the repair is mirror-neutral (it is in
`_run_pipeline`, whose mirror twin is `\trusted`) and corpus-byte-inert.

STILL OPEN, and recorded in `open-routes/route225-a-returned-empty-list-has-length-1024.md`:
`Array.make 1024 0` is spelled the same for the CAPACITY of an append target and for the
VALUE of an empty list. One literal cannot be both, because a Why3 array's length IS its
capacity. Separating them is the real repair; `1871` is its guard.

## Bug 5 — a `#@ class invariant` the CONSTRUCTOR never establishes is assumed by every method

```python
#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 5
    def get(self) -> int:
        return self.n

#@ ensures \result >= 5
def read(c: C) -> int:
    return c.get()
```

    [+] Verification SUCCESS! All contracts formally proven.

CPython: `read(C())` is `0`. Ordinary total Python — no `no_exception`, no opt-in, no
`\trusted` anywhere, and the false fact crosses a MODULE BOUNDARY in a published function's
postcondition.

MECHANISM. A `#@ class invariant` lowers to a Why3 TYPE invariant, and Why3 asks only that
such a type be INHABITED. The emitter discharges that by SYNTHESIZING a witness FROM THE
INVARIANT:

    type c = { mutable n: int }
      invariant { (n >= 5) }
      by { n = 10 }

so the witness is satisfiable whatever the invariant says. The obligation that IS raised —
and this is the correction that makes the route precise — is raised at the CONSTRUCTION
SITE: a file containing `c = C()` fails. **It is attached to the construction site rather
than to the CLASS**, so a file that defines the class, publishes a reader for it, and lets
some other file build it is never asked. That is the ordinary shape of a library module.

REPAIR: emit the constructor's own obligation beside the type, the way `#@ mutex_invariant`'s
initial-state check does —

    goal _check_class_inv_c : forall n : int. n = 0 -> ((n >= 5))

— for the shape it can state exactly (a paramless `__init__` storing int literals). CENSUS:
210 classes carry a `#@ class invariant`, 113 are in scope, and **zero of them are violated**
by their own constructors: the obligation had simply never been asked.

UNLIKE BUG 4 THIS ONE IS NOT CORPUS-BYTE-INERT, and it should not be: 60 corpus modules and
12 of the 38 frozen conformance goldens gain the goal line. Both were audited line by line —
ONLY-ADDED-A-GOAL, no removals, zero `*.ir.json` touched, so no IR version bump is owed.

STILL OPEN, in `open-routes/route226-a-class-invariant-the-constructor-never-establishes.md`:
THREE more carriers the goal cannot state — a field from an `__init__` PARAMETER, a computed
or control-flow store, and `@dataclass`. All three are RUNNABLE, and
`bin/check-class-invariant-establishment.py` (new this generation) runs them against the
corpus on every gate.
