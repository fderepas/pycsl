# no-more-int-emitter-plan.md — type the emitter's string values as `string`, not `int`

> **Purpose.** The campaign to make a `_handle_*` emitter method **body-faithful**
> (the standing goal of `b1-plan.md §12` / `semantic-ceiling-plan.md`). B1 closed
> the type-opacity wall (imported IR records resolve; `b1-plan.md §11` fixed
> ambiguous-field access). What remains is **modeling**: the emitter's own
> string-valued expressions are lowered as `int` (the legacy hash model), so a
> checked body fails L3 typecheck (`string, but expected int`). This plan flips the
> emitter's string handling to real WhyML `string`, one gated layer at a time.
>
> **Gate.** Byte-identical on the 627-file corpus wherever achievable (each layer
> below is *measured* — several are byte-clean because the corpus doesn't exercise
> the flipped path); when a layer must change corpus bytes, the gate becomes
> **"every corpus file still proves Valid"** + intended-diff review. Never both
> broken.
>
> **Scope.** The emitter (self-annotate mirror) path, not user-facing string
> features. Related but distinct: `a2-a3-plan.md` A2 (string-op *content* models);
> this plan is the *typing/plumbing* so string values flow as `string`.

---

## 0. The layers (each is one gated step)

Measured on `_handle_ghost_array_set_stmt` (the B1.4 leaf), whose checked body needs
all of these:

| L | Layer | State |
|---|---|---|
| **L1** | **`-> str` function return-type propagation** — `_build_method_return_type_map` records a `str`-annotated function as WhyML `string` (was: only list/set/dict overridden; `str` fell through to the int-hash default). | ✅ **DONE, byte-clean** (§1) |
| **L2** | **String-local recognizer** — a local whose first assignment is a call to a `string`-returning function is typed `string` (let-bound as a string ref, excluded from the `ref 0` int pre-decl). Builds on L1. | ▶ next |
| **L3** | **String literals in f-strings** — `f"{a}[{i}]"`'s literal chunks (`"["`) lower as WhyML string literals, not int hashes (`465640005`); `str_concat` over all-string operands. | ◻ |
| **L4** | **Sub-field `.to_dict()` receiver** — `stmt.index.to_dict()` must keep its receiver (currently drops to a nullary `stmt_index_to_dict_0 ()`). | ◻ |
| **L5** | **Close B1.4** — the leaf verifies body-faithful (`ensures \result == …`) once L1–L4 land; then scale to more handlers. | ◻ |

Dependency: L2 needs L1; L5 needs L1–L4. L3/L4 are independent. A method that
also does string *content* ops (`.replace`/`.split`) additionally needs
`a2-a3-plan.md` A2 — out of scope here (those handlers stay `\trusted`, enumerated).

---

## 1. L1 — return-type propagation (DONE)

`_build_method_return_type_map` (`functions.py`) overrode the body-inferred return
type from the annotation only for `list`/`set`/`dict`/`frozenset`; a `-> str`
function kept the int-hash default (`find_return_type` returns `int` for a
`return "…"` body — the legacy string-as-int model). Added the `str → "string"`
case.

**Measured results:**
- **Byte-diff 0** across the 627-file corpus — the 30 corpus files with `-> str`
  functions do not consult this map on a byte-affecting path, so the flip is inert
  there. (Green light: L1 is safe now, without waiting on the corpus migration.)
- The mirror's `_module_method_return_types` now types `whyml_ident`, `op_translate`,
  `safe_exc_name`, and the emitter's own `-> str` methods (`_handle_assign_stmt`,
  `_emit_first_assign`, …) as `string` — exactly the callees whose results feed the
  emitter's string locals. This is the foundation L2 builds on.

---

## 2. Sequencing & method

Leaf-first, one layer per PR, each byte-diff-gated (or Valid-gated where a diff is
intended). After each layer, re-check `_handle_ghost_array_set_stmt` to see the
next failure surface (the layers were discovered exactly this way). Stop and
enumerate honestly whenever a layer would ripple the corpus without A2.

**Non-goals:** string *content* semantics (A2); the full corpus int→string
migration (a separate, larger effort — this plan only flips the *emitter* path and
stays byte-clean on the corpus where it can).
