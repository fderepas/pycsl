# Typed IR-node constructor — breaking Ceiling B

**Goal.** Let the emitter's inline IR-node dict literals — `{"type": "Var", "name":
target}`, `{"type": "Attribute", "object": …, "attr": …}` — lower to a **typed
`exprir` value** instead of a heterogeneous `map`, so a sibling that receives BOTH a
real ExprIR field AND a constructed node (the same `self._is_string_expr(...)` call)
type-checks. This is the last wall blocking the body-faithful-emitter track from
scaling past the three handlers already un-`\trusted`.

Companion to `todict-reflection-plan.md` §14 (which diagnosed the wall) and to the
Phase-A/B typed-IR work (`phase-b-expr-plan.md`) and R1 (`todict-reflection-plan.md`
§6–§13). Save/execute per the repo plan-file convention.

---

## 1. The wall, precisely

`_handle_augassign_stmt`'s str-augassign branch (`statements.py:684`):

```python
raw_op == "+" and self._is_string_expr({"type": "Var", "name": target}) \
                and self._is_string_expr(stmt.value.to_dict())
```

In ONE handler `self._is_string_expr` is applied to two operands:

| operand | current WhyML type | why |
|---|---|---|
| `stmt.value.to_dict()` | `int` (R1 routes the to_dict alias to the typed node `stmt.value`, an ExprIR field modelled opaque-int) | §12 var-substitution |
| `{"type": "Var", "name": target}` | `map … (option …)` (a body dict literal) | dict-literal lowering |

A single abstract `val self__is_string_expr_1 (ir: ?)` cannot have a parameter that is
both `int` and `map`. **Ceiling B** = the emitter *manufacturing* a heterogeneous
`Dict[str, Any]` node in-body and reflecting on it, with no existing typed node to
route to. R1 dissolved reflection over *existing* IR; this dissolves *construction* of
new IR.

**Surface** (all inline `{"type": …}` sites in `src/pycsl/module6_whyml/`): 17 total —
**12 `Var`**, **3 `Attribute`**, 1 `RawWhyml`, 1 `Number`. Small, closed, shallow
(deepest is `Attribute` of `Var`, depth 2). This is a bounded feature, not an open
research problem.

---

## 2. The fix in one sentence

Model `ExprIR` as a **WhyML algebraic sum `exprir`** (mirroring the `ExprIR`
dataclass sum that already exists in `ir_schema.py`), lower every inline `{"type":
K, …}` to the matching constructor, type every ExprIR-valued field/param/local as
`exprir`, and express reflection (`.get("type")`/`.get("name")`) as total projection
functions over `exprir`. Then the four sites below all speak one type.

### 2.1 The `exprir` theory (new WhyML prelude, emitted on demand)

Mirror the `ir_schema.ExprIR` variants actually constructed inline (extend as new
kinds appear — an `EOther` catch-all keeps it total):

```whyml
type exprir =
  | EVar      string                 (* VarExpr.name              *)
  | EAttribute exprir string         (* AttributeExpr.object,attr *)
  | EString   string                 (* StringExpr.value          *)
  | ENumber   int                    (* NumberExpr.value          *)
  | ERawWhyml string                 (* RawWhymlExpr.whyml         *)
  | EOther    string                 (* any kind not modelled: carries its tag *)

function kind_of (e: exprir) : string =
  match e with
  | EVar _        -> "Var"      | EAttribute _ _ -> "Attribute"
  | EString _     -> "String"   | ENumber _      -> "Number"
  | ERawWhyml _   -> "RawWhyml" | EOther k       -> k
  end

(* reflection projections — TOTAL, default "" / EOther "" off-variant *)
function name_of  (e: exprir) : string = match e with
  | EVar n -> n | EAttribute _ a -> a | _ -> "" end
function value_of (e: exprir) : string = match e with
  | EString v -> v | ERawWhyml v -> v | _ -> "" end
function object_of (e: exprir) : exprir = match e with
  | EAttribute o _ -> o | _ -> EOther "" end
