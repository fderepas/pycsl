# fable response: raw-`Dict[str,Any]` → emit_ir-ADT bridge wall

**Role:** INDEPENDENT reviewer (fable). Verdict formed from my own repo reading + my own oracle runs.
**Branch:** ghost-assign-bc6, HEAD 901cb301, count 1041.
**Bottom line: BOUNDARY.** The keystone the report proposes to broaden is *already broad* — a bare
`"ExprIR"` param lowers `.get("type")`/subscript to `kind_of`/`is_K`/projectors with **no `.to_dict()`**.
The named-field `-> str` emitters stay trusted because of DIFFERENT, downstream value-model/local-type
gaps, not the raw-dict→ADT keystone. CLAIM B's corpus-inertness premise is also **false** (the ExprIR path
is corpus-load-bearing).

---

## Oracle artifacts

### Artifact 1 — CLAIM A (is `.to_dict()` the trigger?). File `scratchpad/oracle_claimA.py`
Three `-> str` functions, emitted with
`python3 src/pycsl/pycsl.py scratchpad/oracle_claimA.py --import-path src/pycsl --keep-mlw --no-typecheck`.
Emitted `oracle_claimA.mlw`:

```
290  let kind_exprir (node: emit_ir) : string          (* param: node: ExprIR, bare .get, NO .to_dict() *)
293    if (is_binop node) then begin
294      raise (Return_str (op_of node))               (* .get("op") -> op_of : string   ✓ *)

300  let kind_rawdict (node: map string (option int))   (* param: node: Dict[str,Any] *)
303    if ((match Map.get node "type" with | Some v_ -> v_ | None -> 0 end) = 20805482) then begin
304      raise (Return_str (match Map.get node "op" ... end))   (* Map.get -> int; Return_str wants string *)
       => Why3: line 304 "This expression has type int, but is expected to have type string"

310  let left_kind_exprir (node: emit_ir) : string      (* node["left"].get("type") *)
313    if (is_binop node) then begin
314      raise (Return_str (kind_of (left_of node)))    (* subscript ["left"] -> left_of; .get("type") -> kind_of  ✓ *)
```

**Reading:**
- A raw `Dict[str,Any]` param → `map string (option int)`; `.get("type")` → an abstract `Map.get` (the
  key `"type"` hashed to the int `20805482`); the value is `int`, so the `-> str` return type-errors
  (`int` vs `string`). **This half of CLAIM A is CONFIRMED.**
- But a **bare** `"ExprIR"` param (`kind_exprir`, `left_kind_exprir`) — with **no `.to_dict()` anywhere** —
  already lowers `.get("type")==K` → `(is_binop node)`, `.get("op")` → `(op_of node)`, subscript `["left"]`
  → `(left_of node)`, `.get("type")` → `(kind_of …)`. **The causal claim of CLAIM A — that the keystone
  fires ONLY when the body also calls `.to_dict()` — is REFUTED.**

The actual trigger is the **param annotation**, not `.to_dict()`:
- `functions.py:147` — `symtype in ("ExprIR","StmtIR","IRNode","ContractExprIR","exprir")` → the param
  renders `(safe: emit_ir)`.
- `expressions.py:1157-1161` (`_is_emit_ir_expr`, `Var` arm) — a `Var` whose symbol-table type is an
  IR-node tag is emit_ir.
- `expressions.py:5141-5154` (`_lower_dict_get_call`, "B-C3" branch) — `node.get(k)` on such a Var routes
  through `_EMIT_IR_PROJ` to the total projector.
`.to_dict()` is a **separate** alias mechanism (`_todict_aliases`, `statements.py:105-106`,
`expressions.py:5127-5135`) that tags a *local* bound from `d = node.to_dict()`; it is one of several ways
into emit_ir, not the gate.

### Artifact 2 — CLAIM B, part 1 (nothing to broaden; the named-field blocker is elsewhere). File `scratchpad/oracle_stringctx.py`
A faithful shape-copy of the real `_expr_to_whyml_string_ctx` body (`expressions.py:8292-8315`): bind
`t = ir.get("type")`, branch on `t == "StrConcat"`, recurse on `ir["left"]`/`ir["right"]`, and read
`ir.get("value","")` as a string leaf. Emitted `oracle_stringctx.mlw`:

```
299  let rec string_ctx (ir: emit_ir) : string
300      variant  { size ir }                    (* recursion measure INJECTED automatically *)
302    let t = ref 0 in
303    t := (kind_of ir);                         (* kind_of : string  assigned to  ref 0 : int *)
       => Why3: line 302 "This expression has type string, but is expected to have type int"
       ...  let l = ref (string_ctx (left_of ir)) in   (* left_of / right_of recursion  ✓ *)
       ...  raise (Return_str (slit (svalue_of ir)))    (* .get("value","") -> svalue_of : emit_ir, slit wants string *)
```

**Reading — the keystone works, two OTHER gaps block:**
1. `variant { size ir }` is injected and the recursion over `left_of ir`/`right_of ir` type-checks — the
   ADT bridge is fully engaged, no `.to_dict()`.
2. **Local-type-inference gap:** `t = ir.get("type")` binds a local the tool pre-declares `ref 0` (int),
   while `kind_of ir` is `string` → the assignment type-errors. The *working* corpus/oracle cases compare
   `.get("type")` **inline** (`if node.get("type")=="BinOp"` → `is_binop`); binding it to a local first is
   not recognized as producing a string local.
