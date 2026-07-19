# targeted-refactor.md — verifiability-driven refactor of the stateful-giant emitters

**Purpose.** Make the trusted "stateful giant" methods of the IR emitter (`src/pycsl/frontend/Module5_IREmitter.py`)
verifiable under the self-tcb-reduction fixed contract, by an **incremental, behavior-preserving refactor of the LIVE
emitter toward purity** — thread accumulating state as explicit in/out values instead of mutating instance/program
state. Each refactored method then converts to a verified mirror stub exactly like the annotation-walkers did.

**This is NOT a rewrite.** It is a sequence of small, byte-diff-gated moves, each of which *relocates where state
lives* (from `self.*`/`program_ir` mutation to parameters + return values) **without changing what WhyML is emitted**.
The reference-corpus byte-diff (767 files) MUST stay 0 at every step — that is the proof the refactor is
behavior-preserving.

---

## 1. Diagnosis — why the giants resist the fixed contract

The contract is `#@ requires True / ensures True / assigns <frame>` (type-safety + frame only). The giants fail it
because their *frame* is a large mutable heterogeneous state that the modular per-method proof cannot model:

| State | Where | Why unmodelable |
|---|---|---|
| `program_ir` | the ~15-key `Dict[str,Any]` result being appended to (`program_ir["functions"]`, `["type_decls"]`, `["constructors"]`, …) | a growing heterogeneous dict is not the `emit_ir` ADT nor a record; `assigns program_ir["k"]` has no faithful frame |
| `self._cur_*` / `self._protocols` / `self._current_class` | instance fields set in one method, read in another | cross-method state; the modular proof verifies each method in isolation and can't thread it |
| `self._fresh_var_counter` | a monotonic counter bumped for gensym | a side-effecting counter with no value contract |

These are an **architectural** gap, not a transcription gap (unlike the annotation-walkers, whose blockers were tool
value-model primitives). The fix is to remove the mutation, not to model it.

## 2. The refactor pattern (the reusable "primitive")

For each giant, apply **state-threading toward purity**:

**Before** (mutating):
```python
def _collect_typevar_registry(self, module_node):
    for stmt in module_node.body:
        if <is a TypeVar assign>:
            self._typevar_registry[name] = bound      # instance mutation
```
**After** (pure — returns the value; the CALLER stores it):
```python
def _collect_typevar_registry(self, module_node):          # now: module -> registry
    registry = {}
    for stmt in module_node.body:
        if <is a TypeVar assign>:
            registry[name] = bound
    return registry
# caller (visit_Module):  self._typevar_registry = self._collect_typevar_registry(module_node)
```
The refactored method is a **pure map-reduce** (`assigns \nothing`, `ensures True` — its result is a value it built),
which verifies trivially. The single caller absorbs the one assignment (and that caller is itself refactored later,
or its one-line `self.x = f(...)` is a trivially-framed method).

Two recurring sub-patterns:
- **Counter threading.** `self._fresh_var_counter` → pass `counter_in`, return `counter_out` (or return the list of
  fresh names + the final counter). Makes gensym functional.
- **Accumulator threading.** `program_ir["functions"].append(x)` inside a walk → the method **returns the list** it
  built; the caller does the single `program_ir["functions"] = [...]`.

## 2b. CENSUS CORRECTION (2026-07, read-only classification of all 24 candidates)

**Only ~9 of the 24 "giants" are genuine REFACTOR targets. ~11 are ALREADY PURE** (they return their result and
mutate nothing — they only *read* `self.*`), blocked solely by a **collection-accumulator loop** → they are
TRANSCRIPTION targets, not refactor targets. 4 are true orchestrator giants (both). Do the transcription track FIRST
(it needs no `self.*` code motion and un-trusts more methods faster), the refactor track SECOND.

- **PURE-NOW (11, transcription — a NEW `loop-building-a-DICT/LIST` primitive):** `_build_function_symbol_table`
  (the flagship — builds 3 maps, returns a 7-tuple, mutates nothing), `_collect_typevar_registry`,
  `_collect_class_constants` (dict); `_collect_type_params`, `_collect_union_arms`, `_synthesize_overload_guard`,
  `_build_overload_param_guard` (list); `_collect_class_fields` (both); `_field_type_from_annotation_inst`,
  `_m5_get_type_name` (try/except recognizer-dispatch, no loop); `generate_json` (trivial). ONE primitive pair
  (loop-building-a-dict + its list twin, off the banked `loop-over-irlist` skeleton) converts 7 of these with ZERO
  code motion.
