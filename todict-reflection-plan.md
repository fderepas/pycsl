# todict-reflection-plan.md — dissolve the emitter's `.to_dict()`/dict-reflection

> **Purpose.** The last `no-more-int-emitter-plan.md §7` wall to un-`\trusting` a
> state-mutating emitter handler: its body **reflects on IR dicts** —
> `arr = stmt.X.to_dict(); arr.get("type") == "Var"`. `.to_dict()` lowers to an
> opaque map (receiver lost), and `.get(key)` on a **heterogeneous** `Dict[str,Any]`
> (str for `"type"`, a node for `"value"`, a list for `"elts"`) has no model.
>
> **Key finding (this is NOT irreducible / Ceiling B).** The reflected structure is
> already present in the **typed IR** (Phase A/B: `stmt.X` is a typed `ExprIR` with
> a `kind` tag and typed fields). So the wall dissolves by **routing** the
> reflection to typed field access instead of modeling a heterogeneous dict:
> `node.to_dict().get("type")` → `node.kind`; `node.to_dict().get("value")` →
> `node.value`. No `Dict[str,Any]` variant-value model is needed — each `.get(key)`
> becomes the typed field, whose own type handles the heterogeneity.

---

## 0. Grounding (measured)

- **Current lowering** (`refl.py` probe): `d = n.to_dict()` → `d = ref 0` (int
  local) `:= n_to_dict_0 ()` (a **receiver-less** abstract map stub); `d.get("type")`
  → `d_get_1 (int)` (abstract, int-hashed key). The heterogeneous `.get` cannot
  typecheck (`type string, but expected int`).
