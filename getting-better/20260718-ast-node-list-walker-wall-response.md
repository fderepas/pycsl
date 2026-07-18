# fable review — filtered-map comprehension over an AST-node-list (Gate R)

**Reviewer role:** INDEPENDENT fable. No prior context; judgment formed only from my own
reading of the repo (branch `ghost-assign-bc6`, HEAD `d0aa378e`) and my own oracle runs.
The wall report's prose was treated as a claim to CONFIRM/REFUTE, not as authority.

**Bottom line:** **BREAKABLE** — but *not* by the route the report's framing implies.
Naively extending the abstract-`val` content-law comprehension (the `_filter_record_proj_law`
shape) to this shape is **positionally VACUOUS** (my Part-A oracle proves it). It IS breakable
by a *different, stronger* mechanism: a **concrete compaction `function`** composing the
ALREADY-CONCRETE `is_var`/`name_of` — non-vacuous, observable, heterogeneity-proof, axiom-free
(my Part-B oracle proves it). The wall's own §2 escape hatch ("a filter-predicate + a compaction
law that a driver can observe non-vacuously") is the correct answer.

---

## THE ORACLE ARTIFACT

Hand-written `.mlw` modeling the real preamble projectors —
`is_var : emit_ir → bool` (preamble.py:3585), `name_of : emit_ir → string` (preamble.py:3754) —
over a heterogeneous node list. Two parts:
* **Part A** = the naive port of `_filter_record_proj_law` (expressions.py:7547) from
  `array int` records to `array string` emit_ir (same length-bound + membership/predicate/
  projection existential law), with an OBSERVATION driver.
* **Part B** = a concrete compaction fixpoint composing `is_var`/`name_of`, with observe /
  heterogeneity / evil-twin goals.

File: `scratchpad/filtered_string_wall.mlw` (reproduced in §APPENDIX below).

### Commands
```
why3 prove --type-only filtered_string_wall.mlw          # => tc-exit=0, NO errors
why3 prove -P "Alt-Ergo,2.6.2," -t 15 -a split_vc filtered_string_wall.mlw
why3 prove -P "Z3,4.13.3,"     -t 15 -a split_vc filtered_string_wall.mlw
```

### Verbatim output (Alt-Ergo 2.6.2)
```
File "filtered_string_wall.mlw", line 35 ... Sub-goal Assertion of goal obs_len1'vc.
Prover result is: Timeout (15.00s, 168028 steps).
File "filtered_string_wall.mlw", line 60 ... Goal observe.
Prover result is: Valid (0.04s, 17 steps).
File "filtered_string_wall.mlw", line 67 ... Goal observe_hetero.
Prover result is: Valid (0.04s, 23 steps).
File "filtered_string_wall.mlw", line 72 ... Goal evil_twin.
Prover result is: Timeout (15.00s, 112453 steps).
```

### Verbatim output (Z3 4.13.3)
```
File "filtered_string_wall.mlw", line 35 ... Sub-goal Assertion of goal obs_len1'vc.
Prover result is: Unknown (unknown) (0.13s, 297593 steps).
File "filtered_string_wall.mlw", line 60 ... Goal observe.
Prover result is: Valid (0.10s, 288490 steps).
File "filtered_string_wall.mlw", line 67 ... Goal observe_hetero.
Prover result is: Valid (0.10s, 289612 steps).
File "filtered_string_wall.mlw", line 72 ... Goal evil_twin.
Prover result is: Timeout (15.00s, 21965529 steps).
```

### What the artifact proves
| goal | mechanism | result | meaning |
|---|---|---|---|
| `obs_len1` | Part A abstract existential law | **Timeout/Unknown (UNPROVABLE)** | Given `src=[Name "x"]`, the law does NOT entail `∃i. result[i]="x"`. The **empty-result model** (`length result = 0`) satisfies `length ≤ 1` and the `forall` vacuously → the projected string is un-observable. The abstract law is **positionally VACUOUS.** |
| `observe` | Part B compaction fixpoint | **Valid** | A driver builds `Cons e Nil`, `is_var e`, `name_of e = "x"` and observes `filter_names = Cons "x" Nil`. Fully pinned. |
| `observe_hetero` | Part B | **Valid** | `Cons (Name "x") (Cons non-Name Nil)` compacts to exactly `Cons "x" Nil`. Heterogeneity handled — the filter drops the non-Name element. |
| `evil_twin` | Part B | **Timeout/Unknown (UNPROVABLE)** | `filter_names = Cons "y" Nil` is NOT entailed (it contradicts `name_of e = "x"`). The model distinguishes "x" from "y" → **non-vacuous.** |