- **MUTATES (9, refactor — category (a) return-the-value unless noted):** `_collect_final_registry` (POC — single
  accumulator, no counter, no cross-method read, has a pure sibling `_collect_typevar_registry` to mirror),
  `_emit_typeddict_record`, `_emit_namedtuple_record`, `_synthesize_typeddict_functional`,
  `_synthesize_namedtuple_functional`, `_synthesize_tuple_records` (append to program_ir, (a)); `_normalize_literal_
  annotation` (cross-method accumulator `self._cur_literal_*` read by `_build_function_ir`, (b)); `_populate_protocol_
  conformance` (append + cross-method `self._protocols` read, (a)+(b)); `_normalize_union_annotation` (append +
  `self._fresh_var_counter` — category (c), the HARD one).
- **BOTH/GIANT (4, last):** `_build_function_ir`, `visit_Module`, `visit_ClassDef`, `visit_FunctionDef` — need the new
  primitive AND state-threading; tractable only after both tracks are proven.

**Revised POC = `_collect_final_registry`** (not `_build_function_symbol_table`, which is PURE-NOW transcription): it
appends to `self._final_registry` and returns `None` for no reason, has a single accumulator consumed immediately at
the plumb site (visit_Module ~353), and an identical *pure* sibling (`_collect_typevar_registry`) to copy — the
cleanest 3-line "return-the-value, caller absorbs" demonstrator.

## 2c. MEASUREMENT CORRECTION (emission probe refuted §2b's "collection-loop" premise)

An emission probe (converting `_collect_class_constants` and reading the `.mlw`) proved the collection accumulator is
**not** the blocker — `map_update_some` (map) and `Seq.snoc` (seq) already build real collections in a real
`while`+invariant+variant. **The real blocker is that the ITERABLE and its ELEMENTS are un-modeled opaque AST nodes:**
`node.body` (ClassDef body) lowers to opaque `get_body`/`iter_get`; each `child` is an opaque `int`;
`isinstance(child, ast.Assign)` → `isinstance_op` (×5+); `child.targets[0].id` → `get_id(subscript_get(get_targets …))`;
`target in field_names` → `contains_check`. The map is populated with **opaque keys/values from an opaque iteration** —
a vacuous facade. **0 of the 7 PURE-NOW targets convert with a collection primitive.**

**Corrected prerequisite for the ENTIRE giants front (both PURE-NOW collectors AND MUTATES refactor targets):**
**statement/definition-node AST modeling**, extending the expr-node modeling to:
- child-list readers `class_body_ast` (ClassDef `.body`), `func_args_ast` (FunctionDef `.args.args`), `type_params_ast`
  (paralleling the existing `class_bases_ast`);
- typed statement/arg element-field readers (`.targets`/`.value`/`.annotation`/`.arg` on the iterated child);
- a reflection-handling decision for `type(x).__name__` / `getattr(tp,"name"/"bound")` (a genuine value-model wall,
  same class as the confirmed boundaries in `emit-ir-conversion-lessons.md` §3).

**Consequence for the refactor track:** the return-the-value refactor makes a MUTATES method pure, but its mirror
still can't be verified until this AST modeling lands (it iterates `ClassDef`/`FunctionDef` bodies too). So the
refactor is NECESSARY-BUT-NOT-SUFFICIENT — **the statement/definition AST modeling is the gating prerequisite for the
whole front.** This is a substantial multi-reader build (per node type), NOT a lowering primitive — an authorize-first
multi-session effort. The POC ordering below still holds, but AST modeling comes first.

## 3. Target set + ordering (easy → hard) — [superseded by §2b/§2c; the tiers below apply WITHIN the MUTATES set, AFTER the AST-modeling prerequisite]

Do them in this order; each tier is a prerequisite-free batch, and later tiers get easier as callers become pure.

**Tier A — COLLECTORS (pure map-reduce; do FIRST):** `_build_function_symbol_table`, `_collect_typevar_registry`,
`_collect_type_params`, `_collect_final_registry`, `_collect_class_fields`, `_collect_class_constants`. Each builds a
dict/list from a walk and stores it in `self.*`. Refactor = return the built value; caller assigns. Lowest risk,
clearest byte-diff-0.

**Tier B — NORMALIZERS (compute a tag + a side-output):** `_normalize_union_annotation`, `_normalize_literal_
annotation`, `_collect_union_arms`. These mutate `program_ir["type_decls"]` / `self._cur_literal_*` AND bump the
fresh-var counter. Refactor = return `(tag, new_type_decls, counter_out)` as an explicit tuple; caller threads.
Medium.

