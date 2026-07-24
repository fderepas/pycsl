# class-variant-impl.md — the class-instance VARIANT ADT carrier (driver-backlog item 3)

The §10.3 "isinstance-dispatch on a frozen-dataclass UNION + named-field reads" class.
A `\trusted` walker that dispatches on `isinstance(t, SomeDataclass)` over a UNION of frozen
dataclasses (the proof2why3 `Term` ADT) and reads `t.lhs`/`t.args`/… has **no existing
certified value model** (pyval's 2 discriminants `is_plist`/`is_pstr` cannot express `is_Var`
vs `is_App`; pyconst_val / stmt_ir / pyast_stmt model DIFFERENT Python types). This build lands
the class-instance-variant carrier, PROVEN + NON-FACADE, converts the first stub, and co-lands
the axiom-free Rocq+Lean certificate.

## §OUTCOME — 2026-07-24 driver run: BUILT + 1 conversion (count 933 → 932), residual [COST/SCALE]

**Verdict: the class-instance-variant carrier is BUILT, both spikes PASSED, and lands
`emit_why3.contains_unsupported` (a bool existence fold over the `Term` ADT) as the first
conversion. The census is done; the Term-ADT cluster is the SINGLE LARGEST reachable cluster
(~15-18 stubs), the CERT is axiom-free (ledger 3), and the remaining cluster stays [COST/SCALE]
behind the transform / string result-algebra carriers precisely enumerated below.**

### GATE-S census (lesson p) — NEW variant ADT required; cluster is the LARGEST reachable
Enumerated every existing certified value model — pyval (`PStr`/`PList`), pyconst_val (Phase2c
value-variant), the IR-node expr ADT (`_KIND_DISCRIMINANT`, dict `.get("type")` dispatch),
pyast_stmt, stmt_ir, pydict. **NONE carries a 9-way isinstance dispatch on distinct dataclasses:**
pyval's two discriminants can't tell `Var("x")` from `App("x",[])` (both would be `PList`), and
the others model different Python types. So a NEW variant ADT is unavoidable → §10.5 requires a
co-landing axiom-free certificate.

**Cluster size (the largest measured):** an AST scan of every `\trusted` mirror stub found the
proof2why3 `Term` union (Var|IntLit|BoolLit|App|BinOp|UnaryOp|Forall|Exists|Unsupported) is
dispatched by **~18 stubs** across FOUR files: `canonical.py` (10 Term→Term transforms:
`substitute`, `_ac_normalize`, `_alpha_rename`, `_flip_comparisons`, `_dedup_arrow_chain`,
`_sort_arrow_hypotheses`, `_flatten_foralls`, `_normalize_names`, `_iff_app_to_binop`,
`_expand_nat_to_int`), `ir.py` (`free_vars`, `flatten_arrow_chain`), `emit_why3.py` (`_pp` str-build,
`contains_unsupported` bool-fold), `crosscheck_ir.py` (`any_unsupported`, `all_present_unsupported`).
THREE result algebras: **bool fold** (contains_unsupported/any/all), **Term→Term transform**
(constructor emission), **string build** (`_pp`). A SECOND, distinct ADT (`Module2_Parser._csl_to_str`
over `CSLNode` = Var|Number|BinOp) uses `str(int(node.value))` = the `str_to_int` oracle → a separate
[CORRECTNESS] wall, not this ADT.

### Make-or-break spikes — BOTH PASSED
- **CERT / CORRECTNESS spike (cheap):** hand-wrote the full 9-constructor `term` variant + all THREE
  result algebras (bool fold, Term→Term transform w/ constructor emission, string build) in a
  standalone `.mlw`. **Every VC Valid** under Alt-Ergo + z3, structurally terminating (`variant { t }`
  / `variant { l }`), the `is_var_faithful` discriminant lemma Valid (z3; Alt-Ergo times out on the
  string disequality, lesson 19). Why3 ACCEPTS `App string (list term)` + `Forall (list string) string
  term`. **NO 4th axiom** — the variant + measures are all DEFINED / Why3-intrinsic. So the frontier is
  **[COST/SCALE], NOT [CORRECTNESS].**
