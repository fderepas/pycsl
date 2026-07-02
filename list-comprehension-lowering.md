# list-comprehension-lowering.md — the list/string plumbing to un-`\trust` the final two handlers

**Doctrine:** [no-more-int] for the emitter's OWN list/string plumbing. The last two
reflecting-family `_handle_*` handlers — `_handle_tuple_unpack_stmt` and
`_handle_critical_section_stmt` — manipulate lists (comprehensions, `.join`, list-repeat,
index, `.append`) and build strings. Their bodies currently type-error because a list
comprehension lowers to an opaque `val list_comp (x:int):int` and the string-list ops
collapse to `int`. This plan lowers each to its faithful WhyML type.

**Sub-plan of** `i-feel-good.md` §10 (the S5 tail). Companion to `typed-ir-for-b-ceiling.md`
(10 handlers landed) — this closes the remaining two (→ **12/12**).

**Feature-vs-refactor:** FEATURE (changes emitted WhyML) but **byte-clean by construction** —
every lowering is gated on `@mutable_state` (the emitter self-model), which the 627-file
corpus has none of. Gate: **byte-diff 0 across the corpus** + the handler type-checks + a
checked `assigns` frame + non-vacuity.

---

## 0. The verdict — what these two handlers need (measured, from the un-`\trust` probes)

`tuple_unpack` blockers, in body order:
```
targets = stmt.targets                              # L0 ✅ list-local-from-field (i-feel-good S5)
safe_targets = [whyml_ident(t) for t in targets]    # L1 comprehension → array string
if arity_fn in self._abstract_ops:                  # L5 _abstract_ops as Dict[str,str]
    tuple_ret = "(" + ", ".join(["int"]*len(targets)) + ")"  # L3 list-repeat, L2 join, L4 string-+
    self._abstract_ops[arity_fn] = f"..."           # L5 dict subscript-set
tmp_names = [f"_tu_{t}" for t in safe_targets]       # L1 comprehension → array string
pattern = ", ".join(tmp_names)                       # L2 join → string
lines = [f"..."]                                     # (list literal → Seq, already works)
while i_tu < n_tu: tmp = tmp_names[i_tu]; …           # L6 index/len on array string
    lines.append(...)                                # L6 append
```
`critical_section` additionally needs:
```
shared_for_mutex = [sv["name"] for sv in self.ir.get("shared_vars", []) if sv.get("mutex")==mutex]
                                                     # L8 self.ir list-of-dicts reflection + FILTERED comprehension
safe_var = whyml_ident(var)  # in a for-loop         # L8 whyml_ident return decl-vs-map
self._havoc_counter += 1                             # L8 scalar frame
[s.to_dict() for s in body_stmts]                    # L1 comprehension (emit_ir elements)
```

### The model — an abstract element-typed array with a length law (sound, bounded)
A comprehension's *content* is not needed for the `ensures True` + frame contracts these
handlers carry; only its **type** and **length** matter (the `while i < len` bound). Model:

```whyml
val list_comp_string (src: array 'a) : array string
  ensures { Array.length result = Array.length src }        (* no filter: bijective *)
val list_comp_string_filt (src: array 'a) : array string
  ensures { Array.length result <= Array.length src }       (* with `if`: sub-selection *)
```

- **Element type** from `_is_string_expr(elt)` (string) / `_is_emit_ir_expr(elt)` (`emit_ir`)
  / else `int`. A `[… for … in src]` over a typed `src` array carries the length law
  (exact without an `if`, `≤` with). Content is honestly unmodeled — the faithful
  under-approximation, never a false element claim (mirrors `str_repr_op`, `str_split_elem_op`).
- **Sound:** the length law is universally true; the opaque content forbids proving any
  false postcondition about the produced list.

---

## 1. Objective & success criterion

**Done =**
- `_handle_tuple_unpack_stmt` and `_handle_critical_section_stmt` type-check and verify with
  checked `assigns` frames, un-`\trusted` (→ **12 real emitter handlers** off the trusted base);
- **byte-diff 0** across the 627-corpus (every lowering `@mutable_state`-gated);
- a **negative driver** per new op (a false length/element claim FAILS);
- no new `\trusted`; the new `val`s carry only sound length laws.

---

## 2. Stages (each byte-diff-gated; land per-stage)