**Tier C — CLASS-SYNTHESIS EMITTERS:** `_emit_typeddict_record`, `_emit_namedtuple_record`,
`_emit_protocol_interface`, `_populate_protocol_conformance`. Walk a `ClassDef`, build a record/member IR, append to
`program_ir`, and read/write `self._protocols` / `self._current_class`. Refactor = return the record(s) + the protocol
update; caller appends and stores. Medium-hard (cross-method `self._protocols` must become an explicit in/out).

**Tier D — ASSEMBLERS / VISITORS (the pipeline; do LAST):** `_build_function_ir`, `visit_FunctionDef`,
`visit_ClassDef`, `visit_Module`, `generate_json`. These orchestrate everything and own `program_ir` + the counter.
Refactor = build and RETURN the IR sub-tree; thread `program_ir` and `counter` functionally through the visit. Do
these only after A/B/C, when most callees are already pure.

## 4. Proof-of-concept (the FIRST refactor to land)

**Target: `_build_function_symbol_table`** (Tier A) — recommended because it is the most self-contained collector
(builds one symbol-table dict from a function node's params/locals) with a single well-defined output currently stored
in `self._cur_func_symtab`, and it is *read* by already-converted handlers (so proving it complete tightens a real
dependency). If on inspection it has an awkward cross-method dependency, fall back to `_collect_typevar_registry`
(module-level, no per-function coupling).

**POC acceptance criteria (all required):**
1. **Behavior-preserving:** `PYTHONHASHSEED=0 bin/byte-diff-sweep.sh` + `diff -rq` vs pre-refactor baseline = **EMPTY**
   (767 files). This is the load-bearing proof the refactor changed no emitted WhyML.
2. The refactored live method is **pure** (`assigns \nothing` or an explicit-param frame) — no `self.*`/`program_ir`
   write in its body; the single caller absorbs the assignment.
3. **Convert its mirror stub** to the verbatim refactored body → whole-file M5 proof SUCCESS, isinstance_op=0,
   fidelity (mirror body == refactored live body), ledger 3.
4. **Consumer re-proof:** the mirror files that read the produced state still prove (whole-file), and
   `bin/self-annotate-mirror-check.sh` green.
5. Count strictly drops (the giant is un-trusted).

If the POC lands, the pattern is validated and Tiers A→D proceed one method per byte-diff-gated increment.

## 5. Gate (per refactored method) — the fidelity oracle SHIFTS

Because the LIVE emitter changes, the fidelity check is against the **refactored** live body (still verbatim: mirror
body == refactored live body, modulo `#@`). The full gate:
- **Corpus byte-diff 0** (the refactor is behavior-preserving) — MANDATORY, non-negotiable; a non-zero diff means the
  refactor changed emission → not behavior-preserving → revert and rethink.
- Whole-file Why3 proof SUCCESS; isinstance_op=0; fidelity-verbatim; ledger 3 (no new axiom); consumer mirrors
  re-prove; mirror-check green.
- Commit the LIVE refactor + the mirror conversion together (they must co-land — a refactored live method whose mirror
  isn't updated drifts the fidelity gate).

## 6. Risks & constraints

- **Behavior preservation is the hard constraint.** Threading state can subtly change ordering (e.g. when a fresh-var
  counter is bumped, or when `program_ir` keys are populated). Any such change shows as a non-zero byte-diff → caught
  by the gate, but plan the threading to preserve evaluation order exactly.
- **`self.*` read by OTHER (still-trusted) methods.** When you stop mutating `self._x` in method M and make the caller
  assign it, verify every reader of `self._x` still sees it set at the same program points. The single-caller,
  caller-assigns pattern preserves this; a multi-caller field needs care.
- **Do NOT refactor for elegance beyond what verification needs.** The goal is a modelable frame, not a functional
  purity crusade — minimize the diff (smaller diff = easier byte-diff-0 + easier review).
- **Scope creep to `program_ir` as a typed record.** Tempting but large. Prefer accumulator-threading (return the
  list, caller appends) over redefining `program_ir`'s type. Only consider a typed `program_ir` if Tier D proves it
  necessary — and treat that as its own authorize-first decision.
- **Impact if completed:** unlocks ~15–20 trusted stubs (a real TCB cut) and leaves the emitter with pure, testable
  passes. Cost: a multi-session, behavior-preserving refactor of the compiler core — larger and riskier than the
  transcription work, justified only if driving the TCB below the giant floor is the goal.

## 7. Reference-corpus requirement

Per project convention, if any refactor introduces a genuinely new emitter shape that a reference program should
exercise, add it to `test-suite/corpus/pycsl-reference/`. (Most of this refactor is behavior-preserving and adds no
new shape — byte-diff-0 is the expectation — so new fixtures should be rare; a non-empty byte-diff is a red flag, not
a fixture-regen event, unless the change is a deliberate, separately-justified emission change.)
