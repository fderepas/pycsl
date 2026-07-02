# i-feel-good.md — suppress the wrong int-lowerings in the emitter self-model

**Doctrine:** [no-more-int] applied to the emitter's OWN body. Every value the
`_handle_*` emitter methods manipulate must lower to its faithful WhyML type
(`string` / `emit_ir` / a typed map), never collapse to an opaque `int`. This plan
turns the reactive, per-handler recognizer fixes (`typed-ir-for-b-ceiling.md`
§18–§26) into a **systematic suppression of the six int-leak categories at their
source**, so the remaining `\trusted` handlers (`array_set`, `tuple_unpack`,
`critical_section`) close without discovering the same leak six more times.

**Feature-vs-refactor:** FEATURE (changes emitted WhyML) but **byte-clean by
construction** — every fix is gated on `@mutable_state` (the emitter self-model) or
on an `emit_ir`-typed receiver, neither of which the 627-file corpus exercises. The
gate is therefore **byte-diff 0 across the corpus** + the handler type-checks +
non-vacuity, NOT a corpus re-verify.

**Where it sits.** Companion to `typed-ir-for-b-ceiling.md` (the handler-un-`\trust`
campaign, 9 handlers landed) and `no-more-int-emitter-plan.md` (L1–L5, the original
string-typing layers). This plan is the *consolidation*: the leaks below were found
one-at-a-time; here they are enumerated, root-caused, and each given a single
systematic suppressor + gate.

---

## 0. The verdict — what leaks today (measured, from the array_set / ghost_assign WhyML)

Six root causes generate every wrong int-lowering observed. Each row: the leak, the
emitted-WhyML symptom, the root cause, and the current status.

| # | Leak | Emitted symptom | Root cause | Status |
|---|------|-----------------|------------|--------|
| **A** | string literal → int hash | `else 313406155`; `st.get(k) = 1555321514` | a `str` literal defaults to `stable_hash→int` outside a recognized string context (comparison RHS, ternary arm, default arg) | ⏳ partial |
| **B** | string local → `ref 0` | `let s = ref 0`; `int_to_string !s` | a local first-assigned a string value keeps the integer `ref 0` pre-decl | ⏳ partial |
| **C** | string sibling → int return | `self__m_1 … : int` used where string expected | the abstract self-call `val` for a `-> str` sibling defaults to `int` | ⏳ partial |
| **D** | `emit_ir` reflection → opaque int | `get_1 …`; `subscript_get node …`; `get_field node` | an IR-node reflection form not routed to an `emit_ir` projection falls to the opaque `int` accessor | ⏳ partial |
| **E** | dict/collection read → int | `subscript_get d k`; `self__dict_value_types_get_1` | a dict read on a body-local / getattr-alias / self-field not recognized as a map → opaque int | ⏳ partial |
| **F** | set membership → int container | `contains_check x 0`; `contains_check x !d` | `x in c` where `c` is int-typed (undeclared field → `0`, or an unrecognized alias) | ⏳ partial |

The through-line: **the DEFAULT is int**. Every leak is "recognizer X did not fire, so
the int fallback ran." The systematic fix is to make each recognizer *total over the
forms the emitter actually uses*, so the int fallback is never reached on the
`@mutable_state` path.

---

## 1. Objective & success criterion

**Objective.** For every `@mutable_state` emitter method, each of A–F is suppressed at
its recognizer, so a value's faithful type is inferred regardless of the *syntactic
form* it appears in (dotted `.get` vs subscript `["k"]` vs nested vs computed-receiver;
literal vs local vs sibling-return).

**Done =**
- the three remaining reflecting handlers (`array_set`, `tuple_unpack`,
  `critical_section`) type-check and verify with checked `assigns` frames, un-`\trusted`
  (→ **12/12** real handlers off the trusted base);
- **byte-diff 0** across the 627-file corpus (every fix is `@mutable_state`/`emit_ir`-gated);
- a **negative driver** per new capability (a deliberately-wrong string/emit_ir contract FAILS);
- **no new `\trusted`**, no new opaque `val` beyond the enumerated projections.

---

## 2. The systematic suppressors (one per leak category)

Each suppressor replaces N per-site patches with one form-complete recognizer.

### I-A — string-literal context inference (leak A)
**Rule:** a `String` literal lowers to a WhyML string (not `stable_hash`) whenever its
*sibling in the enclosing node* is string-typed — i.e. make `_is_string_expr` total over
the enclosing forms, then have those forms consult it:
- **Comparison** `LHS == "lit"` / `"lit" == RHS`: if either operand `_is_string_expr`,
  route through `str_eq_op` and emit the literal as a WhyML string.
- **Ternary** `a if c else b`: if either arm `_is_string_expr`, the whole node is string;
  emit both arms as strings (a bare `""`/`"lit"` stays a WhyML string). *(landed:
  `_handle_ifexpr_expr` string-aware path.)*
- **Default arg** `d.get(k, "lit")`: the default inherits the map's value type.