```

`kind_of`/`name_of`/`value_of`/`object_of` are `function`s (logic + program via the
standard `val`-bridge the emitter already uses for `str_length_op` etc.), so they work
in both body and spec contexts. The recursion in `EAttribute` is why an **ADT, not a
wide record**, is the right model (a self-referential record needs the ADT anyway).

### 2.2 The four integration points

1. **Construction.** `{"type": "Var", "name": e}` → `(EVar <e lowered>)`;
   `{"type": "Attribute", "object": o, "attr": a}` → `(EAttribute <o> <a>)`; etc.
   Unknown/partial kinds → `(EOther "<kind>")` (sound: reflection yields the tag and
   `""`, never a false value).
2. **ExprIR-valued fields/params/locals.** A typed ExprIR field (`stmt.value`,
   `AssignStmt.value: "ExprIR"`) and the sibling params that take one
   (`_is_string_expr(ir)`, `_expr_to_whyml(expr)`, `_seq_operand(val_ir)`) are typed
   `exprir` — replacing today's opaque `int`.
3. **Reflection.** `node.get("type")` → `(kind_of <node>)`; `.get("name")` →
   `(name_of <node>)`; `.get("object")` → `(object_of <node>)`; `.get("value")` →
   `(value_of <node>)`. This SUPERSEDES the R1 `_todict_routed_ir` field routing with a
   single typed projection — R1's alias tracking (§7) stays; only the lowering target
   changes from an `Attribute` IR to a `*_of` call.
4. **Round-trip identity.** `to_dict(from_dict(d)) == d` already holds in Python
   (`test_ir_schema_roundtrip.py`); the WhyML side needs
   `kind_of (EVar n) = "Var"` etc. as `ensures` on the constructors — trivial by the
   `match`, discharged automatically.

---

## 3. Phased plan (each phase byte-diff-gated, own PR)

Gate every phase on `@mutable_state` (the emitter-model marker) so the 627-file corpus
stays **byte-identical** — this feature only ever fires inside the self-annotation
mirror. `bin/byte-diff-sweep.sh <out>` + `diff -rq <baseline> <out>` must be empty.

- **B-C1 — the theory + constructor lowering.** Emit the §2.1 `exprir` prelude via
  `_add_abstract_op` when any inline `{"type": K}` is lowered in a `@mutable_state`
  method; lower the 4 constructed kinds (Var/Attribute/String/Number/RawWhyml) to their
  constructors, everything else to `EOther`. *Gate:* a witness
  `src/self-annotate/typed-irnode-witness.py` — a `@mutable_state` method that builds
  `{"type": "Var", "name": x}` and returns `kind_of` of it == `"Var"` — verifies;
  byte-diff 0.
- **B-C2 — ExprIR field/param typing.** Type ExprIR-valued record fields and the three
  sibling stubs (`_is_string_expr`, `_expr_to_whyml`, `_seq_operand`) as `exprir`
  instead of `int`. Reconcile with §12 var-substitution: `d = node.to_dict()` alias now
  routes `d` → the node at type `exprir` (not the opaque field). *Gate:* the witness's
  `_is_string_expr(EVar x)` AND `_is_string_expr(stmt.value)` in one function both
  type-check; byte-diff 0.
- **B-C3 — reflection as projection.** Replace `_todict_routed_ir`'s Attribute-IR
  target with `kind_of`/`name_of`/`object_of`/`value_of` when the receiver is typed
  `exprir`. Keep the R2 record-`str`-field path for genuine record reads. *Gate:* the
  R1 witnesses (`todict-r1-witnesses.py`, `todict-varsubst-witness.py`) still verify
  unchanged; byte-diff 0.
- **B-C4 — acceptance: un-`\trust` `_handle_augassign_stmt`.** Apply the established
  per-handler recipe (declare `_array_locals`/`_seq_locals`/… `Set[str]`, align
  `_seq_operand`, the str-keyed dict-membership consistency fix from the aborted
  scale-h3). With B-C1..3 landed, the str-augassign branch now type-checks. *Gate:*
  `statements.py` PASSES the self-annotation suite with augassign un-`\trusted` (only
  the pre-existing `errors.py` fails); byte-diff 0.

Land B-C1..3 (the mechanism) even if B-C4 surfaces a further residual no-more-int gap —
each is independently valuable and gated.

---

## 4. Non-goals / scope boundary

- **Not** modelling ExprIR *evaluation* — `exprir` carries structure for reflection and
  identity only; `_expr_to_whyml` stays a trusted opaque-`string`-returning sibling
  (its RESULT is unchanged). We type its *argument*, not its body.
- **Not** populating body dict literals in general (the `Map.set`-chain TODO at
  `expressions.py:3676` stays) — only `{"type": K, …}` IR-node shapes are recognized.
- **Not** touching the wire/JSON format or `ir_schema.py`'s Python sum — this is purely
  the WhyML lowering of the mirror. The Python `ExprIR` is the source of truth the ADT
  mirrors.
- **Not** corpus-visible: every change gated on `@mutable_state`.

## 5. Risks & open questions

1. **Recursion cost.** `EAttribute exprir string` makes `exprir` recursive; SMT over
   recursive ADTs can be slow. Mitigation: the constructed nodes are depth ≤ 2, and
   `*_of` are non-recursive matches — no induction needed. Probe VC time on the witness
   before B-C4.
2. **Two coexisting node models during migration.** Between B-C2 and B-C3 some sites see
   `exprir`, some `int`. Keep them disjoint by the `@mutable_state`-scoped
   `_dict_key_types`-style registry; a mixed-type sibling call is the exact error we're
   removing, so it surfaces loudly, never silently.
3. **`from_dict` faithfulness.** The Python `from_dict` (ir_schema.py:250) drops unknown
   keys / tolerates partial dicts; `EOther` must match that under-approximation (reflect
   the tag, default the rest) — never invent a value. Assert this with a witness that
   builds a partial `{"type": "Var"}` (no `name`) and checks `name_of == ""`.
4. **Does R1 fully subsume, or coexist?** R1 routes reflection on *aliased* nodes; B-C3
   routes reflection on *any* `exprir`-typed receiver incl. constructed ones. Confirm
   R1's alias map and B-C3's projection agree on overlapping inputs (the witnesses in
   B-C3's gate check this).

## 6. Reference corpus (required)

Per the repo convention, add a positive fixture to
`test-suite/corpus/pycsl-reference/`: a small `@mutable_state` class whose method
constructs an IR-node dict, reflects on it (`.get("type")`), and passes it to a
str-returning sibling — exercising all three of construction, reflection, and typed-arg
unification. It doubles as the regression guard for B-C1..3 and the minimal
reproduction of the Ceiling-B pattern for future readers.

## 7. Definition of done

- The `exprir` ADT + `kind_of`/`name_of`/`value_of`/`object_of` prelude emitted on
  demand, gated on `@mutable_state`.
- All 17 inline `{"type": K}` sites lower to `exprir` constructors.
- `_is_string_expr` / `_expr_to_whyml` / `_seq_operand` params typed `exprir`; the
  str-augassign branch (`_is_string_expr(constructed) ∧ _is_string_expr(field)`)
  type-checks.
- `_handle_augassign_stmt` un-`\trusted`, verifies, suite green, byte-diff 0.
- Reference-corpus fixture + witnesses committed; `todict-reflection-plan.md` §14
  updated to "Ceiling B LIFTED".
- A FOURTH real emitter handler off the trusted base — and every *inline-reflecting*
  handler now reduced to the mechanical per-handler recipe.

---

## 8. Implementation log — B-C1 + B-C2 landed

**B-C1 (theory + construction lowering) — DONE, byte-clean.** The `emit_ir` ADT
(§2.1) + `kind_of`/`name_of`/`value_of`/`object_of` projections are emitted (once, as
a single-line `type` decl so the abstract-val block can't split it) for any module
with a `@mutable_state` class — `Module6_WhyMLTranspiler._emit_exprir_theory`. Inline
`{"type": K, …}` dict literals lower to the matching constructor via
`expressions._lower_irnode_construction` (`{"type":"Var","name":e}` → `(IrVar <e>)`;
unknown kind / missing payload → `(IrOther "<kind>")`, sound).

**B-C2 (ExprIR field/param typing) — DONE, byte-clean.** `_symtype_to_whyml` maps an
`ExprIR`/`StmtIR`/`IRNode`/`ContractExprIR` symtype → the `emit_ir` type. So an inline
construction (an `emit_ir`) and a real ExprIR field/param unify at a sibling.

**Two discoveries during implementation:**
1. The mirror imports `IRNode` → a `type irnode = int` opaque alias; and it already
   carries FORMAL-SEMANTICS `#@ datatype expr_ir = EVar(string) | …` / `stmt_ir`
   declarations (for the Rocq/Lean proofs, `statements.py:35`). Both own the names
   `exprir`/`irnode` and the constructor `EVar`. The new ADT is therefore named
   **`emit_ir`** with constructors **`IrVar`/`IrAttr`/`IrStr`/`IrNum`/`IrRaw`/
   `IrOther`** to avoid every collision — it coexists with, and is distinct from, the
   formal `expr_ir` (which is NOT wired to the real field types; those are still `int`).