- **RECOGNIZER falsifier (lesson q, the decisive one):** ported `contains_unsupported` VERBATIM into
  the mirror, emitted — the baseline is VACUOUS: `term: int` (erased), every `isinstance(term, Cls)`
  lowers to `isinstance_op 0 0` (hash constants, all branches undistinguished, lesson l), field reads
  to opaque `get_lhs term`, the `any(genexp)` to an opaque `_any_fold`, L3-tc FAILS. So the recognizer
  gap is real and is the session-scale wall (the cert is the easy part, lesson q).

### What was BUILT (all in `src/pycsl`, NOT the mirror → 0 new stubs; ledger 3)
- **`compute_term_adt_spec(functions, type_decls)`** (`generic_fold.py`) — builds the `term` variant
  spec (constructor set + per-field WhyML types) from the IMPORTED dataclass `type_decls` + the file's
  fold-recursion usage. The IR degrades the recursive annotations (`Term`→`Any`, `Tuple[Term,...]`→
  `tuple`, `Tuple[str,...]`→`tuple`); recovered deterministically: `Any`→`term`; a `tuple` field is
  `list term` iff SOME fold does `any(self(x) for x in p.<field>)` (the recursion signal), else `list
  string`; `str/int/bool`→`string/int/bool`. Fail-closed (un-typeable field → None → carrier off).
- **`recognize_term_isinstance_fold` + `emit_term_isinstance_fold_group`** (`generic_fold.py`) — the
  bool existence fold (`contains_unsupported` shape): an if-chain of `isinstance(p, Cls | (A,B,C))`
  guards each returning `True/False | self(p.F) | self(p.A) or self(p.B) | any(self(x) for x in p.F)`,
  TOTAL over the ctor set (fail-closed `_PVWBail` on any node outside the fragment). Emitted as a TOTAL
  positional `match v_p with | App _ v_args -> {n}__list v_args | BinOp _ v_lhs v_rhs -> ({n} v_lhs) ||
  ({n} v_rhs) | ... end` (+ a `{n}__list` list helper when an `any(...)` arm is present). Structural
  `variant { v_p }` / `variant { l }` — termination Why3-intrinsic, NO measure, NO axiom.
- **`_emit_term_theory`** (`preamble.py`) — emits the `type term = <ctors>` variant (gated on
  `needs_term`; pulls `string.String` + `list.List`). Computed once in `_scan_preamble_needs`, stashed
  on `self._term_adt_spec` so theory + dispatch share the SAME spec.