**Files:** `expressions.py` — `_is_string_expr` (the `==`/BinOp/ternary consulters),
`_handle_ifexpr_expr`, the comparison lowering (`_binop_to_whyml` / compare path).

### I-B — total string-local inference (leak B)
**Rule:** the string-local fixpoint (`_collect_str_call_result_locals`/`_is_str_val`)
must recognize EVERY string-valued first-assignment shape, so no string local is left
`ref 0`. Forms to cover (each an `_is_str_val` arm, `@mutable_state`-gated):
call to a `-> str` sibling · f-string (all-string / mixed) · ternary of strings *(landed)*
· subscript-form `emit_ir` string projection *(landed via `_is_string_expr`)* · a
`.get` on a `dict[str,str]` self-field / getattr-alias *(landed)* · a bare `str` var/field.
The fixpoint already grows the symbol table, so dependency ordering resolves.

**Files:** `statements.py` — `_collect_str_call_result_locals` / `_is_str_val`.

### I-C — sibling return-type completeness (leak C)
**Rule:** every `-> str` sibling the emitter calls has an explicit `-> str` trusted stub
in the mirror (so `_module_method_return_types` types it `string`), OR the return-type
map preserves the annotation. Audit the mirror for the closed set of string-returning
siblings (`_field_label`, `_field_type_of`, `_maybe_emit_no_exception_assert`,
`_resolve_effective_ghost_type`, `_e`, …) and declare each once.

**Files:** `src/self-annotate/src/module6_whyml/statements.py` (stubs);
`functions.py::_build_method_return_type_map` (L1 propagation).

### I-D — form-complete `emit_ir` reflection router (leak D)
**Rule:** ONE router recognizes an IR-node reflection regardless of surface form and
routes to the `emit_ir` projection. Normalize all four forms to `(recv_node, key)`:
- `node.get("k")` (dotted) · `node["k"]` (subscript) · `node.get("k", default)` (defaulted)
  · **nested / computed-receiver** `node.get("a").get("b")` and `node["a"]["b"]`.
Then map `key → projection`: string keys `{type→kind_of, name/attr→name_of, func→func_of,
value→value_of}`; sub-node keys `{value→svalue_of, object→object_of, index→sindex_of}`;
list keys `{args→(nargs_of/arg0_of), elts→(elt0_of/elt1_of)}`. Extend the ADT
(`_emit_exprir_theory`) with any missing variant/projection on demand (B-C5 Call/Subscript,
B-C6 IrTuple already landed; **add `field_of` for `node.get("field")`** — the one still
opaque as `get_field`). `_is_emit_ir_expr` must be closed under the sub-node projections
so chains type-check.

**Files:** `expressions.py` — a new `_emit_ir_reflect(node)→(recv,key)|None` unifying
`_emit_ir_args_recv_ir` + `_todict_emit_ir_projection` + the `_lower_dict_get_call`
emit_ir branch + the `_handle_subscript` projection block; `preamble.py::_emit_exprir_theory`.

### I-E — self-state map-read completeness (leak E)
**Rule:** a dict read resolves to `Map.get <the real map>` for every receiver kind the
emitter uses: body-local dict · dict/set param · `self.<field>` · **getattr-bound-local
alias** `X = getattr(self, "<field>", {})`. The alias mechanism
(`_getattr_self_dict_aliases` + `_alias_self_field`) already covers `.get` / `[k]` /
`[k]=v`; ensure `_dict_value_types`/`_dict_key_types` reads and the value-type/default
(`""` for `dict[str,str]`, `0` for `dict[str,int]`) are consistent across read, write,
and membership. *(alias landed; audit key/value-type consistency.)*

**Files:** `expressions.py` — `_lower_dict_get_call`, `_handle_subscript`, `_alias_self_field`,
`_self_field_dict_nu`; `statements.py::_handle_array_set_stmt` (the subscript-set side).

### I-F — set-membership container typing (leak F)
**Rule:** `x in c` emits `Map.get`-membership whenever `c` is any recognized set/dict
container (local / param / `self.<field>` / getattr-alias); an **undeclared** state field
that reaches `contains_check … 0` is a MISSING FIELD DECLARATION, not a modeling gap —
declare it in the mirror. Audit the mirror `@mutable_state` class for every state field
the handlers read (`_inline_array_temps`, `_array2d_params`, …) and declare each with its
faithful type.

**Files:** `expressions.py::_emit_membership`; mirror class field block.

---

## 3. Stages (each byte-diff-gated; land per-stage)

Order by leverage — the earlier stages unblock the most handlers.

- **S1 — I-D router + `field_of`** (the emit_ir reflection consolidation). *Gate:* the
  array_set 2d-branch condition `arr.get("value").get("type") == "Var"` and
  `arr.get("field")` type-check; corpus byte-diff 0; the `call-subscript-witness.py` and
  a new `nested-reflect-witness.py` verify.