2. The multi-line `type` decl was spliced by the abstract-val insertion point
   (`_find_abstract_val_insert_idx` inserts after the last `type ` line) → the ADT is
   emitted as ONE line.

**Gates passed:** the witness `src/self-annotate/typed-irnode-witness.py` (inline
construction passed to an `ExprIR`-typed sibling) verifies; corpus byte-diff 0; the
mirror `statements.py` still PASSES with the three handlers un-`\trusted`.

**Remaining:** B-C3 (reflection `.get("type")` → `kind_of`, over an `emit_ir`
receiver) and B-C4 (migrate the mirror's `_is_string_expr`/`_expr_to_whyml`/
`_seq_operand` stubs from `int` to `ExprIR`, then un-`\trust` `_handle_augassign_stmt`
— the ripple to re-verify array_slice/fieldassign is the migration cost noted in §5.2).

---

## 9. B-C4 depth finding — the migration is multi-seam (attempted, reverted to green)

B-C4 (un-`\trust` `_handle_augassign_stmt`) was attempted end-to-end. It got FAR — the
inline `{"type":"Var","name":target}` lowers to `(IrVar !target)` inside augassign, and
several migration steps landed byte-clean in a probe branch — but it is **not a single
migration**: `ExprIR → emit_ir` must be threaded through SEVERAL INDEPENDENT
type-resolution seams, each its own fix. §5.2's "migration cost" was understated. The
probe reverted (main stays green at B-C1+B-C2; the mirror must never be left broken).