Type-check (`--type-only`, exit 0, no errors) independently confirms **`array string` /
`list string` are well-typed Why3 carriers** — the `array (array τ)` rejection noted in project
memory does NOT apply (string is a *pure* element type; only mutable elements in a pure type var
are rejected).

---

## 1. CLAIM A / CLAIM B verdict

**CLAIM A (the filtered-map-to-string-seq is not expressible today): CONFIRMED.**
Traced in source (not prose):
* `_content_comp` (expressions.py:7287) is the sole content-faithful comprehension router.
* Its filtered-projection branch fires **only** at `if has_if and _src_elem_cls is not None`
  (:7377) → `_filter_record_proj_law`. `_src_elem_cls` is set **only** for a
  `_record_array_params` source (:7364) producing `array <record>` with an **int** field
  projection (result carrier hard-coded `array int`, :7613/7623). An `array emit_ir` `.elts`
  source is not a record-array param → this branch never fires.
* The `is_var` / `isinstance(x, ast.Name)` filter is **not** a `_comp_cond_pure_bool`
  (:7457 whitelists only `< <= > >= == !=` numeric comparisons / boolean combinations) → the
  predicate never lifts.
* The element `x.id` → `name_of` is a **string**, so `_comp_elt_pure_int` (called :7343)
  returns False → `_content_comp` returns None → the comprehension **falls through to the
  opaque length-only `list_comp` path**. There is no `array string`/`seq string` filtered
  path anywhere.

So today the shape either degrades to an opaque length-only facade or type-mismatches where the
string list is consumed. Unexpressible as a faithful value. **CONFIRMED.**

**CLAIM B (why it is hard — "heterogeneous `.elts`, no per-element discriminant"): REFUTED as
stated; the real reason is different.**
The discriminant already EXISTS and already WORKS:
* `isinstance(x, ast.Name)` on an emit_ir child is already recognized and lowered to `(is_var x)`
  — expressions.py:4900-4904 via `_AST_CLASS_TO_IR_KIND` `"Name"→"Var"` (:995) and
  `_KIND_DISCRIMINANT` `"Var"→"is_var"` (:973); `is_var` is a total `let function` over the
  full emit_ir ADT (preamble.py:3585).
* `name_of` (preamble.py:3754) is the string projector `IrVar n → n`.
* Heterogeneity is therefore **not** the blocker: the emit_ir ADT already models the mixed
  Name/Starred/Attribute list, and my `observe_hetero` goal (Valid on both provers) shows the
  filter cleanly drops non-Name elements.

The **actual** difficulty is the one CLAIM B under-states: the **FILTER makes output length
data-dependent** (compaction), and the natural abstract-`val` existential law that survives
compaction is **positionally vacuous** (Part A: the empty-result model defeats every observation).
This matters because the existing `_filter_record_proj_law` precedent was "non-vacuous enough"
only via **consequence transfer** — its predicate `p.x > 0` constrains the *projected field*, so
`result[i] > 0` transfers (see `wl04d_filtered_record_proj_spike.mlw`). Here the predicate
`is_var e` says **nothing** about `name_of e`, so there is no consequence to transfer and nothing
observable survives. **Porting WL-04d naively to this shape would be a false-green vacuity
regression** — the reviewer's key warning.

---

## 2. THE VERDICT: **BREAKABLE** (via a compaction `function`, not the abstract-val law)

Can the filtered map be soundly extended to a non-vacuous `seq string` without a new axiom /
corpus perturbation / heterogeneity defeating it? **Yes — via the concrete compaction route,
NOT the abstract-existential-law route.**

* **Abstract-val existential law → NO** (Part A vacuous). Do not ship this; it is a facade for
  this predicate class.
