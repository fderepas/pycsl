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
