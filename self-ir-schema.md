# self-ir-schema.md — a typed `self.ir` slice to un-`\trust` the 12th handler

**Doctrine:** [no-more-int] for the emitter's reflection on its OWN INPUT IR. The last
`\trusted` reflecting-family handler — `_handle_critical_section_stmt` — reflects on
`self.ir`, the transpiler's untyped nested input IR (`Dict[str, Any]`). This plan gives the
one slice it reads (`self.ir.get("shared_vars", [])`) a **minimal typed WhyML model**, so the
comprehension over it type-checks and the handler closes (→ **12/12** handlers).

**Sub-plan of** `list-comprehension-lowering.md` §8 (L8). Companion to
`typed-ir-for-b-ceiling.md` / `i-feel-good.md` (11 handlers landed).

**Feature-vs-refactor:** FEATURE, **byte-clean by construction** — every model is gated on
`@mutable_state`, which the 627-file corpus has none of. Gate: **byte-diff 0** + type-check +
a checked `assigns` frame + non-vacuity.

---

## 0. The verdict — exactly what critical_section reflects on `self.ir` (measured)

```python
shared_for_mutex = [
    sv["name"] for sv in self.ir.get("shared_vars", [])   # IR1: array of shared-var records
    if sv.get("mutex") == mutex                            # (filter — opaque in the L1 lowering)
]
for var in shared_for_mutex:                               # IR4: for-loop over `array string`
    safe_var = whyml_ident(var)                            #      var : string → whyml_ident ✓
    self._havoc_counter += 1                               # IR4: scalar self-field frame
...
inv_str = self._mutex_inv_application(mutex, inv_str)      # IR4: sibling stub (-> str)
body_code = self._stmts_to_whyml([s.to_dict() for s in body_stmts], …)  # IR2: emit_ir comprehension
```

**The crucial simplification (from L1).** The comprehension lowers to the OPAQUE
`list_comp_<τ> src` — the element expr `sv["name"]` and filter `sv.get("mutex")==mutex` are
**never emitted to WhyML**. So the handler does NOT need a faithful model of `sv`'s dict
reflection; it needs only:
1. the ITERABLE `self.ir.get("shared_vars", [])` to be an **array** (any element type), and
2. the comprehension's ELEMENT TYPE inferred as **`string`** (so `shared_for_mutex : array
   string` and the downstream `whyml_ident(var)` type-checks).

That is the whole problem. No deep `Dict[str, Any]` model is required — just a typed element
for the one list `self.ir.get(<key>)` returns, and a loop-var binding for type inference.

---

## 1. The model — a minimal `sharedvar` element record (sound, bounded)

```whyml
type sharedvar = { sv_name: string; sv_mutex: string }
val ir_shared_vars (ir: int) : array sharedvar      (* self.ir.get("shared_vars", []) — opaque
                                                       array; content unmodeled, type faithful *)