**Seams identified (✓ = solved in the probe, byte-clean; ✗ = still open):**
1. ✓ **Sibling stub params** — `_is_string_expr`/`_expr_to_whyml`/`_expr_to_whyml_string_ctx`/
   `_seq_operand` mirror signatures `int`/`Dict[str,Any]` → `"ExprIR"`.
2. ✓ **Record field types** — `preamble._emit_type_decls` ftype resolver: an `ExprIR`
   field tag → `emit_ir` (else falls back to `int`).
3. ✓ **Param annotation → symtype** — `Module5._m5_get_type_name` (and
   `_field_type_from_annotation_inst`): preserve `ExprIR`/`StmtIR`/`IRNode` (bare,
   forward-ref string, or `Optional[...]`) as the tag "ExprIR", via a shared
   `_irnode_ann_name` helper.
4. ✓ **ADT declared before records** — the `emit_ir` `type` must precede the record
   types that name it (move the `_emit_exprir_theory` call above `type_lines`).
5. ✓ **Inline `to_dict()` identity** — `<node>.to_dict()` (no args) in a @mutable_state
   method → the receiver (an `emit_ir`), since to_dict is identity on the typed IR
   (`_handle_call_expr` intercept). The BOUND form is R1's alias.
6. ✗ **`_module_method_param_types` map** — `_resolve_dotted_signature` still returns
   `['int']` for `_is_string_expr`'s param (the abstract self-call `val` is declared
   `(x0: int)`), because the METHOD param symtype in this map is built via a path that
   does NOT yet see the "ExprIR" tag. This is the next fix: thread the tag into
   `_build_method_param_types_map` / the symbol-table param typing.
7. ✗ **augassign's own residual no-more-int tail** — unreached; expect the same class of
   per-handler gaps scale-h3 hit (dict-literal value types, etc.).