* **Concrete compaction fixpoint → YES** (Part B). `filter_names` is a total, terminating,
  structural recursion composing the *already-concrete* `is_var`/`name_of`. It clears every §4
  constraint:
  - **No new axiom** — definitional `function` (Why3 termination via structural `variant`); the
    3-axiom ledger is untouched. The co-landed `src/formal-semantics/` certificate is a
    Phase2c/2d-style proof that `filter_names = Python filtered-list-comp semantics` — axiom-free.
  - **No corpus perturbation** — @mutable_state-gated (emitter model only) → byte-diff 0, exactly
    as the variadic content-law comp and `_filter_record_proj_law` are gated.
  - **Heterogeneity does not defeat it** — the emit_ir ADT already carries every `.elts`
    constructor; `is_var`/`name_of` dispatch over all of them (`observe_hetero` Valid).
  - **Non-vacuous & driver-observable** — `observe` Valid, `evil_twin` unprovable.

The asymmetry that makes this work — and that the map-only variadic comp could not exploit — is
that the FILTER+PROJECTION uses **only already-concrete projectors** (`is_var`, `name_of`),
whereas the map case (`[disp(e) for e in elts]`) had to stay abstract because the dispatcher's
value semantics are genuinely opaque. No opaque semantics enter here, so a concrete fixpoint is
available and is strictly stronger than any abstract law.

**Why not CERTIFIED-BOUNDARY:** the only thing the compaction fixpoint requires that the codebase
does not already have is (a) exposing the source as an inductive `irlist` rather than
`array emit_ir` for the structural recursion — and `IrMkTupleN` *already stores `.elts` as
`irlist`* (preamble comment expressions.py:936-944), so this is at hand — and (b) a monomorphic
`string`-list carrier to avoid polymorphic-`list` axiom explosion (mirror the `irlist` choice the
variadic comp already made). Both are bounded, well-founded builds, not walls.

---

## 3. Make-or-break SPIKE (BREAKABLE path)

Target: `_py_stmt_assign` Tuple branch —
`targets = [elt.id for elt in target.elts if isinstance(elt, ast.Name)]`.

1. **Carrier.** Add a monomorphic `strlist` (Nil/Cons string, mutually-independent of emit_ir) to
   `preamble.py` `_emit_exprir_theory` — same defensive choice as `irlist` for the variadic comp.
2. **Compaction function.** Emit, once per site (dedup by name), the axiom-free
   ```
   let rec function var_names_of (s: irlist) : strlist
     variant { s }
   = match s with
     | INil -> SNil
     | ICons e rest -> if is_var e then SCons (name_of e) (var_names_of rest)
                       else var_names_of rest
     end
   ```
   composing the EXISTING `is_var`/`name_of`. Recurses over the `IrMkTupleN` `irlist` payload.
3. **Wire the recognizer.** In `_content_comp`, add a filtered branch *before* the record-proj
   gate: when `src` is `array emit_ir`/`irlist`, the `if` is an `isinstance(x, ast.Name)`
   (→ `is_var`) via the `_KIND_DISCRIMINANT` chain already used at expressions.py:4900, and the
   element is `x.id` (→ `name_of`, string), emit `(var_names_of <elts>)` : `strlist`.
4. **Certificate.** `src/formal-semantics/Phase2X_VarNamesOf.{v,lean}` — `var_names_of` equals the
   Python `[e.id for e in l if isinstance(e, Name)]` under the abstraction map. Axiom-free.
5. **Observational driver** (mirror-mode, @mutable_state): construct the Tuple `(x, 5, y)`
   (Name/Num/Name); assert the emitted targets = `SCons "x" (SCons "y" SNil)` and observe the head
   `"x"`. **Evil-twin driver:** assert head `"z"` / targets `SCons "x" (SCons "z" SNil)` — must
   stay UNPROVEN. (My Part-B `observe` / `observe_hetero` / `evil_twin` goals are the reduced
   proof-of-concept of exactly this driver pair; they already pass/fail as required.)

If steps 1-4 land byte-diff 0 with the driver pair behaving as in Part B, the wall is broken for
this comprehension. (Per the report's own §1 note, `_py_stmt_assign` also needs `targets[0]`-head
+ symtab-membership + `raise` to FULLY convert; this spike clears the node-list-walker enabler
only, which is the wall under adjudication.)

---

## APPENDIX — oracle source (`scratchpad/filtered_string_wall.mlw`)

Part A models the abstract existential law (WL-04d shape ported to `array string`/emit_ir); Part B
the concrete compaction fixpoint. `is_var` modeled as `predicate`, `name_of` as
`function … : string`, matching the preamble's total projectors. `obs_len1` (Part A) times out /
unknown on both provers = vacuity; `observe`+`observe_hetero` (Part B) Valid; `evil_twin` (Part B)
times out = non-vacuous. Full file retained at the path above.