3. **`value_of` vs `svalue_of` gap:** `ir.get("value","")` on a *bare-Var* emit_ir receiver projects to
   `svalue_of` (an emit_ir sub-node, for chaining), not the string leaf `value_of`. The string-leaf
   disambiguation exists only for a *subscript-element* receiver (`expressions.py:5027`,
   `_k == "value" → value_of`), so a bare-Var string-context read type-errors.

Both are value-model / local-type gaps **downstream of** the keystone; broadening the raw-dict→ADT trigger
would not touch them.

### Artifact 3 — CLAIM B, part 2 (the ExprIR path is corpus-LOAD-BEARING, not inert)
```
$ grep -rl 'ExprIR\|StmtIR\|IRNode\|ContractExprIR' test-suite/corpus/
  test-suite/corpus/pycsl-reference/{0748,0749,0878,0879,0880,0881}.py
```
These reference programs declare `node: ExprIR` (or `"ExprIR"`) params and exercise exactly this lowering —
e.g. `0878.py`: `node.get("type")=="BinOp"` → `is_binop`, `node.get("op")` → `op_of`,
`node.get("left")`/`.get("right")` → `left_of`/`right_of`, with `variant { size node }`. It PROVES today:
```
$ python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0878.py --import-path src/pycsl
  ... node_size'vc  Prover result is: Valid (0.06s, 38850 steps).
  [+] Verification SUCCESS! All contracts formally proven.
```
So the premise "`ExprIR` is a mirror-only annotation that NO reference-corpus program uses" is **false**;
any change to this lowering path is **corpus-affecting**, and byte-diff-0 cannot be assumed.

---

## Verdicts

### 1. CLAIM A — MIXED (surface CONFIRMED, causal claim REFUTED)
- CONFIRMED: a raw `Dict[str,Any]` param → `map string (option int)`; `.get("type")` → abstract `Map.get`
  (int-hashed key); the sibling/return type-error (`int` vs `string`) is real (Artifact 1, line 304).
- REFUTED: `.to_dict()` is **not** the trigger. A bare `"ExprIR"` param already lowers `.get`/subscript to
  `kind_of`/`is_K`/`op_of`/`left_of`/`svalue_of` (Artifact 1, lines 290-294 & 310-314). The trigger is the
  IR-node param annotation (`functions.py:147`), which `.to_dict()` merely also feeds via a distinct alias.

### 2. CLAIM B — REFUTED on both sub-claims
- "Broaden the dict→ADT trigger so bare `.get`/subscript on an `ExprIR` param lowers to `kind_of`/
  projectors": **nothing to broaden — it already does** (`_lower_dict_get_call:5141-5154`,
  `_is_emit_ir_expr:1157-1161`; Artifacts 1 & 2). The keystone is already as broad as the report wants.
- "corpus-byte-diff-0 because no corpus program uses `ExprIR` params": **false** — 0748/0749/0878-0881 use
  them and prove on this path (Artifact 3). The path is load-bearing; a change to it is corpus-affecting.

### 3. VERDICT: **BOUNDARY**
The raw-dict→emit_ir keystone is **not** the wall. It already fires for bare `ExprIR` params without
`.to_dict()`, and it is corpus-load-bearing (so it is neither cheaply broadenable nor corpus-inert). The
`~4-5 named-field `-> str` emitters stay trusted for **separate, downstream** reasons, demonstrated on the
real `_expr_to_whyml_string_ctx` body (Artifact 2):

- **(B1) `kind_of`-bound-local type inference:** `t = ir.get("type")` yields an `int ref`, not a string
  local — the string-typedness of `kind_of` is not propagated to a bound local (only to an inline compare).
- **(B2) bare-Var `.get("value")` string-leaf projection:** projects to `svalue_of` (emit_ir sub-node), not
  `value_of` (string), for a non-subscript receiver.

Neither is the report's keystone; neither is the sibling-stub-contract-propagation issue either. Note on the
report's own BOUNDARY hypothesis: for a `-> str` / `ensures True` emitter, calling a sibling trusted stub
(`_expr_to_whyml`, typed `emit_ir -> string`, `ensures True`) **does** propagate fine — the caller gets an
abstract string, which satisfies its own `ensures True` (Artifact 2's self-recursion + `str_concat_op`
type-checked). So sibling-contract non-propagation is **not** the blocker here; the two value-model gaps
above are.

### Recommended next move (for the driver — NOT authorized by this review)
Retire this wall report; it targets a non-blocker. If the named-field `-> str` emitters are still wanted,
open a **new, correctly-scoped** wall on the two value-model gaps (B1 kind_of-bound-local string inference;
B2 bare-Var `value_of` string-leaf). Both are corpus-affecting recognizer work (the ExprIR path is
load-bearing), so each is BIG-BUILD / authorize-first with a mandatory `bin/byte-diff-sweep.sh` gate — not a
cheap keystone broadening. A cheap first probe: does teaching the string-local collector that
`<emit_ir>.get(<kind-key>)` yields a string local (B1 only) fire byte-diff-0? — but that is a separate
adjudication, not this one.

---

## Provenance / hygiene
- Oracle files: `scratchpad/oracle_claimA.py|.mlw`, `scratchpad/oracle_stringctx.py|.mlw` (all under `/tmp`
  scratch; not in the repo).
- **No spike touched `src/pycsl` or the mirror** — the keystone already fires, so no trigger edit was
  needed to test it; the retype-to-`ExprIR` "spike" was realized as standalone scratch programs instead of a
  mirror edit. `git status` shows only pre-existing `TODO`/`session.txt` (not mine) + this report + the wall
  report. Nothing to revert.