**Assessment.** The mechanism (B-C1+B-C2) is sound and landed. B-C4 is a bounded but
GENUINELY MULTI-SEAM migration (~2 seams still open + augassign's tail), each fix
byte-clean and gated. It is finishable, but as a focused pass that threads seam 6, then
walks augassign to green — NOT a single edit. Recommend doing it with a fresh context
budget; the seams above are the exact worklist.

---

## 10. B-C3 + B-C4 DONE — Ceiling B LIFTED, a FOURTH handler un-`\trusted`

`_handle_augassign_stmt` is no longer `\trusted` — it verifies; `statements.py` PASSES
the self-annotation suite with all FOUR real handlers un-`\trusted`
(`_handle_ghost_array_set_stmt`, `_handle_array_slice_set_stmt`,
`_handle_fieldassign_stmt`, `_handle_augassign_stmt`; only the pre-existing `errors.py`
fails). The Ceiling-B pattern — `self._is_string_expr({"type":"Var",…})` alongside
`self._is_string_expr(stmt.value.to_dict())` — now type-checks: both are `emit_ir`.

**All 7 seams threaded, byte-clean:**
1. sibling stub params (`int`/`Dict` → `"ExprIR"`) — mirror.
2. record field-type resolver `ExprIR` → `emit_ir` — `preamble._emit_type_decls`.
3. annotation → symtype (bare / forward-ref / `Optional[…]`), via a shared
   `_irnode_ann_name` helper — `Module5._m5_get_type_name` + `_field_type_from_
   annotation_inst`. **Critical fix:** the helper duck-types on `type(node).__name__`,
   NOT `isinstance(_, ast.Constant)` — the frontend's AST nodes come from a different
   `ast` module object, so isinstance spuriously returns False (the bug that stalled the
   first B-C4 attempt).
4. ADT declared BEFORE the record types — `Module6_WhyMLTranspiler`.
5. inline `to_dict()`-identity → the receiver — `_handle_call_expr`.
6. `_module_method_param_types` map — resolved once seam 3 fed the "ExprIR" tag through
   the symbol table (`self__is_string_expr_1 (x0: emit_ir)`).
7. augassign's residual no-more-int tail — `Optional[ExprIR]` `is None`/`is not None`
   (modeled always-present, sound for the type-safety+frame contracts; `option emit_ir`
   is the value-faithful follow-on); and the `bitwise_ops` str-dict — membership AND
   subscript now BOTH `str_hash_op` the key (an int-keyed `map _ (option int)`), so they
   agree.

**B-C3 (reflection as projection) — implemented.** `<emit_ir>.get("type")` →
`(kind_of node)`, `"name"`/`"attr"` → `(name_of node)`, `"value"` → `(value_of node)`,
`"object"` → `(object_of node)` (`_lower_dict_get_call`), and `_is_string_expr`
recognizes the string-valued projections so `node.get("type") == "Var"` routes through
`str_eq_op`. Byte-clean; the lowering is correct (`if (str_eq_op (kind_of node) "Var")`).
Not exercised by the current four handlers (they reflect via `.to_dict()` aliases, R1),
so it stands as a proven capability for future reflecting handlers.

**Net.** Ceiling B — the emitter manufacturing a heterogeneous IR-node dict and
reflecting on it, feared irreducible — is LIFTED. FOUR real emitter handlers verify
their own body-faithfulness. The witness `src/self-annotate/typed-irnode-witness.py`
verifies; corpus byte-diff 0. Value-faithful `option emit_ir` for optionals remains the
one honest simplification (§9 seam 7), a bounded follow-on.

---

## 11. A FIFTH handler un-`\trusted` (`_handle_fieldaugassign_stmt`) — zero tool changes

`_handle_fieldaugassign_stmt` is now un-`\trusted` and verifies with **no new tool
code** — the B-C4 `emit_ir` infrastructure (typed field/param, inline `to_dict()`
identity, `_add_abstract_op` opaque) was sufficient. `statements.py` PASSES the suite
with FIVE real handlers off the trusted base (only the pre-existing `errors.py` fails).
Confirms the infrastructure now amortizes: a reflecting-family handler that reads a
typed `stmt.value`, emits via `_expr_to_whyml`, and registers ops needs only the mirror
un-`\trust`.

**`_handle_assign_stmt` (the flagship) — deeper, deferred.** An attempt got it partway
(via three reusable-but-unlanded probes: **R1 × B-C3** — a `d = node.to_dict()` alias
whose node is `emit_ir` routes `d.get("type")` to `kind_of`, not the legacy `get_kind`;
a **recognizer-time alias pre-scan** so the string-local recognizer sees the alias; and
a **`_is_str_val` Call fall-through** so an alias-get is recognized as `string`). But it
then hit machinery beyond the reflection layer: `.get()` on a SELF-FIELD dict
(`self._current_symbol_table.get(target)`), a `dict[str,str]` field with string values,
and a `declared_refs.add(target)` PARAM mutation. Those are a separate sub-feature
(self-field dict reflection), not the IR-node story — so assign_stmt is deferred with
its worklist recorded here, and the three probes were not landed (they only fire for
assign_stmt, so they'd be inert until it's taken on).

**Net.** FIVE real emitter handlers verify their own body-faithfulness. Each new one
after the B-C4 lift costs less; the two that remain hardest (`assign`, and the big
`_handle_array_set_stmt`/`_handle_critical_section_stmt`) need self-field dict
reflection, a bounded next feature.

---

## 12. Self-field dict reflection — BUILT (the next feature for `assign`/big handlers)

`self.<dict-field>.get(key)` now reads the DECLARED record map field instead of an
opaque abstract — the reflection an emitter does over its OWN transpiler state (e.g.
`_handle_assign_stmt`'s `self._current_symbol_table.get(target)`). Byte-clean, gated on
the field being a real record dict/set field. Witness
`src/self-annotate/self-field-dict-witness.py` verifies.

**Parts (all byte-diff 0 across the 627-corpus):**
1. **The read** — `_lower_dict_get_call` recognizes a `self.<field>.get(k)` whose
   `<field>` is a `dict`/`set` record field (`_self_field_dict_nu`) and emits
   `(match Map.get self.<field> <k> with Some v -> v | None -> <default>)`; the string
   key is `str_hash_op`-hashed (matching the M.7 `.add` write). The receiver lowers via
   a `FieldGet` IR so it is the real `self.<field>`, not `get_<field>`.
2. **The value type** — a `dict[str, str]` field carries `option string` values
   (`Module5._m5_get_dict_value_type` → the field's `value_type`; the preamble emits
   `map int (option string)` and records `field_value_types`), so the get reads back a
   `string`.
3. **The recognizer** — `_is_string_expr` knows `self.<dict[str,str]-field>.get(k)` is a
   `string`, so `… == "str"` routes through `str_eq_op`, not an int hash.
4. **The imports** — a record with a `map …` field triggers `use map.Map`/`map.Const`/
   `option.Option` even in a module with no body dict (real handlers already have one).

**What this unblocks.** `_handle_assign_stmt` (and the big `_handle_array_set_stmt`/
`_handle_critical_section_stmt`) read `self.<dict-field>.get(…)`; that opaque read was
one of the three blockers §11 named. The remaining two for `assign` specifically are the
reflection probes (R1×B-C3 emit_ir alias→`kind_of`, recognizer-time alias pre-scan,
`_is_str_val` Call fall-through — prototyped in §11, land them WITH `assign`) and a
`declared_refs.add` PARAM-set mutation. This feature is the reusable piece; the rest is
per-handler.

---

## 13. A SIXTH handler un-`\trusted` (`_handle_seq_assign`) — two small reusable fixes

`_handle_seq_assign` is un-`\trusted` and verifies. `statements.py` PASSES the suite
with SIX real handlers off the trusted base (only the pre-existing `errors.py` fails).
It needed the `_seq_init_expr` sibling typed `"ExprIR"` (mirror) plus two byte-clean,
reusable tool fixes — both blockers §11 named for the reflecting handlers:

- **Set/dict PARAM mutation** (`declared_refs.add(target)`) — a `.add`/`.discard`/
  `.remove` on a set/dict-typed PARAM (not a body-local, not a self-field) in a
  `@mutable_state` method is a SOUND NO-OP: the mutation is on a value param, so it
  does not escape for the `assigns \nothing` / type-safety contract (a Python set param
  IS mutated, but no contract here reads it — the recursion's `declared_refs` is a
  trusted-sibling arg). This was the third §11 blocker for `_handle_assign_stmt`, now
  dissolved and reusable.
- **String truthiness** (`if not rest_code:`) — a `string` var (`rest_code =
  self._stmts_to_whyml(…)`) is truthy iff non-empty (`String.length s <> 0`), not the
  ill-typed int `s <> 0`. Added to `_to_bool`, the str counterpart of the existing
  array-truthiness case.

**Net.** SIX real emitter handlers verify their own body-faithfulness. `_handle_assign_
stmt`'s three §11 blockers are now ALL solved (self-field dict §12, the reflection
probes prototyped in §11, and set-param mutation §13) — assign is the next natural
target, needing only the §11 probes landed alongside it.

---

## 14. `_handle_assign_stmt` — attempted; a deeper multi-feature tail (NOT the last three)

Scaling to the flagship `_handle_assign_stmt` was attempted with all the pieces: the
three reflection probes re-applied (R1×B-C3 emit_ir alias→`kind_of`, recognizer-time
alias pre-scan, `_is_str_val` Call fall-through — all byte-clean), the state fields
declared (`_current_symbol_table: Dict[str,str]`, `_shared_var_names`,
`_decode_to_string`), and the `_track_collection_metadata` sibling stubbed. It advanced
past `vt = val_ir.get("type")` (the reflection) and `_track_collection_metadata` — but
then revealed that `assign`'s tail is DEEPER than the three §11 blockers, needing new
sub-features:

1. **The `getattr(self, "<field>", <default>).method()` idiom** — the emitter's
   defensive field access (`getattr(self, "_current_symbol_table", {}).get(target)`,
   3× in these handlers). The `.get` is a method on a `getattr` CALL result — a
   STRUCTURED func, not the flat `self.<field>.get` string the self-field-dict
   recognizer (§12) matches — so it falls to the opaque `get_1`. Handling it needs
   recognizing `getattr(self, <str-field>, <default>)` as `self.<field>` at the call
   seam, then routing the method.
2. **Bool-flag self mutation** — `self._decode_to_string = True/False` (a scalar field
   write, distinct from the set-field `.add` of §13).
3. **Set-field membership on more state** — `target in self._shared_var_names` /
   `self._seq_locals` / `self._array_locals`, plus `_emit_array_local_reassign`.

None is hard alone, but there are SEVERAL, and #1 (structured-func reflection through
`getattr`) is a genuine new feature. `assign` is therefore the most entangled statement
handler — deferred with this worklist. The attempt was reverted to keep the SIX landed
handlers green (the re-applied probes are inert without `assign`, so not landed). The
tractable frontier is elsewhere: a handler whose reflection is direct (`stmt.value`)
rather than through `getattr(self, …)`.