```

- `self.ir.get("shared_vars", <list-default>)` → `(ir_shared_vars self.ir)` : `array sharedvar`.
- The comprehension loop var `sv` is bound (FOR ELEMENT-TYPE INFERENCE ONLY) to the iterable's
  element type `sharedvar`; `sv["name"]` → the `sv_name` field (string) → the comprehension
  element type is `string` → `list_comp_string_filt` → `shared_for_mutex : array string`.
- **Sound:** `ir_shared_vars` is an opaque array (its contents are never claimed); the record
  fields carry only the string TYPE, never a value. The handler's `ensures True` + frame hold.

`self.ir` itself stays an opaque `int` field (the untyped `Dict[str, Any]`); ONLY the
`shared_vars` slice is typed — the minimal surface critical_section reads.

---

## 2. Stages (byte-diff-gated)

- **IR1 — `self.ir.get(<key>, <list-default>)` → an array.** Recognize a `.get` on `self.ir`
  (a Var `self` `.ir`, or the field) with a string key and a LIST default `[]` → an abstract
  array. For the `"shared_vars"` key emit `(ir_shared_vars self.ir) : array sharedvar` (the
  `sharedvar` record + `ir_shared_vars` val on demand). @mutable_state-gated. *Gate:* the
  iterable type-checks as an array; corpus byte-diff 0.
- **IR2 — comprehension loop-var element type.** In L1's element-type inference, bind the
  generator `target` to the iterable's element type: for `sv in self.ir.get("shared_vars")`,
  `sv : sharedvar`; for `s in body_stmts`, `s : <StmtIR/emit_ir>`. Then `sv["name"]` /
  `s.to_dict()` are typed at inference time. *Gate:* `shared_for_mutex : array string`,
  `[s.to_dict() for s in body_stmts] : array emit_ir`.
- **IR3 — `sv["name"]` / `sv.get("mutex")` → `sharedvar` field reads** (string), used only in
  element-type inference (the opaque comprehension discards the emitted form). *Gate:*
  `_is_string_expr(sv["name"])` is True when `sv : sharedvar`.
- **IR4 — the rest.** `_havoc_counter: int` field + `assigns self._havoc_counter`;
  `_mutex_inv_application(mutex, inv) -> str` sibling stub; the `for var in shared_for_mutex`
  loop over `array string` (var : string). *Gate:* each type-checks.
- **IR5 — un-`\trust` `_handle_critical_section_stmt`** with its checked frame
  (`assigns self._havoc_counter` — the only transpiler-state write). *Gate:* verifies
  un-`\trusted`; suite green (only pre-existing `errors.py`); byte-diff 0.

---

## 3. Critical files

- `src/pycsl/module6_whyml/preamble.py` — the `sharedvar` record + `ir_shared_vars` val (on
  demand, @mutable_state).
- `src/pycsl/module6_whyml/expressions.py` — `_lower_dict_get_call` (the `self.ir.get(key,[])`
  recognizer), `_is_string_expr` / `_is_emit_ir_expr` (`sv["name"]` field read), the
  ListComp element-type inference (loop-var binding — likely in `statements.py`
  `_collect_array_elem_types` and the L1 dispatch).
- `src/pycsl/module6_whyml/statements.py` — `_collect_array_elem_types` loop-var binding.
- `src/self-annotate/src/module6_whyml/statements.py` — `_havoc_counter` field,
  `_mutex_inv_application` stub, the un-`\trust` edit + frame; a loop invariant on the
  `for var in shared_for_mutex` loop if the emitted array read needs a bound.

---

## 4. Out-of-scope / soundness boundary

- **`self.ir` stays opaque** except the `shared_vars` slice — the untyped `Dict[str, Any]`
  is NOT modeled; only the one list the handler reads gets a typed element. A different
  `self.ir.get(<other-key>)` stays opaque (documented).
- **Content is never modeled** — `ir_shared_vars` is an opaque array; `sv_name`/`sv_mutex`
  carry only the string type. `ensures True` + frame only, not value-faithful.
- **Corpus untouched** — @mutable_state-gated; byte-diff 0 is the proof.
- This is a SOUND under-approximation: the opaque array + typed element can never prove a
  false claim about the shared-var list.

---

## 5. Reference corpus (required)

Add to `test-suite/corpus/pycsl-reference/` + a mirror witness under `src/self-annotate/`:
- `self-ir-comp-witness.py` — a `@mutable_state` method with `[e["name"] for e in
  self.d.get("xs", [])]` binding an `array string`, iterated with a string consumer.

---

## 6. Verification (exact commands)

```bash
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl --no-proof
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl        # full proof
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <baseline> /tmp/after
bash bin/run-self-annotation-suite.sh    # only pre-existing errors.py may fail
```

---

## 7. Definition of done

- IR1–IR5 landed; `self.ir.get("shared_vars")` typed; the comprehension → `array string`;
  `_handle_critical_section_stmt` un-`\trusted` with a checked frame.
- **12 real emitter handlers verify their own body-faithfulness** — the reflecting-family
  trusted base EMPTY.
- Byte-diff 0; suite green; `list-comprehension-lowering.md` §8 (L8) closed.
