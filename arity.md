# arity.md — fixing the inliner's array-typed temporary bug

**Status:** Plan / partial work in tree (uncommitted), blocked on upstream PyCSL-source update
**Owner:** TBD
**Source of truth for the inliner:** `src/pycsl/ir_inline.py`, `inline.md` (Phases 1–3)
**Companion:** the inline feature drivers `0576`–`0580`; the imported-class fix `ab962c1`
(`Module5_IREmitter.py`, `module_globals` detection).

---

## 1. Symptom

After `ab962c1` taught `collect_module_globals` to recognise imported class names
(`from X import Y` → `_filesystem = UnixInodeFileSystem()` is now seen as a module-level
global instance), the inliner *fires* on method calls against such globals. But for a
method whose parameter — or a local/intermediate that flows an `array int` — is array
typed, the emitted WhyML fails to type-check: a temporary introduced by the inliner is
declared as `ref 0` (int) yet used where an `array int` is expected, and operations on it
are emitted with the *abstract* opaque-int ops instead of the *concrete* array ops.

The authoring agent described it as "helper function stubs (`_unpack_direntry_1`, etc.)
still have `int` parameter types, but the inlined body passes `array int` to them." The
underlying mechanism is type erasure at the inline boundary (§2). No committed driver
exercises it yet, so the reference suite is green; this is a **latent** defect on the
imported-class inline path, not a regression in the 0576–0582 drivers.

---

## 2. Root cause — TWO layers, not one

The defect is **type-erasure at the inline boundary**, not a gap in `array int` support
(array params and locals work fine outside inlining). The erasure surfaces as two distinct
failures, and fixing only the first leaves the second.

### 2a. Declaration-typing layer

The inliner binds every **non-trivial** actual argument to a fresh temporary before
substituting it into the method body. In `ir_inline.py::_Inliner._expand`
(`src/pycsl/ir_inline.py:211-217`):

```python
for formal, actual in zip(formals, args):
    if isinstance(actual, dict) and actual.get("type") in ("Var", "Number", "Constant", "Bool"):
        param_map[formal] = actual
    else:
        tmp = self._fresh(formal)
        pre.append({"stmt": "Assign", "target": tmp, "value": copy.deepcopy(actual)})  # ← untyped
        param_map[formal] = {"type": "Var", "name": tmp}
```

The temp is emitted as a bare `Assign` carrying **no type**. Module 6 then re-derives the
temp's WhyML type by a *syntactic* scan of the RHS (`IRScanner.find_array_and_dict_vars`,
`ir_scanner.py:100`), which marks a local `array int` only when the RHS is a recognisable
array **producer** (`ListLit` / `ArrayLit` / `ListComp` / `list()` / `sorted()` /
`SliceAccess` / `[x] * N`). A temp whose RHS is a `Var` aliasing an array, a `FieldGet` of
an `array int` field (the `UnixInodeFileSystem` inode-table shape), or a `Call` to a
function/method returning `array int` is **not** recognised → it falls to the default local
pre-declaration `ref 0` (`stmt_control_flow.py:310`) → used as `array int` → Why3 type error.

The callee *does* know the formal's type (`array1d_params`, the arg symbol-table consulted
by `functions.py::_param_type_str:13`, and `_module_method_return_types`). The inliner
**discards** it when manufacturing the temp. (Module 5's `formal_params`,
`Module5_IREmitter.py:1455`, is names-only; the types live in sibling fields on the same
function dict — so Block-1's "the IR stores no types" is wrong; the types exist, they're
just not threaded across the inline boundary.)

### 2b. Operation-selection layer (the layer the first pass misses)

Even once a temp is *declared* `array int`, the statement emitter still has to pick the
right operation. A subscript write `inode[3] = mode` is emitted two ways
(`statements.py:388-460`):