- **S2 — I-A/I-B string completeness** (literal-in-context + total string-local). *Gate:*
  the array_set `code`/`pred`/`arr_e` string locals type-check (no `int_to_string`
  wrap); byte-diff 0; a `str-literal-context-witness.py` verifies + a `_fails` twin FAILS.
- **S3 — I-E/I-F self-state maps** (alias + field-decl audit). *Gate:* array_set's
  `known_sizes`/`st`/`_inline_array_temps` reads/writes/membership type-check; byte-diff 0.
- **S4 — un-`\trust` `_handle_array_set_stmt`.** With S1–S3 the body type-checks; add the
  checked `assigns` frame (the mutated state fields). *Gate:* verifies un-`\trusted`;
  self-annotation suite green (only pre-existing `errors.py` fails); byte-diff 0.
- **S5 — `tuple_unpack` + `critical_section`.** These additionally need the **list
  plumbing** (comprehension→collection, `List[τ]` field → typed list local, `.join`/
  `.append`/index) and the `whyml_ident` return decl-vs-map fix — a distinct feature set
  tracked as its own follow-on (`no-more-int-emitter-plan.md` scope). Land the shared I-A–I-F
  fixes here first, then the list feature. *Gate:* both verify un-`\trusted`; 12/12 handlers.

I-C is a prerequisite audit folded into whichever stage first needs each sibling.

---

## 4. Critical files

- `src/pycsl/module6_whyml/expressions.py` — `_is_string_expr` (811), `_handle_ifexpr_expr`,
  `_lower_dict_get_call` (2685), `_is_emit_ir_expr` (512), `_emit_ir_args_recv_ir` (570),
  `_handle_subscript`, `_emit_membership` (362), `_alias_self_field`, `_self_field_dict_nu` (707).
- `src/pycsl/module6_whyml/preamble.py` — `_emit_exprir_theory` (2718; the `emit_ir` ADT + projections).
- `src/pycsl/module6_whyml/statements.py` — `_collect_str_call_result_locals`/`_is_str_val` (1224),
  `_prescan_todict_aliases` (1466), `_handle_array_set_stmt` (455).
- `src/pycsl/module6_whyml/functions.py` — `_todict_aliases`/`_getattr_self_dict_aliases` init (197),
  `_build_method_return_type_map` (L1).
- `src/self-annotate/src/module6_whyml/statements.py` — the `@mutable_state` mirror: field
  declarations + `-> str` sibling stubs + the un-`\trust` edits.

---

## 5. Out-of-scope / soundness boundary

- **The corpus int-collapse stays.** This plan does NOT promote `list`/`dict`/`bool` to
  richer types for USER programs — only the emitter self-model (`@mutable_state`) path.
  Byte-diff 0 on the corpus is the proof.
- **No value-faithful `ensures`.** The handlers keep `ensures True`; this is type-safety +
  frame (`assigns`), not `\result == <the WhyML string>` (that needs the B3 sibling-string
  values — a separate effort).
- **List plumbing (S5) is corpus-adjacent** and larger; if a comprehension→collection
  lowering cannot be `@mutable_state`-gated cleanly, it splits into its own plan rather
  than risking a corpus byte change.
- **Every suppressor is a SOUND under-approximation:** an unmodeled reflection key →
  `IrOther ""`/`0` default (never a false value); an unrecognized container →
  the loud int type-error (never a silent wrong lowering).

---

## 6. Reference corpus (required)

Per the repo convention, add to `test-suite/corpus/pycsl-reference/` (and mirror witnesses
under `src/self-annotate/`):
- `nested-reflect-witness.py` — a `@mutable_state` method reflecting `node.get("a").get("b")`
  and `node["a"]["b"]`, asserting the projected kind.
- `str-literal-context-witness.py` (+ a `_fails` twin) — a ternary/comparison mixing a
  string sibling and a bare literal; the `_fails` twin asserts a false string equality and
  must NOT verify (non-vacuity for I-A).
- reuse `getattr-self-field-witness.py` / `self-field-dict-witness.py` for I-E/I-F.

---

## 7. Verification (the exact commands)

```bash
# per-handler type-check (fast, no proof)
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl --no-proof

# full proof (checked assigns frames)
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl

# corpus byte-diff 0 (baseline from a clean HEAD worktree, main venv, then diff)
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after_mlw
diff -rq <baseline_mlw> /tmp/after_mlw    # must be empty

# the authoritative gate
bash bin/run-self-annotation-suite.sh     # only the pre-existing errors.py may fail
```

---

## 8. Definition of done

- A–F each suppressed by a single form-complete recognizer; the int fallback is
  unreachable on the `@mutable_state` path.
- `array_set` un-`\trusted` (S4); `tuple_unpack` + `critical_section` un-`\trusted` (S5)
  → **12 real emitter handlers verify their own body-faithfulness**, the trusted base of
  reflecting-family `_handle_*` methods empty.
- Byte-diff 0; negative drivers FAIL; suite green; `typed-ir-for-b-ceiling.md` §25 worklist
  closed and this plan's leaks marked ✅.