- **dispatch** (`functions.py`) — tried before `recognize_type_existence`; gated on `self._term_adt_spec`.
- **Co-landing certificate** (§10.5): `src/formal-semantics/rocq/Phase2i_TermIR.v` (+ `_CoqProject`) and
  `src/formal-semantics/lean/PyCSL/TermIR.lean` (+ `PyCSL.lean` import). Certifies the load-bearing
  facts the total-match + positional-projection lowering relies on: the inductive is well-formed (the
  recursor `term_rect` / `Term.rec` EXISTS ⇒ the WhyML `variant` structural recursion terminates); the
  constructors are OBSERVABLY DISTINCT (`term_kind` exact per ctor + discriminate lemmas ⇒ non-
  overlapping match arms = faithful isinstance dispatch); the constructors are INJECTIVE on the slots
  the emitter binds positionally (`Var`/`App`/`BinOp`/`UnaryOp`/`Forall` ⇒ `t.lhs`/`t.args` project the
  real child). **AXIOM-FREE:** Rocq `Print Assumptions` = "Closed under the global context" ×9; Lean
  `#print axioms` = "does not depend on any axioms" ×14. The WhyML uses a STRUCTURAL variant, so NO size
  measure is certified (unlike pyval's bespoke `hval_list` — the child is the standard `list term`).
  **Ledger stays 3** (no `proof_axiom_allowlist.py` edit).

### Gate battery (driver-verified fresh)
- count 933 → **932** (`contains_unsupported` un-`\trusted`); ledger **3** (both certs axiom-free;
  `proof_axiom_allowlist.py` untouched).
- `--fun contains_unsupported` **SUCCESS** (all VCs Valid incl. the `{n}__list` variant decrease);
  **whole-file** `emit_why3.py` proof **SUCCESS** (added to the suite array — lesson 10 full-file gate).
- L3-tc ✓ (whole file). Vacuity `--emit` exit 0: **0 input-blind**, no NEW erasure (`contains_unsupported`
  reads `v_term`; the 3 KNOWN erasures unchanged).
- **corpus byte-diff 0** (796 common == 796, mine vs detached-HEAD worktree with `.venv` symlinked,
  IDENTICAL). The recognizer is fail-closed + gated on `needs_term` → fires on 0 corpus programs.
- mirror-check **52/52**; drift **2 == HEAD** (`contains_unsupported` verbatim = in sync; the 2
  pre-existing `_handle_var_expr` / `_handle_for_stmt` still-blocked).
- **MUTATION TEST (Gate C, decisive):** `Unsupported: return True` → `return False` flips the emitted
  `Unsupported _ _ -> true` to `-> false`; changing `UnaryOp: self(term.arg)` → `self(term.body)` flips
  the emitted `UnaryOp _ v_arg -> {n} v_arg` to `UnaryOp _ _ -> {n} v_body`. Non-facade (no int-hash /
  oracle to hide behind — the match reads the real variant fields positionally).
- reference fixture (`git add -f`): `0950_class_variant_bool_fold.py` — a standalone
  `Expr = Leaf | Bad | Neg | Pair` bool fold that fires the carrier and PROVES (regression lock). No
  evil-twin (the carrier forces `ensures True`, no oracle to collapse to; mutation test + vacuity are
  the non-vacuity lock — the pyval-walker precedent).

## §RESIDUAL — the rest of the Term-ADT cluster ([COST/SCALE], carriers enumerated)
The carrier CURRENTLY reaches the **bool existence fold** only (`contains_unsupported`; `any_unsupported`
/ `all_present_unsupported` are methods on a crosscheck class — the same bool algebra, reachable with a
small self-state extension). The other two result algebras need distinct, still-unbuilt emitter carriers
(each a real feature, not a facade; all CERT-covered by the SAME `term` inductive — no new cert):
- **T-transform — Term→Term (constructor emission):** the 10 `canonical.py` transforms
  (`substitute`, `_flip_comparisons`, …) return a REBUILT `Term` (`BinOp o (flip a) (flip b)`). The
  cert already covers it (the spike's `flip` proved Valid); the recognizer must translate the
  constructor-CALL arms + the mutable-accumulator find-loops some transforms use. The single biggest
  count sub-cluster.
- **T-string — `_pp` string build:** `_pp` interpolates fields via f-strings + `str(int)` + a
  precedence `parent_prec: int` second param + a `_BINOP_PREC` dict lookup. Needs the string-build
  recognizer over `term` (the `emit_frt_group` `str_concat_op` precedent) + f-string-of-field lowering.
- **T-set/list returns:** `free_vars` (returns a `set`), `flatten_arrow_chain` (returns a tuple/list).
  Different result algebras again.

Each is a bounded feature the funded window CAN pay (no 4th axiom — the `term` cert covers the whole
ADT; Why3 accepts the variant). This run banked the certified carrier + cert + the bool-fold conversion;
the transform/string recognizers are the next increments. `Module2_Parser._csl_to_str` (the CSLNode
ADT) stays [CORRECTNESS] (its int is `str_to_int` = the oracle, no-more-int).