- **`is_array` true** → concrete: `inode[3] <- mode` with an `Array.length` bounds check.
- **`is_array` false** → abstract: `subscript_set inode 3 mode`, where
  `val subscript_set (x: int) (i: int) (v: int) : unit` (`statements.py:459`) takes an
  **int** receiver.

So a temp that is correctly *declared* `array int` but whose `is_array` decision at the
write site is still false emits `subscript_set !inode 3 mode` → "array.Array.array int,
but is expected to have type int". **Concretising an opaque type via inlining forces every
operation on it to switch from abstract ops to concrete array ops** — and the `is_array`
decision at each operation site reads a *different* set (`_array_locals` + a `FieldGet`
check at `statements.py:405`) than the declaration path does.

### 2c. The deeper smell — too many disagreeing detectors

Array-ness is decided independently by at least five mechanisms that can disagree:
`find_array_and_dict_vars`, `_collect_array_var_assigns` (`types.py:295`), `_typed_local_vars`
(`statements.py:824`), the `_array_locals` set, and the per-site `is_array` heuristic
(`statements.py:388`). The 2a/2b split is exactly a case where one path is taught about a
var and another isn't. Patching each detector is whack-a-mole; the durable fix asserts the
type **once** and threads a single authoritative set through both declaration and operation
selection.

---

## 3. Fix strategies

### Strategy A — propagate the type at the inline boundary (recommended)

The inliner has full type context (callee `symbol_table`, `array1d_params`,
`_module_method_return_types`). Assert each freshened local's / intermediate's type **at
inline time**, and merge it into the caller's *one* authoritative typed-local set — not
re-infer it later.

1. In `_expand`, classify each formal / temp from the callee dict (reuse the
   classification `_param_type_str` already encodes: array / dict / record / int).
2. Return those typed-local entries alongside the statements (`_expand` lacks the caller
   IR — Block 3 is right that the merge belongs one level up, in `inline_stmts` /
   `apply_inline_globals`, which *do* have the function dict).
3. Feed the merged set into **both** the declaration path *and* the per-site `is_array`
   decision, so 2a and 2b are driven by the same source of truth.

**Why this beats post-hoc inference:** it dissolves 2a's transitive-propagation problem
(`inode := !_inl_res` is stamped from the formal's type — no var-to-var re-inference, no
fixpoint loop) and 2b's `subscript_set` surprise (the same set drives operation selection).

### Strategy B — make Module 6's scanners type-aware (the in-tree partial attempt)

Extend the post-hoc scanners to recognise array-returning calls + transitive var-to-var
aliasing (needs a fixpoint). This is what the **uncommitted in-tree work currently does**
(see §4). It is the *symptom-patching* layer: it works for 2a but required a `while changed`
propagation loop and still leaves 2b open. Higher regression surface (touches `types.py` /
`statements.py`, which type *every* function, not just inlined ones).

### Recommendation

Land **Strategy A**. If the upstream update arrives as Strategy B, accept it only with the
2b operation-selection fix included and the byte-diff gate green — and treat the multiple
overlapping detectors (§2c) as tech debt to consolidate.

---

## 4. State of the in-tree (uncommitted) work

As of this writing the following are modified but **uncommitted** on `main`
(`git diff` — stash/branch before it is lost):

- `ir_inline.py` — (i) freshen dotted-call receivers `entries.append` →
  `entries__inlN.append` (real correctness fix, orthogonal — **keep**); (ii) treat
  `String` actuals as trivial (no temp).
- `types.py` — (i) `_field_type_of` now resolves `global.field`, not just `self.field`
  (necessary for inlined global field access — **keep**); (ii) `_collect_array_var_assigns`
  now catches bare array-returning calls + transitive var-to-var with a `while changed` loop
  and a `seed`.
- `statements.py` — one line: pass `seed=array_vars` into `_collect_array_var_assigns`.
- `pycsl.py` — +20 lines (inspect before judging).