- **L1 — comprehension → element-typed array** (the crux). `ListCompExpr` → `list_comp_<τ>`
  (`string`/`emit_ir`/`int`) with the length law; the filtered form (`generators[*].ifs`
  non-empty) → the `_filt` variant (`≤`). `_is_string_expr`/`_is_emit_ir_expr`/`_typed_local_vars`
  recognize a comprehension-bound local as an array of the element type. *Gate:* a witness
  `list-comp-witness.py` — `[f(t) for t in xs]` binds an `array string`, `len` + `[i]`
  type-check; corpus byte-diff 0.
- **L2 — `join` on a string-list → `string`.** `sep.join(<array string>)` → a new
  `val str_join_arr (sep: string) (xs: array string) : string` with
  `ensures { String.length result >= 0 }` (a general-iterable join; the literal-list join
  from `faithful-string-op.md` §3.5 stays exact). *Gate:* `", ".join(safe)` is `string`.
- **L3 — list-repeat `["x"] * n` → array.** `[<elt>] * <int>` → `Array.make <n> <elt>` at the
  element type (the elt's `_is_string_expr` decides `array string` vs `array int`). *Gate:*
  `["int"] * len(targets)` is `array string`.
- **L4 — string-`+` in `@mutable_state`.** `"(" + s + ")"` routes to `str_concat_op` when
  either operand is string (the I-A comparison analogue for `+`, @mutable_state-gated).
- **L5 — `_abstract_ops` as `Dict[str,str]`.** Declare the mirror field; `k in`/`[k]`/`[k]=v`
  route via the I-E/I-F self-dict machinery (already built). Add to the handler's `assigns`.
- **L6 — list index / `len` / `.append` on a string array.** `xs[i]` → `xs[i]` (string),
  `len(xs)` → `Array.length`, `xs.append(v)` → the growable-list `_len` model at `array string`.
- **L7 — un-`\trust` `_handle_tuple_unpack_stmt`** with its checked `assigns` frame.
- **L8 — `_handle_critical_section_stmt`.** The `self.ir.get("shared_vars")` list-of-dicts
  reflection + filtered comprehension (L1 `_filt`), the `whyml_ident` return decl-vs-map fix,
  and the `_havoc_counter += 1` scalar frame; then un-`\trust`.

L1 gates L2–L6 (they operate on the array L1 produces). L7 needs L1–L6; L8 needs L1 + its own.

---

## 3. Critical files

- `src/pycsl/module6_whyml/expressions.py` — the `ListCompExpr`/`SetCompExpr` dispatch
  (~4285), `_is_string_expr` / `_is_emit_ir_expr` (comprehension recognition), `_handle_binop`
  (list-repeat `*`, string-`+`), the `.join` recognizer, `_handle_subscript` (index).
- `src/pycsl/module6_whyml/preamble.py` — the new `list_comp_<τ>` / `str_join_arr` `val`s.
- `src/pycsl/module6_whyml/statements.py` — `_typed_local_vars` / the string-local &
  array-local collectors (a comprehension-bound local); `_handle_critical_section_stmt` frame.
- `src/pycsl/module6_whyml/types.py` — comprehension array-var recognition.
- `src/self-annotate/src/module6_whyml/statements.py` — `_abstract_ops: Dict[str,str]` field,
  the two un-`\trust` edits + `assigns` frames.

---

## 4. Out-of-scope / soundness boundary

- **Content is never modeled.** The comprehension/join ops carry LENGTH laws only — a
  postcondition about the produced list's ELEMENTS is honestly unprovable (the faithful
  under-approximation, not a trusted lie). These handlers carry `ensures True`, so this is
  type-safety + frame, not value-faithful.
- **Corpus int-model untouched.** Every lowering is `@mutable_state`-gated; byte-diff 0 is the proof.
- **General-iterable `.join` (L2)** gets only `length ≥ 0`; the exact literal-list join stays
  in `faithful-string-op.md`. A caller needing an exact join length over a variable list is
  out of scope.
- **A filtered comprehension** weakens the length law to `≤` (sound); an unfiltered one is `=`.

---

## 5. Reference corpus (required)

Add to `test-suite/corpus/pycsl-reference/` + mirror witnesses under `src/self-annotate/`:
- `list-comp-witness.py` — `[f(t) for t in xs]` binds an `array string`; `len`/`[i]` type-check.
- `list-comp-len_proves.py` (+ `_fails` twin) — proves `len([x for x in xs]) == len(xs)` (no
  filter); the `_fails` twin asserts `== len(xs) + 1` and must NOT verify (non-vacuity for L1).
