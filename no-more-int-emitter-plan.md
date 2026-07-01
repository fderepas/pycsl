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
| **L2** | **String-local recognizer** — a local whose first assignment is a call to a `string`-returning function is typed `string` (let-bound as a string ref, excluded from the `ref 0` int pre-decl). Builds on L1. | ✅ **DONE, byte-clean** (§2a) |
| **L2b** | **Cross-mixin-file sibling return types** — explicit `-> str` `\trusted` stubs for `_expr_to_whyml`/`_expr_to_whyml_string_ctx` (B3 siblings) in the mirror, so their `string` return type is in this module's table. | ✅ **DONE** (§2b) |
| **L3** | **F-string result locals** — a local assigned an all-string f-string is typed `string` (fixpoint recognizer). The literals already lower as WhyML strings once all parts are string (b14 B2 + L2/L2b). | ✅ **DONE, byte-clean** (§3) |
| **L4** | **String-`+` / concat self-call resolution** — `_is_string_expr` resolves a `self.<m>(…)` str-returning sibling, so `code += ";\n" + self._stmts_to_whyml(…)` routes to `str_concat_op`. | ✅ **DONE, byte-clean** (§4) |
| **L4b** | **Imported-stub param types** — Module5 preserves `param_annotations` (survives injection like `return_annotation`); the emitter merges them for `Any` params. `val whyml_ident (name: string)`. | ✅ **DONE, byte-clean** (§5) |
| **L4c** | **Remaining int-leaks in the leaf body** — list-truthiness (`if rest:` → `rest <> 0` on an `array int`); `.to_dict()` receiver loss (`stmt_index_to_dict_0 ()`); each a distinct no-more-int fix. | ◻ (chain) |
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


---

## 2a. L2 — string-local recognizer (DONE)

Added `_collect_str_call_result_locals` (`statements.py`): a local whose first
assignment is a call to a `string`-returning function (return type resolved from
`_module_method_return_types`, keyed exactly as `_handle_dotted_call` — `self.<m>`
→ `<self_type>__<m>`) is unioned into `string_vars`, so it let-binds as a string
ref instead of the `ref 0` int pre-decl.

**Measured:** byte-diff 0 across the 627-file corpus. On the B1.4 leaf, `arr =
whyml_ident(stmt.target)` now emits `let arr = ref (whyml_ident stmt.ghost…_target)`
(a `string` ref, was `ref 0`).

**Surfaced next (L2b):** `idx`/`py_val` come from `self._expr_to_whyml(…)`, defined
in the *expressions.py* mirror file, so its return type is absent from statements.py's
method table (emitted as abstract `self__expr_to_whyml_2`) and the local stays int.
Cross-mixin-file method-return-type resolution is the next layer — B1-style, but for
methods across the mirror's files. After that: L3 (string literals) and L4 (`.to_dict`).


---

## 2b. L2b — sibling return types (DONE)

`_expr_to_whyml` / `_expr_to_whyml_string_ctx` live in the `ExpressionEmissionMixin`
file; `StatementEmissionMixin` composes with it at runtime but does not inherit it
here, so verifying `statements.py` alone left their return type unknown (abstract
`self__expr_to_whyml_2 : int`). Added explicit `	rusted`, `-> str` stub
declarations for them in the mirror (the B3 "trusted sibling" pattern made
explicit — faithful, since the real siblings do return `str`).

**Result:** `idx`/`py_val` (from `self._expr_to_whyml(...)`) now emit `let … = ref
(self__expr_to_whyml_2 …)` as **string** refs. Mirror-only change → corpus byte-diff
0. Next surface: `code` (the f-string) is still `ref 0` and its `str_concat`
receives int-hashed literals → **L3**.


---

## 3. L3 — f-string result locals (DONE)

Once L1/L2/L2b type the interpolated locals as string, an all-string f-string
already lowers to `str_concat_op` over real string literals (b14 B2) — the literal
int-hash (`465640005`) is gone. What remained: the *receiving* local (`code = f"…"`)
was still `ref 0`. Generalized the string-local recognizer to a **fixpoint** that
also marks a local first-assigned an all-string f-string (handling `FString`
directly, without touching the widely-used `_is_string_expr`); the fixpoint marks
`arr`/`idx` (L2 calls) first, then `code` (the f-string over them). Byte-diff 0.

**Result:** all four leaf locals (`arr`, `idx`, `py_val`, `code`) are string refs.
Next surface (L4): the `if rest` branch `code := !code + (";\n" + self._stmts_to_whyml(…))`
lowers `+` as int add because `_is_string_expr` doesn't resolve the *self-call*
`self._stmts_to_whyml(…)` (the `_module_method_return_annotations` map isn't keyed
for `self.<m>`) — the string-`+`/concat routing then misses.


---

## 4. L4 — string-`+` self-call resolution (DONE)

The rest-branch `code += ";\n" + self._stmts_to_whyml(…)` lowered `+` as int add
because `_is_string_expr`'s `Call` branch looked up `_module_method_return_
annotations` by the raw func name — a `self.<m>` call missed the class-qualified
key. Resolved self-calls to `<self_type>__<m>` (as `_handle_dotted_call` /the L2
recognizer do). Now the rest-branch emits `str_concat_op !code (str_concat_op ";\n"
(self__stmts_to_whyml_5 …))`. Byte-diff 0.

**Next surface (L4b):** `let arr = ref (whyml_ident stmt.ghostarraysetstmt_target)`
fails — the field is `string` but `val whyml_ident (name: int)` types the param int.
Imported/trusted-stub PARAM annotations aren't propagated (L1 did returns only);
`whyml_ident(name: str)` should emit `(name: string)`. That is the next layer.


---

## 5. L4b — imported-stub param types (DONE)

`whyml_ident(name: str)` emitted `val whyml_ident (name: int)` while the field arg
is `string`. The imported stub's `symbol_table` is rebuilt with `Any` params by the
injection (losing `name: str`). Fix mirrors `return_annotation`: Module5 now emits a
`param_annotations` field (from the same `arg_type` it computes), which survives
injection; `_reset_function_state` merges it into the symbol table for `Any`/missing
params only (copy-on-write, never overriding a resolved type). Also fixed the L2b
sibling stubs' `local_refs` param to `Set[str]` (was `int`) to match the callers.
Byte-diff 0.

**Result:** `val whyml_ident (name: string) : string`. The leaf now typechecks
through the string locals + concat + field access + param types.

### The honest remaining chain to L5
The leaf still does not close — each fix exposes the NEXT int-leak, because the
emitter body is pervasively int-modelled:
- **list truthiness**: `if rest:` lowers to `rest <> 0` (an `array int` vs `int`);
  needs `Array.length rest <> 0` (a list-truthiness fix).
- **`.to_dict()` receiver loss**: `stmt.index.to_dict()` → nullary
  `stmt_index_to_dict_0 ()` (drops the receiver) — a faithfulness gap.
- likely further leaks below these.

Each is a distinct, byte-diff-sensitive no-more-int layer. **Closing one leaf is a
multi-layer chain** — the no-more-int doctrine's "long-term / EXTREME RIGOR" is
literal here. Landed so far: B1.4 field-access + L1/L2/L2b/L3/L4/L4b (7 byte-clean
layers). L5 (leaf verifies) remains gated on the L4c chain.