**Incomplete:** the reasoning trace stops *at the realisation* about `subscript_set`; the
operation-selection fix (§2b) is **not** implemented (the `statements.py` change is only the
`seed=` pass-through). The reproducer almost certainly still fails. We are waiting on the
upstream PyCSL-source update before doing more here.

---

## 5. Implementation steps (when unblocked)

1. **Reproduce (Gate-A driver first).** Minimal failing driver under
   `test-suite/corpus/pycsl-reference/` (~`0583`): imported-class module global whose method
   takes/returns `array int`, with a statement-position call (`inline_stmts`) **and** an
   expression-position call (`_hoist_calls_in_expr` + `_inl_res`), and an in-body array
   subscript **write** to force the 2b path. Confirm the Why3 type error; dump with
   `bin/pycsl-ir-dump.py` and inspect `/tmp/.pycsl_*.mlw`.
2. **Fix 2a + 2b together** via Strategy A (or accept B with 2b included).
3. **Consider eliminating the redundant `_inl_res`** for `x = g.m(args)` (Block 3): pass the
   caller's target as `result_var` so the inliner assigns straight to `x` — fewer untypable
   intermediates.
4. **Cover dict- and record-typed temps**, or `log()` the deferral in the driver docstring.

---

## 6. Test plan (corpus drivers)

Per the reference-corpus discipline, add to `test-suite/corpus/pycsl-reference/`:

- **`0583` (positive):** imported-class global, method with an `array int` parameter,
  inlined; proves a true postcondition about an element read.
- **`0584` (positive):** method **returning** `array int`, inlined in expression position
  (exercises `_hoist_calls_in_expr` + `_inl_res`); proves a fact about the result.
- **`0585` (positive, 2b):** inlined body that **mutates** the array (`a[i] = v`) — forces
  the `Array.set` / bounds-check path, not `subscript_set`.
- **`0586` (negative, `# pycsl-expected: FAIL`):** false post-claim about the array —
  confirms the inlined array temp is not vacuously typed/true.
- Mirror the inline-family convention (`0576`–`0580`): docstring states the Phase,
  `# pycsl-flags: --memory-model hoare`.

---

## 7. Verification / gates

1. `bash bin/run-reference-tests.sh --pycsl --start-at 576 --stop-at 586` → all PASS/XFAIL.
2. Full sweep: `bash bin/run-reference-tests.sh` → no regressions. **Critical here:** the
   in-tree fix touches `types.py` / `statements.py`, which type *every* function — not just
   inlined ones — so a full green sweep is mandatory, not optional.
3. **Emission-identical byte-diff gate** (`bin/extraction-byte-diff*.sh`): a driver that does
   NOT trigger array-temp inlining must emit byte-identical WhyML before/after — the type
   changes must be inert on the non-array path.
4. PyCSL language audit `bin/audit-pycsl-language.sh` — should be a no-op (IR-internal only,
   no new `#@` clause).

---

## 8. Docs to update on landing

- `inline.md` — inlined temporaries/locals carry the callee's declared type (array/dict/
  record), and operations on a concretised array switch to concrete array ops.
- `test-suite/annotations.md` + `remains-2.md` — record the fix and drivers `0583`–`0586` in
  the inline cross-reference.
- `docs/glossary/method-call-inlining.md` — one line on temp typing / op selection.

---

## 9. Out of scope

- Recursive-method inlining (correctly refused — driver `0580`).
- Aliasing a global into a local / passing it as an argument (banned by `_check_no_aliasing`,
  `ir_inline.py:308`).
- 2-D (`matrix`) temps — extend only if a driver needs it; the same mechanism generalises.
- **Do NOT** modify `UnixInodeFileSystem.py` to work around the tool bug (Block-1 options
  1/2/4) — that deforms a faithful stub to hide a transpiler defect, violating the
  extreme-rigor / faithful-semantics discipline. Adding *correct* missing type annotations
  to a source helper is fine; coaxing inference by restructuring is not.