- `str-join-arr_proves.py` — `len(",".join(xs)) >= 0` proves; a false `== 0` twin FAILS.

---

## 6. Verification (exact commands)

```bash
# per-handler type-check
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl --no-proof
# full proof (checked frames)
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl
# corpus byte-diff 0 (baseline from a clean HEAD worktree)
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <baseline> /tmp/after
bash bin/run-self-annotation-suite.sh    # only pre-existing errors.py may fail
```

---

## 7. Definition of done

- L1–L8 landed; comprehensions/join/list-repeat/index/append lower to element-typed arrays
  and strings; `tuple_unpack` + `critical_section` un-`\trusted`.
- **12 real emitter handlers verify their own body-faithfulness** — the reflecting-family
  trusted base empty.
- Byte-diff 0; negative drivers FAIL; suite green; `i-feel-good.md` §10 tail closed.

---

## 8. Execution log

**L1–L7 COMPLETE — `_handle_tuple_unpack_stmt` un-`\trusted` (the 11th handler).** Byte-diff 0
across the 627-corpus; self-annotation suite unchanged (only pre-existing `errors.py`). Landed:
- **L1** comprehension → `list_comp_<τ>` (string/emit_ir/int) with the length law
  (`=`/`≤`); comprehension-bound local is an array local; `_array_elem_types` tracks the
  element type (computed BEFORE the string-local collectors).
- **L2** `sep.join(<string-array>)` → `str_join_arr` (`string`); fires before the int
  `is_array` path; recognized in `_is_string_expr`. **+ seq variant** `str_join_seq` for a
  `.append`-grown string list (`lines`).
- **L3** list-repeat `["x"] * n` → `Array.make n "x"` (already worked once the element is string).
- **L4** string-`+` via the string-join recognition in `_is_string_expr`.
- **L5** `_abstract_ops: Dict[str,str]`; `map_update_some` POLYMORPHIC in a @mutable_state
  module (one decl unifies with string-valued dict fields); self-field dict-read default per ν
  (`""`); self-field dict[str,str] subscript read recognized as string.
- **L6** list index / `len` on a string array (`safe_targets[i]`, `len(tmp_names)`).
- **L7** `re.findall(pat, s)` → `array string` (string args, modeled before arg-coercion);
  `_handle_tuple_unpack_stmt` un-`\trusted` with `assigns self._abstract_ops` **plus loop
  invariants** (`0 <= i_tu`, `n_tu == len(tmp_names)`, `len(safe_targets) == len(tmp_names)`
  — the last two from the `list_comp` length law) so the `xs[i_tu]` array-bounds VCs discharge.

**11 of 12 reflecting-family emitter handlers now verify their own body-faithfulness.**

**L8 — `_handle_critical_section_stmt` — the honest wall (a DISTINCT, harder problem).** Its
first blocker is `shared_for_mutex = [sv["name"] for sv in self.ir.get("shared_vars", []) if
sv.get("mutex") == mutex]` — deep reflection on `self.ir`, the transpiler's **untyped nested
input IR** (`Dict[str, Any]`, a list-of-dicts). The comprehension's element `sv["name"]` and
filter `sv.get("mutex")` reflect on an opaque dict ELEMENT whose type the list-comp machinery
(L1) cannot infer — sv is bound to elements of an untyped list, so `sv["name"]` is not
recognized as a string and the whole comprehension collapses to `array int`. This is NOT the
typed-collection plumbing L1–L7 solved; it is **heterogeneous untyped-`Dict[str,Any]`
reflection over `self.ir`** — the same class of problem as the original Ceiling A (the
reflective dict), resurfacing for the transpiler's *input* structure rather than its *output*.
Modeling it soundly needs either a typed `self.ir` schema (a large front-end feature) or an
audited abstract-array model of `self.ir.get(<key>)` with string-typed element projection — its
own sub-plan. critical_section additionally needs the `whyml_ident` return decl-vs-map fix and
the `_havoc_counter += 1` scalar frame, both bounded, but the `self.ir` reflection gates it.

**Net:** L1–L7 delivered the complete list/string plumbing (11th handler); L8 is deferred as a
distinct `self.ir`-reflection sub-problem, precisely scoped.