---

## 15. The `getattr(self, field, default)` recognizer — BUILT (§14 blocker #1)

`getattr(self, "<field>", <default>).get(key)` — the emitter's DEFENSIVE self-field
access, the first of the three §14 sub-features `_handle_assign_stmt` needs — now routes
to the REAL record map field instead of the opaque `get_1`. Byte-clean; witness
`src/self-annotate/getattr-self-field-witness.py` verifies.

**Two parts (byte-diff 0):**
1. **The rewrite** (`_handle_call_expr`): a bare-method call (`func == "get"`) whose
   `receiver` is `getattr(self, "<str>", <default>)` (`_getattr_self_field`) naming a
   DECLARED dict/set field is rewritten to `self.<field>.<method>`, so it flows through
   the self-field dict path (§12) — `(match Map.get self.<field> (str_hash_op k) …)`.
   Gated on @mutable_state and on the field actually being a record dict/set field.
2. **The recognizer** (`_is_string_expr`): the getattr-defensive form of a
   `dict[str,str]` `.get` is a `string`, so `getattr(self, f, {}).get(k) == "s"` routes
   through `str_eq_op`.

**Status of the §14 worklist for `_handle_assign_stmt`.** #1 (the getattr idiom) is now
DONE. Remaining: #2 bool-flag self mutation (`self._decode_to_string = True/False`) and
#3 set-field membership on `_shared_var_names`/`_seq_locals`/`_array_locals` — both
bounded scalar/set-field features, not new reflection. The recognizer here is reusable:
the big `_handle_array_set_stmt`/`_handle_critical_section_stmt` use the same
`getattr(self, …)` idiom.

