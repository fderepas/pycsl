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
| **R1.1** | Recognize `d = <typed-node>.to_dict()`; track `d` as an alias of the node (a `_todict_aliases` map, like `_dict_locals` but → the typed node). | alias recorded; `d` not a `ref 0` |
| **R1.2** | Lower `d.get(key)` for an aliased `d` to the node's field: `"type"`→kind tag; other keys→`node.<key>` (schema-checked). Reuse `_lower_dict_get_call`'s Map path only as a fallback. | reflection witnesses (str/node/list keys) verify |
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