- **Infra already present** for the recognizer route:
  `_recognize_field_decode_idiom` (an established idiom-recognizer pattern),
  `_lower_dict_get_call` (`.get` → `match Map.get …`), and
  `_record_types[cls]["field_types"]` (the node's key→type schema).
- **The reflection reduces to two bounded pieces**, confirmed by rewriting the
  target to typed access (`refl.py` → `n.kind`): it then fails only on **no-more-int
  str-field handling** (`n.kind == "Var"` int-hashed), not a new dict problem.

---

## 1. The two sub-problems

| | Piece | Nature |
|---|---|---|
| **R1** | **Reflection-idiom recognizer** — track `d = node.to_dict()` as a *typed-node alias*; lower `d.get(key)` to `node.<field-for-key>` (`"type"` → the kind tag; other keys → same-named fields, via the `field_types` schema). Eliminates the dict. | bounded emitter feature (reuses the idiom-recognizer + schema infra) |
| **R2** | **no-more-int on the routed typed access** — the resulting `node.<field>` reads/compares hit the same str/list/etc. int-leaks as the L1–L4c chain. | the existing no-more-int toolbox |

**R1 dissolves the heterogeneity** (each key routes to its own typed field); **R2**
is the familiar chain. Neither is metacircular/irreducible.

---

## 2. Progress — R2 str-field comparison (DONE, byte-clean)

`_is_string_expr` now recognizes a record's `str`-typed **field** read (`n.kind`)
— self/global/record-var via `_field_type_of`, and a record-typed **param/local**
via the symbol table + the record's `field_types`. So `n.kind == "Var"` routes to
`str_eq_op` (was the int-hash mismatch). Witness
`src/self-annotate/todict-reflection-witnesses.py` verifies; **byte-diff 0** across
the 627-file corpus (only genuine str-field reads are affected; unknown/non-str
fields keep the opaque path).

This is the first R2 fix and the validation that the **typed-access target** the
recognizer produces is sound.

---

## 3. Work items

| WI | Item | Gate |
|---|---|---|
| **R2.a** | str-field comparison → `str_eq_op` | ✅ DONE (§2) |
| **R1.1** | Recognize `d = <typed-node>.to_dict()`; track the alias; no-op the assign. | ✅ **DONE, byte-clean** (§7) |
| **R1.2** | Lower `d.get(key)` for an aliased `d` to `node.<field>` (`_todict_routed_ir`); `_is_string_expr` routes an alias-get too so the str-eq path fires. | ✅ **DONE, byte-clean** (§7) |
| **R1.3** | The value flows: `d.get("value")` yields the typed sub-node (feeds `_expr_to_whyml`); `d.get("elts")` yields the list. | typed sub-node access works |
| **R2.b** | Remaining no-more-int on routed reads (list `.get`, nested `.get`, etc.) — as they surface, per the L1–L4c toolbox. | each byte-gated |
| **R3** | Apply to a real reflecting mirror handler (e.g. `_handle_array_set_stmt`) with the A3 frame — the first state-mutating handler un-`\trusted`. | handler verifies |

---

## 4. Gate criteria

1. **Byte-identical** on the 627-file sweep at every step — the recognizer fires on
   the emitter/reflection path; corpus drivers don't reflect on IR dicts.
2. **Reflection witnesses** verify (str/node/list keys routed to typed fields).
3. **No heterogeneous-dict axiom** — the dict is *dissolved*, not modeled; residual
   trust unchanged.

---

## 5. Non-goals / honest boundaries

- **Not** a faithful heterogeneous `Dict[str,Any]` model — the recognizer bypasses
  it. (A general Any-typed dict *would* need a variant value type; the point is we
  don't need it, because the typed IR carries the structure.)
- **Not** a rewrite of the mirror handlers to typed style — R1 recognizes the
  `.to_dict().get()` idiom *as written* and routes it; the handler source is
  unchanged (like the other recognizers).
- A handler reflecting in a way the recognizer doesn't cover stays `\trusted`,
  enumerated.

---

## 6. Why this closes the §7 picture

`no-more-int-emitter-plan.md §7` named two walls for the state-mutating handlers:
A3 (frame) and this (`.to_dict()`/reflection). **A3 is proven** (`a3-plan.md §11`);
this plan shows the reflection wall is **bounded** (recognizer + no-more-int, not
Ceiling B) and lands its first piece byte-clean. Together they reduce
"un-`\trust` a real state-mutating handler" to the enumerated R1/R2/R3 work — a
finite, gated feature, no longer an open ceiling.


---

## 7. R1 BUILT (2026-07-01) — the reflection recognizer, byte-clean

`d = node.to_dict()` is recognized (`statements._handle_assign_stmt`): the target is
recorded in `self._todict_aliases` (→ the receiver dotted-name) and the assign emits
NOTHING — `d` is never a real value. Every `d.get(key)` then routes to the node's
TYPED field via `_todict_routed_ir` (`"type"` → `node.kind`; other keys → `node.<key>`),
in BOTH `_lower_dict_get_call` (the value) and `_is_string_expr` (so the binop str-eq
path fires). The heterogeneous `Dict[str,Any]` is **never materialized** — each key
resolves to its own typed field.

**Verified** (`src/self-annotate/todict-r1-witnesses.py`): `d = n.to_dict();
d.get("type") == "Var"` lowers to `if (str_eq_op n.kind "Var")` and proves; multi-key
(`d.get("type") == "Var"` / `== "Const"`) proves. **Byte-diff 0** across the 627-file
corpus (fires only on a literal `.to_dict()`/`.get()` reflection, which no corpus
driver has).

**Status.** R1.1 ✅ · R1.2 ✅ · R2.a ✅ (str-field, PR #119). Remaining: R1.3
(`d.get("value")` yielding a typed SUB-NODE that feeds `_expr_to_whyml` — the witness
covers str keys; node/list-valued keys are the next slice), R2.b (no-more-int on
routed non-str reads), R3 (a real reflecting mirror handler with the A3 frame). The
reflection wall is now a working recognizer, not an open ceiling.

---

## 8. R3 — R1 + A3 COMPOSE (2026-07-01); the real-handler tail characterized

**The integration is PROVEN.** `src/self-annotate/r3-integration-witness.py` (verifies):
a single un-`\trusted` handler that **reflects** (`d = stmt.to_dict();
d.get("type") == "Var"` → `str_eq_op stmt.kind "Var"`; `d.get("target")` →
`stmt.target`) **and mutates transpiler state** (`self.dict_locals.add(…)` → a real
map write; `self.add_abstract_op(…)` inherited) verifies with a **CHECKED composed
frame** `writes { self.dict_locals, self.abstract_ops }`. R1 (reflection→typed) and
A3 (state frame) compose automatically — the R1 recognizer feeds the A3 set-field
`.add` in one line (`self.dict_locals.add(d.get("target"))`). No trust; a wrong
`assigns` FAILS.

This is the R3 essence: a reflecting + state-mutating handler verified with a proven
frame, integrating B1 + the string chain + R1 + A3.

**The real-mirror-handler tail (honest).** Un-`\trusting` an *actual* mirror handler
(e.g. `_handle_fieldassign_stmt`) additionally needs, per handler:
1. **Mirror class `@mutable_state` + declared state fields** — `StatementEmissionMixin`
   is a mixin, not a `@dataclass`; giving it the A3 model is a structural mirror
   change (declare the ~15 state fields).
2. **R1.3** — node/list-*valued* `d.get(key)` feeding `_expr_to_whyml` (the witness
   covers str-valued keys; the real handlers also read sub-nodes).
3. **A per-handler no-more-int pass** — each 300–700-line handler carries its own
   residual str/int leaks (e.g. a `string, but expected int` surfaced in
   `_handle_fieldassign_stmt`), the L1–L4c toolbox applied case-by-case.

None is a new ceiling; each is enumerated, bounded, gated. R3-proper is the
per-handler integration on top of the proven composition — a focused campaign, not
an open question.

**Net.** Every wall of the body-faithful-emitter arc is knocked down or reduced to
bounded, gated follow-on: B1 (typing) ✅, field-access ✅, string chain ✅, first
un-`\trusted` leaf ✅, mutable-self/soundness ✅, A3 frame ✅, R1 reflection ✅, and
**R1+A3 composition ✅**. "Un-`\trust` a real state-mutating reflecting handler" is
now the enumerated (mirror-`@mutable_state` + R1.3 + per-handler no-more-int)
integration on proven foundations.

---

## 9. R1 var-substitution + R3-proper status (2026-07-01)

**R1 var-substitution (DONE, byte-clean).** `d = node.to_dict()` now binds `d` as a
FULL alias: besides `d.get(key)` → `node.<field>`, a bare `d` reference lowers to
the node itself (`_handle_var_expr`). So the pervasive emitter idiom
`d = sub.to_dict(); self._expr_to_whyml(d)` (the recursive sub-expression emission)
routes `d` → the typed sub-node instead of the opaque `unit` to_dict. Byte-diff 0;
witness `src/self-annotate/todict-varsubst-witness.py` verifies.

**R3-proper — measured status on a REAL handler.** Un-`\trusting`
`_handle_array_slice_set_stmt` (with the mirror class marked `@mutable_state
@dataclass` + `_slice_set_tmp_counter` declared) now emits:
- `writes { self._slice_set_tmp_counter }` — the **A3 frame** ✓;
- `dst = self._expr_to_whyml(stmt.arrayslicesetstmt_array …)` — the **R1
  var-substitution** routed the bound to_dict alias to the typed field ✓.

The mirror class `@mutable_state @dataclass` restructuring is **viable** (the mirror
still verifies with all other handlers trusted). The remaining gap is a **per-handler
string-local typing** issue (`dst = ref 0` int vs the string `_expr_to_whyml` result
— the L2 chain applied to THIS handler's locals), not reflection or frame.

**So R3-proper reduces to:** mirror `@mutable_state` (viable) + A3 frame (works) +
R1 reflection/var-substitution (built) + a per-handler no-more-int pass (string-local
typing for the handler's `dst`/`src`/… locals — the L1–L4c toolbox, case-by-case).
Every piece is proven/viable; closing one real handler is the enumerated per-handler
finish, not an open ceiling.

---

## 10. Mixed str/int f-string (DONE, byte-clean); R3-proper down to conditional string-local pre-decl

**Mixed str/int f-string → string (R3, byte-clean).** In a `@mutable_state` class a
MIXED f-string (a gensym `f"__x_{n}"`, an int counter interpolated) is now a STRING:
`_handle_fstring_expr` converts each int segment via `int_to_string` and concats;
the string-local recognizer marks the receiving local string too. Witness
`src/self-annotate/mixed-fstring-witness.py` verifies; byte-diff 0 (gated on
`@mutable_state`). This closes the emitter's gensym locals (e.g.
`_handle_array_slice_set_stmt`'s `src_var`, `prologue`).

**R3-proper — `_handle_array_slice_set_stmt` remaining gap (measured).** With the
mirror class `@mutable_state @dataclass` + `_slice_set_tmp_counter` declared, the
handler now type-checks its A3 frame, R1 var-substitution, and every string local
(`dst`/`src`/`lo`/`src_var`/`prologue`) — down to ONE gap: `hi`, assigned in BOTH
branches of `if stmt.upper is not None: … else: …` and used after, is let-bound
per-branch (out of scope). A string local first-assigned inside branches needs a
**string pre-declaration** (`ref ""` before the `if`) — the string analogue of the
int `ref 0` pre-decl. That is a bounded emitter fix (conditional string-local
pre-decl), and the handler's last blocker.

**R3-proper status:** mirror `@mutable_state` (viable) ✅ + A3 frame ✅ + R1
reflection/var-subst ✅ + string-local typing (calls, f-strings, mixed f-strings) ✅
→ remaining: conditional string-local pre-declaration. One bounded fix from the
first real state-mutating emitter handler un-`\trusted`.

---

## 11. Conditional string-local pre-decl (DONE, byte-clean)

A string local first-assigned inside BOTH branches of a conditional now
PRE-DECLARES `ref ""` before the branch (the string analogue of the int `ref 0`
pre-decl), in a `@mutable_state` method — so it stays in scope after the branch,
instead of being let-bound per-branch (out of scope). Witness
`src/self-annotate/conditional-strlocal-witness.py` verifies; byte-diff 0 (gated on
`@mutable_state`). This is the `hi` idiom in `_handle_array_slice_set_stmt`
(`if stmt.upper is not None: hi = <str call> else: hi = f"…"`).

**R3-proper — cumulative status.** Every structural/typing piece for the first real
state-mutating emitter handler is now built and byte-clean: mirror
`@mutable_state @dataclass` (viable) · A3 frame · R1 reflection + var-substitution ·
string-local typing (calls, f-strings, **mixed str/int f-strings**, **conditional
string locals**). What remains for `_handle_array_slice_set_stmt` is the residual
per-handler no-more-int tail — each surfaced gap byte-clean-fixable with the L1–L4c
toolbox, discovered one at a time. The building blocks are all proven; closing this
handler is the enumerated per-handler finish, converging.

---

## 12. R3-PROPER DONE (2026-07-01) — the first REAL state-mutating handler un-`\trusted`

**`_handle_array_slice_set_stmt` is no longer `\trusted` — it verifies with a checked
body.** `statements.py` PASSES the self-annotation suite with it un-`\trusted` (only
the pre-existing, unrelated `errors.py` fails). This is the FIRST real emitter handler
that MUTATES transpiler state removed from the trusted base — the culmination of the
whole body-faithful-emitter arc.

**What composed** (every piece proven earlier, integrated here):
- **B1** — typed imported IR param (`stmt: arrayslicesetstmt`, via `--import-path`);
- **field access** — `stmt.arrayslicesetstmt_array` (ambiguous-field qualification);
- **R1 var-substitution** — `arr = stmt.array.to_dict(); self._expr_to_whyml(arr)` →
  `self._expr_to_whyml(stmt.array)` (the recursive sub-expression emission);
- **string-local typing** — `dst`/`src`/`lo`/`hi` (str-returning calls, f-strings);
  the gensym `src_var` (**mixed str/int f-string** → `int_to_string`); `prologue`;
  the conditional `hi` (**string pre-decl** `ref ""`); `code +=` on an f-string
  (**FString in `_is_string_expr`**);
- **A3 / mutable-self** — mirror class `@mutable_state @dataclass`,
  `#@ assigns self._slice_set_tmp_counter` emitted as a CHECKED `writes { … }`.

The last tool gap (this PR): `_is_string_expr` recognizes an f-string as string in a
`@mutable_state` class, so `code += f"…"` routes to `str_concat_op`. Byte-diff 0.

**Contract proven:** `requires True / ensures True / assigns
self._slice_set_tmp_counter` on a CHECKED body — type-safety + frame (not yet the
value-faithful `ensures \result == …`, which needs the B3 sibling string values).
But the handler is no longer a black-box stub, and it MUTATES state with a proven
frame.

**Net.** The body-faithful-emitter track — blocked for the project's history, feared
metacircular — has un-`\trusted` its first real reflecting-family, state-mutating
handler. Scaling to the rest is the same per-handler recipe (B1 + R1 + string chain +
A3), each a bounded gated pass on now-proven foundations.

---

## 13. SCALED — a THIRD real handler un-`\trusted` (`_handle_fieldassign_stmt`)

`_handle_fieldassign_stmt` is no longer `\trusted` — it verifies (`assigns \nothing`);
`statements.py` PASSES the suite with BOTH it and `_handle_array_slice_set_stmt`
un-`\trusted` (only the pre-existing `errors.py` fails). Third real emitter handler off
the trusted base, confirming the R3 recipe scales.

**The per-handler recipe applied** (mirror-side, in the `@mutable_state` class):
- declared the state field it reads as a set — `_all_record_fields: Set[str]`;
- typed sibling stubs for the `str`-returning helpers it calls — `_field_label`,
  `_array_coerce_arg`, `_coerce_to_int`, `_field_type_for` (`-> str`), plus a
  no-effect `_add_abstract_op(decl: str)` (abstract-op registration is an opaque
  output accumulator, not logic state — consistent with array_slice's frame).

**Three byte-clean TOOL fixes** (each gated on `@mutable_state`, reusable by every
future handler; byte-diff 0):
1. **`_is_str_val` generalized** — in a `@mutable_state` class ANY string-typed value
   binds a string local (`obj = stmt.object` — a `str` field read; `s = other_str`),
   not just Call/FString results.
2. **str-key set membership** — `field in self._all_record_fields` hashes the string
   key with `str_hash_op` (the read-side analogue of M.7's `.add`).
3. **`any()`/`all()` truthiness** — they lower to bool-returning vals, so `if not
   any(…)` uses them directly, never the int `(… <> 0)` coercion.

**Net.** THREE real emitter handlers now verify their own bodies
(`_handle_ghost_array_set_stmt`, `_handle_array_slice_set_stmt`,
`_handle_fieldassign_stmt`). Each new handler adds a few gated tool fixes that the
next inherits — the per-handler cost is shrinking. The body-faithful-emitter track is
a working, scaling pipeline.

---

## 14. Scaling limit found — `_handle_augassign_stmt` hits Ceiling B (heterogeneous reflection)

Attempting the 4th handler exposed where the per-handler recipe stops being mechanical.
`_handle_augassign_stmt` advanced cleanly through the familiar tail — declaring the
array/seq state sets (`_array_locals`, `_array2d_params`, `_current_array1d_params`,
`_seq_locals` as `Set[str]`), aligning the `_seq_operand` stub param, and a str-keyed
dict-membership consistency fix — but its **str-augassign branch** hits a genuine wall:

```python
raw_op == "+" and self._is_string_expr({"type": "Var", "name": target})
                and self._is_string_expr(stmt.value.to_dict())
```

In ONE handler, `self._is_string_expr` is called with BOTH `stmt.value` (a typed IR
node — R1 routes it to `int`) AND an **inline-constructed dict** `{"type": "Var",
"name": target}` (a heterogeneous `map`). A single abstract sibling `val` can't take
both an `int` and a `map` for the same parameter — the heterogeneous `Dict[str, Any]`
built on the fly and reflected on IS **Ceiling B**. Unlike R1 (`d = node.to_dict();
d.get(k)`, a recognizer over the EXISTING typed IR), this is the emitter *manufacturing*
a node dict and immediately querying it — there is no typed node to route to.

**Takeaway.** The recipe scales mechanically for handlers that read typed fields, call
`str`-returning siblings, and mutate declared state (three landed:
`_handle_ghost_array_set_stmt`, `_handle_array_slice_set_stmt`,
`_handle_fieldassign_stmt`). It STOPS at handlers that construct inline IR-node dicts
and reflect on them mid-body. Un-`\trusting` those needs the real Ceiling-B lift — a
typed constructor for IR nodes (so `{"type": "Var", …}` builds a typed `ExprIR`, not a
`map`), which is the Phase-A/B story extended to node *construction*, not just
consumption. That is a feature, not a per-handler stub — scoped, not attempted here.