---

## 16. `_handle_assign_stmt` — deepest handler; a sibling-typing campaign (not a scale-up)

A second attempt (with §15's getattr recognizer landed) got FURTHER but confirmed
`_handle_assign_stmt` is a MULTI-FIX CAMPAIGN, not a single scale-up. It advanced through
~8 distinct issues before the tail continued. The bound-alias reflection (`vt =
val_ir.get("type") → kind_of`) and the getattr idiom (§15) both worked; the new blockers
are in the ABSTRACT SELF-CALL VAL generation for the siblings `assign` calls
(`_handle_seq_assign`, `_first_assign_kind`, `_emit_first_assign`, `_emit_array_local_
reassign`, `_val_is_bool`, …):

- **Record-class param → the record type** — `self._handle_seq_assign(stmt, …)` where
  `stmt: AssignStmt`: the abstract must carry `assignstmt`, not `int` (fix drafted in
  `_build_method_param_types_map`, byte-clean, @mutable_state-gated).
- **Reassigned formal params dropped** — `_emit_first_assign`'s `val: str` param is
  reassigned in the body (`val = _empty`), so the map builder skipped it as a "local",
  short-changing the param list and MISALIGNING the abstract's parameter types (fix:
  don't skip a name that is in `formal_params`; byte-clean).
- **Reassigned-param TYPE drift** — after the two fixes above, `_emit_first_assign`'s
  `val` param still resolves to `int` (its symbol-table type drifted from the `str`
  annotation because the body reassigns it): the abstract self-call val must prefer the
  param ANNOTATION over the re-inferred symbol-table type. NOT yet solved.
- Plus §14 #2 (bool-flag self mutation `self._decode_to_string = …`) and #3 (set-field
  membership) still ahead.

**Assessment.** `assign` is the ONLY statement handler that calls a rich fan of typed
siblings, so it exercises the abstract-self-call-val typing seam far harder than the six
landed handlers (which mostly call `_expr_to_whyml`/`_add_abstract_op`). Closing it is a
dedicated pass over that seam (record params, reassigned params, annotation-vs-inferred
type, then §14 #2/#3) — bounded but multi-fix. Reverted to keep the SIX landed handlers
green. The tractable frontier remains the direct-reflection handlers; `assign` wants its
own focused campaign with this worklist.

---

## 17. THE ASSIGN CAMPAIGN — DONE. `_handle_assign_stmt` un-`\trusted` (SEVEN handlers)

`_handle_assign_stmt` — the flagship, the deepest statement handler — is no longer
`\trusted`. It verifies with `assigns self._decode_to_string`; `statements.py` PASSES the
suite with SEVEN real handlers off the trusted base (only the pre-existing `errors.py`
fails). Byte-diff 0 across the 627-corpus.

The campaign landed the abstract-self-call-val typing seam (the §16 worklist) plus the
final pieces — all byte-clean, all gated on @mutable_state:

- **Record-class param → the record type** (`_build_method_param_types_map`):
  `self._handle_seq_assign(stmt: AssignStmt)` → the abstract carries `assignstmt`.
- **Reassigned formal params kept** (same map): a formal param reassigned in the body
  (`val = _empty`) is no longer dropped as a "local" (which misaligned the abstract's
  parameter types).
- **Annotation over inferred type** (same map): a formal param prefers its declared
  annotation (`val: str`) over its drifted symbol-table type (`Any`→int).
- **`let function` projections** (`_emit_exprir_theory`): `kind_of`/`name_of`/`value_of`/
  `object_of` are `let function` (program+logic), so `vt = val_ir.get("type")` →
  `(kind_of stmt.value)` is legal in the program body (a plain `function` is logic-only,
  rejected in non-ghost context).
- **Bool-flag self mutation** (§14 #2): `self._decode_to_string = True/…/restore` is a
  genuine transient self-field write → the handler's frame is `assigns
  self._decode_to_string` (a CHECKED write, not `\nothing`).
- The reflection probes (R1×B-C3, alias pre-scan, `_is_str_val` Call fall-through) and
  the self-field-dict/getattr recognizers (§12/§15) all fired. §14 #3 (set-field
  membership) needed no new work — the existing str-key membership handled it.

Mirror side: declared `_current_symbol_table: Dict[str,str]`/`_shared_var_names`/
`_decode_to_string`; typed the `_track_collection_metadata`/`_first_assign_kind`/
`_val_is_bool` sibling stubs and the `_emit_first_assign`/`_emit_array_local_reassign`
`val_ir` params as `"ExprIR"`.

**Net.** SEVEN real emitter handlers verify their own body-faithfulness, INCLUDING the
flagship — the one that reflects on the IR, mutates transpiler state, defensively reads
its own dict fields via `getattr`, and fans out to a rich set of typed siblings. The
abstract-self-call-val typing seam is now correct for the whole emitter.

---

## 18. Field-vs-local collision + two no-more-int fixes (toward `_handle_ghost_assign_stmt`)

Scaling toward `_handle_ghost_assign_stmt` produced three byte-clean, GENERAL fixes —
the first is the key one:

- **Field-vs-local label collision** (`_emit_type_decls`, witness
  `src/self-annotate/field-vs-local-witness.py`): a record field whose name ALSO names
  a LOCAL var in some method collided in Why3 — `stmt.ghost_type` resolved to the local
  `ghost_type` ref ("this expression has type ref int … it cannot be applied"), not the
  field. Such fields are now qualified (`<record>_<field>`) in both decl and access
  (added to `_ambiguous_fields`). This was the SHARED first error of all three "ref
  cannot be applied" handlers (`ghost_assign`, `tuple_unpack`, `critical_section`).
- **Dict-FIELD subscript-set str key** (`_handle_array_set_stmt`): `self._ghost_tuple_
  vars[target] = …` on a `Dict[str,_]` field hashes the string key with `str_hash_op`
  (the write analogue of the §12 self-field-dict get).
- **`int(<str>)` conversion** (`_handle_call_expr`): `int(ghost_type[-1])` is a genuine
  str→int (`str_to_int`), not the int-identity.

All @mutable_state-gated, byte-diff 0. The seven landed handlers stay green.

**`_handle_ghost_assign_stmt` — a LONG handler, deferred.** With the collision fixed it
advanced far (sibling stub `_resolve_effective_ghost_type`, seven ghost-var-kind state
fields `_ghost_string_vars`/`_ghost_array_vars`/`_ghost_tuple_vars`/`_ghost_dict_vars`/
`_ghost_list_vars`/`_ghost_set_vars` + a checked `assigns`, the dict-field subscript-set,
`int(str)`) — but it tracks SEVEN ghost-var kinds, each a branch with its own set/dict
mutation and str parsing, plus emit_ir-LOCAL typing (`val_ir := stmt.value`, an emit_ir
local not yet recognized like a string local). It is bounded but broad — its own pass.
The field-vs-local fix, though, is landed and reusable: it clears the first blocker for
`tuple_unpack` and `critical_section` too.

---

## 19. Emit_ir-local recognizer (toward `_handle_critical_section_stmt`)

A local bound to an `emit_ir` value — `assume_inv = stmt.assume_invariant` (an ExprIR
field), an inline `{"type": K}` construction, a `d = node.to_dict()` alias, or another
emit_ir local — is now recognized and pre-declared `ref (IrOther "")` (the emit_ir
counterpart of the R3 string `ref ""` pre-decl), not the integer `ref 0`. Byte-clean,
@mutable_state-gated; witness `src/self-annotate/emit-ir-local-witness.py` verifies.

**Three parts:**
- `_collect_emit_ir_result_locals` — a fixpoint over first-assignments (mirrors
  `_collect_str_call_result_locals`), also grows the symbol table to `ExprIR` so
  reflection on the local (`node.get("type")`) sees emit_ir.
- `_emit_ir_predecl` in `_emit_body_code` — pre-declares them `ref (IrOther "")`.
- `_to_bool` — an emit_ir local's truthiness (`if assume_inv:`) is modeled
  always-present (`true`), like the emit_ir `is None` comparison (sound for the
  type-safety+frame contracts; both arms type-check, no self-field write).

**`_handle_critical_section_stmt` — deferred.** With the emit_ir-local recognizer it
cleared `assume_inv`/truthiness but continued into: `safe_var = whyml_ident(var)` in a
`for var in shared_for_mutex:` loop where `whyml_ident`'s abstract-val RETURN is `int`
while its return-ANNOTATION map says `string` (a decl-vs-map inconsistency for a bare
imported helper), the `self._havoc_counter += 1` scalar mutation, the
`_mutex_inv_application` sibling, and a `[s.to_dict() for s in body_stmts]` comprehension.
Bounded but broad — its own pass. The emit_ir-local recognizer is landed and reusable:
it also clears `_handle_ghost_assign_stmt`'s `val_ir := stmt.value` (§18).
