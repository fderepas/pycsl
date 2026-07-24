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

## §OUTCOME-T — 2026-07-24 driver run: T-transform BUILT + 1 conversion (932 → 931)

**Verdict: the Term→Term (constructor-rebuild) transform algebra is BUILT, the spike
PASSED, and it converts `canonical.py::_flip_comparisons` (932 → 931). NO new certificate
(the SAME `Phase2i_TermIR.v`/`TermIR.lean` inductive covers it); ledger stays 3; `val
pystr_eq` is an uninterpreted `val`, NOT an axiom. src/formal-semantics/ + proof_axiom_allowlist.py
UNTOUCHED.**

### GATE-S census — the transform-algebra-ALONE cluster is SMALL (1 clean, not "most of 10")
Of the 10 canonical.py Term→Term stubs, only stubs reachable by constructor-rebuild + recursion +
simple guards **with NO cross-call to an un-built callee and NO extra value shape** count. Measured:
- **`_flip_comparisons` — REACHABLE, CLEAN. CONVERTED.** Pure structural rebuild; the only tweak is
  the BinOp op-swap via the certified str→str module constant `_FLIP_COMPARISON` (`module_const_dicts`).
- **`_iff_app_to_binop` — RESIDUAL [COST/SCALE].** Needs `len(t.args)==2` + `t.args[0]/[1]` index →
  a nested list-pattern `Cons a0 (Cons a1 Nil)`; the spike (`ttransform_spike2.mlw`) proved `flip`
  Valid (0.24s) but `iff_app` TIMES OUT on BOTH alt-ergo AND z3 (the structural-variant termination
  VC on deep nested-pattern subterms `a0`/`a1` blows up: 6.4M steps). Two extra recognizer features
  (list-len-guard, list-index) + a proof-cost wall → not clean.
- **The other 8 are OUT (cross-call / extra value shape), NOT transform-algebra-reachable:**
  `substitute` (Dict[str,str] map param + `.get`), `_alpha_rename` (cross-calls `substitute` + mutable
  counter + f-string), `_expand_nat_to_int`/`_dedup_arrow_chain`/`_sort_arrow_hypotheses`/`_flatten_foralls`
  (cross-call the still-`\trusted` `mk_arrow_chain`/`flatten_arrow_chain`), `_ac_normalize` (closure +
  `sorted` + `.pp()`), `_normalize_names` (cross-calls `_camel_to_snake`/`substitute`/`_normalize_type_string`
  + string ops), `canonicalize` (cross-calls ALL). So the T-transform-ALONE cluster = **1**; the rest wait
  on the T-string (`_pp`), map-param, and cross-call-callee carriers.

### Make-or-break spike — PASSED (CORRECTNESS clean)
- Hand-wrote `flip` (= `_flip_comparisons`) as a PROGRAM `let rec` over the 9-ctor `term` variant with the
  op-swap via `val pystr_eq`: **flip'vc Valid** (alt-ergo, 0.24s), structural `variant { v_t }` / list helper
  `variant { l }`, NO axiom (pystr_eq is a `val`, not an `axiom`). String equality on the `string` op field
  in COMPUTABLE position is the blocker (Why3 `string.String` gives only LOGICAL `=`); SOLVED by the
  already-trusted, ledger-neutral abstract `val pystr_eq (a b: string): bool` (used by the pydict readers),
  which forces a **program `let rec`** (not the bool-fold's logic `let rec function`).
- BASELINE VACUITY confirmed: the verbatim body lowers to `_flip_comparisons (t: int)`, `isinstance_op 0 0`
  (hash constants), `subscript_get _FLIP_COMPARISON (get_op t)` (int-hash), and FAILS L3-tc — the wall is real.

### What was BUILT (all source-only in `src/pycsl`, NOT the mirror → 0 new stubs; ledger 3)
- **`recognize_term_isinstance_transform` + `emit_term_isinstance_transform_group`** (`generic_fold.py`) — the
  Term→Term algebra: identity leaf arms (`return t` → `v_t`), single-ctor rebuild (COPY `t.F`→`v_F`, REC
  `self(t.F)`→`{n} v_F`, MAPREC `tuple(self(x) for x in t.F)`→`{n}__list v_F`), the SAME-KIND rebuild idiom
  (`kind = A if isinstance(t,A) else B; return kind(...)` → two arms each rebuilding its own ctor), and the
  const-map conditional (`if t.op in _MAP: return Ctor(_MAP[t.op], …)` → an `if pystr_eq v_op "<k>" then …`
  chain, contents from `module_const_dicts`). TOTAL positional `match` over the ctor set, PROGRAM `let rec`
  + `{n}__list` list helper, structural `variant` — NO measure, NO axiom. Fail-closed `_PVWBail`.
- **`_term_field_names_selfiter` generalized** (`generic_fold.py`) — now detects a self-recursive genexp under
  ANY wrapper (`tuple(...)` for a transform, not only `any(...)` for a bool fold), so `App.args` types as
  `list term` (the recursion signal is `self(x)` applied to the elements — binder-string lists never self-recurse).
- **dispatch** (`functions.py`) — transform tried before the bool fold (disjoint: transform returns the union
  type, fold returns bool); gated on `self._term_adt_spec`.
- **preamble** — `_scan_preamble_needs` sets `needs_term` for a transform too, stashes `self._term_const_dicts
  = ir["module_const_dicts"]`, and flags `needs_term_streq`; `_emit_term_theory` appends `val pystr_eq` under
  `needs_term_streq` when pydict isn't already declaring it.
- **Certificate: UNCHANGED.** The `term` inductive's well-formedness / distinctness / injectivity (the
  facts the total-match + positional-projection rely on) are ALREADY certified axiom-free in `Phase2i_TermIR.v`
  / `TermIR.lean`. Constructor EMISSION uses the same constructors; no new fact. Ledger stays 3.

### Gate battery (driver-verified fresh)
- count 932 → **931** (`_flip_comparisons` un-`\trusted`); ledger **3** (no cert/allowlist/formal-semantics edit).
- `--fun _flip_comparisons` **SUCCESS**; **whole-file** `canonical.py` proof **SUCCESS** (all VCs Valid incl.
  `_flip_comparisons'vc`, `_flip_comparisons__list'vc`, `alpha_normalize'vc`). L3-tc ✓ whole file.
- **corpus byte-diff 0** (797 common == 797, mine vs detached-HEAD worktree, `.venv` symlinked, IDENTICAL) —
  the recognizer is fail-closed + gated on `needs_term`.
- Vacuity `--emit` exit 0: **0 input-blind**, no NEW erasure (`_flip_comparisons` reads `v_t`; the 3 KNOWN
  erasures unchanged).
- mirror-check **52/52**; drift **2 == HEAD** (`_flip_comparisons` verbatim = in sync; the 2 pre-existing
  `_handle_var_expr` / `_handle_for_stmt` still-blocked).
- **MUTATION TEST (Gate C, decisive):** map value `>=`→`>>` flips emitted `BinOp ">="`→`BinOp ">>"` (const-map
  contents genuinely flow); dropping `UnaryOp(t.op, self(t.arg))`→`UnaryOp(t.op, t.arg)` flips `UnaryOp v_op
  (_flip_comparisons v_arg)`→`UnaryOp v_op v_arg`. Non-facade (real variant fields, no int-hash/oracle).
- reference fixture (`git add -f`): `0951_class_variant_term_transform.py` — a standalone
  `Expr = Leaf | Neg | Bin | Quant` flip transform (identity + rebuild + condmap + list-string-binder rebuild)
  that fires the carrier and PROVES (regression lock). No evil-twin (carrier forces `ensures True`; mutation
  test + vacuity are the non-vacuity lock — the 0950 precedent).

## §OUTCOME-TL — 2026-07-24 driver run: T-set/list LEAF algebras BUILT + 3 conversions (931 → 928)

**Verdict: the T-set/list LEAF algebras over `term` are BUILT and convert the `ir.py` leaf
utilities `mk_arrow_chain` (list-fold BUILDER, 930), `flatten_arrow_chain` (while-spine TUPLE
return, 929), and `free_vars` (set-fold, 928). All three lower onto the SAME certified
`Phase2i_TermIR` inductive — NO new value shape, NO new certificate; ledger stays 3.
src/formal-semantics/ + proof_axiom_allowlist.py UNTOUCHED.**

**SHARED-LEAF CASCADE (§10.4, benign):** the leaves live in `proof2why3/ir.py` and are IMPORTED by
`canonical.py`, `emit_why3.py`, `parser.py`. Converting them changes every importer's emission (the
`val` stub → the full definition inlined). Verified all three needs_term importers still prove
whole-file SUCCESS (`emit_why3.py`, `canonical.py`, `ir.py`) and `parser.py` (not suite-gated)
L3-tc ✓ — no cascade regression. The App.args/Forall.binders faithfulness fix (below) affects only
the `term` VARIANT theory those files already emit; corpus byte-diff stays 0.

**FAITHFULNESS FIX (`App.args`, `Forall`/`Exists.binders`):** the mirror stub-gen degraded
`Tuple[Term,...]`→`int` and `Tuple[str,...]`→`int`. `free_vars` needs `App.args` typed `list term`
(the `for a in t.args` self-recursion) and `binders` typed `list string` (`set(t.binders)`). Fixed
the mirror dataclass fields to MATCH LIVE (`args: Tuple['Term', ...]`, `binders: Tuple[str, ...]`) —
mirror-check compares param COUNTS not field types, so no drift; the fix is more faithful (reduces
mirror↔live divergence). Extended `_term_field_names_selfiter` to detect For-LOOP self-recursion
(`for a in <p>.F: … <self>(a) …`), not only genexps, so `App.args` types `list term` in the set-fold.

### GATE-S census — 3 reachable leaves; the cascade CALLERS stay [COST/SCALE]
The leaf set (`mk_arrow_chain`/`flatten_arrow_chain`/`free_vars`; `substitute` is a separate
`Dict[str,str]` map-param carrier) — reachability by a T-set/list algebra over the `term` ADT ALONE:
- **`mk_arrow_chain(hyps: List[Term], conclusion: Term) -> Term` — REACHABLE, CLEANEST.** A
  (`list term`, `term`) accumulator fold that BUILDS a right-leaning chain via `Bin("->", h, out)`.
  No new value shape (result = `term`, the T-transform algebra). Spike (`spike_mac.mlw`) all VCs
  Valid Alt-Ergo, structural `variant { l }`, NO axiom.
- **`flatten_arrow_chain(t: Term) -> Tuple[List[Term], Term]` — REACHABLE.** A while-spine walk down
  the `->` chain, structural recursion over the term spine returning `(list term, term)` (Why3-native
  tuple). Spike (`spike_fac.mlw`) all Valid, `variant { v_cur }`, only abstract symbol a VC-free
  `val __streq` (the T-transform `pystr_eq` precedent), NO axiom.
- **`free_vars(t: Term) -> set` — REACHABLE, CONVERTED.** A set-of-strings catamorphism
  (singleton/`|`-union/`-`-diff over `map string bool`, the ALREADY-CERTIFIED L1 set repr). Spike
  (`spike_fv5.mlw`) all Valid with STRUCTURAL mutual `variant { v_t }` / `variant { l }` (the fold
  emitter precedent — NO size-lemma pack needed, unlike the first `spike_fv2` attempt). `__set_add`
  is a BARE abstract `val` (no `ensures` → not even an assumed fact; maximally axiom-free). NO new cert.
- **The cascade CALLERS stay [COST/SCALE] — the leaves did NOT unblock them.** Re-census of the 4
  `canonical.py` transforms that cross-call the now-converted leaves: `_expand_nat_to_int` (a
  genexp `[BinOp(">=", Var(b), IntLit(0)) for b in t.binders]` building a `list term` from a binder
  `list string` + the `mk_arrow_chain` call — a genexp-to-termlist feature the transform recognizer
  lacks), `_dedup_arrow_chain` (a `not in`-membership dedup loop over `list term` — term-equality +
  list-search), `_sort_arrow_hypotheses` (`sorted` closure), `_flatten_foralls` (mutable hyp
  gather-loop). Each carries an INDEPENDENT wall beyond the leaf call; the leaf conversions are the
  yield, not a cascade.

### What was BUILT (all in `src/pycsl`, NOT the mirror → 0 new stubs; ledger 3)
- **`recognize_term_list_build` + `emit_term_list_build_group`** (`generic_fold.py`) — the
  (`list term`, `term`) accumulator BUILDER: parses `acc = seed; for h in [reversed(]list[)]: acc =
  Ctor(… h … acc …); return acc`, emits a structural `{n}__go (l: list term) (acc: term): term` fold
  (`reversed` => foldr wrapping `{n}__go rest`; plain => foldl threading the acc). The ctor-build
  expression is parsed to a nested AST over the `term` spec ctors (fail-closed `_PVWBail`).
- **`recognize_term_flatten_arrow` + `emit_term_flatten_arrow_group`** (`generic_fold.py`) — the
  while-spine TUPLE walker: `list=[]; cur=t; while isinstance(cur,BinOp) and cur.op==LIT:
  list.append(cur.<f1>); cur=cur.<f2>; return list,cur` → a structural `{n}__go (v_cur: term) (acc:
  list term): (list term, term) variant { v_cur }` + inline DEFINED `{n}__app` list append + VC-free
  `val {n}__streq`.
- **needs_term gate** (`preamble.py`) — both leaf recognizers set `needs_term` (same `term` theory).
- **dispatch** (`functions.py`) — tried after the transform/fold, gated on `self._term_adt_spec`.
- **suite** (`run-self-annotation-suite.sh`) — `proof2why3/ir.py` added to the FULL-FILE proof gate.

### Gate battery (driver-verified fresh, per conversion)
- count 931 → **930** (`mk_arrow_chain`) → **929** (`flatten_arrow_chain`) → **928** (`free_vars`);
  ledger **3** (no cert/allowlist/formal-semantics edit — `git diff` EMPTY).
- **whole-file** proof **SUCCESS** for all three needs_term files (`ir.py` — the conversions; plus
  the shared-leaf importers `emit_why3.py` + `canonical.py`, re-proven with the inlined defs). L3-tc
  ✓ whole file. Full self-annotation SUITE PASS.
- **corpus byte-diff 0** (798 common == 798, mine vs detached-HEAD worktree with `.venv` symlinked,
  IDENTICAL; only the new 0952–0957 fixtures are mine-only). All recognizers fail-closed + gated on
  `needs_term`/`needs_term_setfold` → fire on 0 corpus programs.
- Vacuity `--emit` exit 0: 0 input-blind, no NEW erasure (all three leaves read their params; the 3
  KNOWN erasures unchanged).
- mirror-check **52/52**; drift **2 == HEAD** (all bodies verbatim = in sync; the 2 pre-existing
  `_handle_var_expr`/`_handle_for_stmt` still-blocked).
- **MUTATION TEST (Gate C, decisive):** `mk_arrow_chain` ctor `"->"` → `"~>"` flips emitted `Bin
  "->" v_h …` → `Bin "~>" …`; `flatten_arrow_chain` `cur.lhs` → `cur.rhs` flips emitted `Cons v_lhs
  Nil` → `Cons v_rhs Nil`; `free_vars` `-`→`|` flips emitted `set_diff` → `set_union` in the Quant/
  Forall arm. Non-facade (real variant fields, no int-hash/oracle).
- fixtures (`git add -f`): `0952`/`0953` (list-build + ctor-string twin), `0954`/`0955` (flatten +
  append-field twin), `0956`/`0957` (free_vars + diff-vs-union twin) — all PROVE; each twin is the
  mechanical non-facade lock (byte-different emission for the discriminated knob).

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

## §OUTCOME-TS — 2026-07-24 driver run: T-string BUILT + 1 conversion (928 → 927), the ir.py per-class pp family is a RECORD-BRIDGE [COST/SCALE] boundary

**Verdict: the term→string BUILD catamorphism (the `_pp` shape) is BUILT, the spike
PASSED, and it converts `emit_why3._pp` (928 → 927) — the single-function member of the
pp/pretty-print family. NO new certificate (the SAME `Phase2i_TermIR` inductive covers it);
ledger stays 3; `val pystr_eq`/`str_concat_op`/`str_of_int` are uninterpreted `val`s, NOT
axioms. src/formal-semantics/ + proof_axiom_allowlist.py UNTOUCHED.**

### GATE-S census — REFUTES the target's "~7 stub" framing: 1 single-function + 5 record-bridge
The target expected the whole pp/`_pp` family (~7) reachable by "the term→string catamorphism
ALONE". The AST census REFUTES this — the family splits into TWO structurally-distinct shapes:
- **`emit_why3._pp` — a SINGLE-FUNCTION isinstance-dispatch catamorphism** (`_pp(t: Term,
  parent_prec: int) -> str`), the same shape the existing term recognizers use (like
  `contains_unsupported`). REACHABLE — **CONVERTED (927).** It carries a precedence sub-algebra
  beyond a plain string build: a threaded inherited-attribute int param (`parent_prec`), a
  `_BINOP_PREC` str→int const-table lookup, int arithmetic (`op_prec + 1`), an int comparison +
  conditional paren-wrap (`f"({s})" if parent_prec > op_prec`), plus two list-joins (binder
  `list string` + App-arg `list term` with recursion). All SOUND (no oracle, no 4th axiom).
- **`ir.py` App/BinOp/UnaryOp/Forall/Exists `.pp` (5 stubs) — NOT reachable by the catamorphism
  ALONE. [COST/SCALE] RECORD-BRIDGE boundary.** These are per-variant METHODS on the frozen-
  dataclass RECORD types (`app__pp (self: app)` where `type app = { head: string; args: array
  int }`), recursing via VIRTUAL dispatch `a.pp()` on `Term`-typed subterms. The record model
  ERASES the recursive children to `array int`/`int` — there is NO faithful bridge to the `term`
  variant `App string (list term)`. Converting them needs a distinct capability: (a) a record-
  field-type fix so a term-ctor dataclass's record fields emit the VARIANT field types (`args:
  list term`, `lhs/rhs: term` — the `compute_term_adt_spec` types), (b) a SYNTHESIZED unified
  `pp_term (t: term): string` catamorphism assembled from the 9-method family, and (c) each
  `cls__pp` emitted as `pp_term (Ctor self.<fields>)` (record→variant injection). It is
  co-dependent across the whole family (you cannot convert `App.pp` alone — the virtual
  `a.pp()` needs the unified `pp_term`), so it violates one-stub-per-commit without staging, and
  the record-field-type change has corpus-byte-diff exposure. REOPEN: build the record⇄variant
  bridge + synthesized `pp_term` + per-class delegation; do it once for all 5. No 4th axiom
  (Why3 accepts the variant) — a bounded but genuinely-distinct session-scale build.

There is NO other term→string single-function catamorphism in the mirror (canonical.py = 10
Term→Term transforms; crosscheck_ir = bool folds). So the T-string-single-function cluster = 1.

### Make-or-break spike — PASSED (CORRECTNESS-clean, sound; whole-body PROOF, not just tc)
BASELINE (verbatim port, `--no-proof`): the vacuous int-hash wall — `_pp (t: int) (parent_prec:
int)`, every `isinstance_op 0 0` (hash constants), string literals as hash ints, `str_concat:
int×int→int`, `_BINOP_PREC_get_2` opaque; L3-tc FAILS. Wall real, sound to break (all features
DEFINED/Why3-intrinsic). BUILT the recognizer → the emitted `_pp` is a REAL fold over the
certified `term` inductive:
```
let rec _pp (v_t: term) (parent_prec: int) : string variant { v_t }
= match v_t with
  | App v_head v_args -> (if (match v_args with Nil -> true | Cons _ _ -> false end) then v_head
      else (let l_args_s = (_pp__joinargs " " v_args (8)) in ...
            (if (parent_prec > 7) then (str_concat_op "(" (str_concat_op l_s ")")) else l_s)))
  | BinOp v_op v_lhs v_rhs -> (let l_op_prec = (_pp__binop_prec_BINOP_PREC v_op) in
      (let l_lhs = (if (pystr_eq v_op "->") then (_pp v_lhs ((l_op_prec + 1)))
                    else (_pp v_lhs (l_op_prec))) in ...))
  | IntLit v_value -> (str_of_int v_value)  | Var v_name -> v_name  | ... end
with _pp__joinargs (sep: string) (l: list term) (pr: int) : string variant { l } = ...
```
Real reads throughout (`v_op`/`v_head`/`v_args`, `pystr_eq v_op "->"`, the recursion `_pp v_lhs
…`, `str_of_int v_value`); NO int-hash, NO `any_1`, NO oracle. `--fun _pp` **SUCCESS**;
**whole-file** `emit_why3.py` proof **SUCCESS** (all `_pp'vc` / `_pp__joinstr'vc` /
`_pp__joinargs'vc` sub-goals Valid, structural `variant { v_t }` / `variant { l }`; the
str-build `val`s spec'd by `concat`, NO axiom). L3-tc ✓ whole file.

### What was BUILT (all source-only in `src/pycsl`, NOT the mirror → 0 new stubs; ledger 3)
- **`collect_module_const_int_dicts`** (`frontend/module_collect.py`) — the str→int analogue of
  `collect_module_const_dicts` (`_BINOP_PREC = {"->": _PREC_ARROW, ...}`, int-const values
  resolved via `collect_module_constants`). New IR field `module_const_int_dicts`, wired in
  Module5. Consumed ONLY by the term-pp emitter (gated on the recognizer) → corpus-inert.
- **`recognize_term_string_pp` + `emit_term_string_pp_group`** (`generic_fold.py`) — a genuine
  fragment-grammar STRUCTURAL translator (not a shape matcher) over the `term` ADT: per-arm
  blocks with intra-arm local `let`s, parallel conditional assigns (`if op=="->"` lhs/rhs), an
  early-return guard (`if not args`), a string sublanguage (lit / field / `str()` / bool-ifexpr /
  f-string→`str_concat_op` / list-string join / term-list join-with-recursion / conditional
  paren-wrap) and an int sublanguage (lit / module-const / threaded param / `+N` / `dict.get`).
  Fail-closed `_PVWBail`. Inline TOTAL `{n}__joinstr` + `{n}__binop_prec_<dict>` + mutual
  `{n}__joinargs`; PROGRAM `let rec` (calls `val pystr_eq`), structural `variant`, NO axiom.
- **`recognize_term_pp_wrapper` + `emit_term_pp_wrapper_group`** (`generic_fold.py`, §10.4
  cascade) — `ir_to_whyml_axiom_body` (the sole caller of `_pp`, a VERIFIED sibling) delegates
  `return _pp(term, _PREC_TOP)`; it must now type its param as the `term` variant. Emitted as
  `let f (v_x: term): string = _pp v_x (0)`. Re-proven SAME commit (whole-file SUCCESS).
- **preamble** (`preamble.py`) — `needs_term` fires for a pp too; `needs_term_streq` (pystr_eq)
  and a new `needs_term_strbuild` (declare `str_concat_op` + `str_of_int` in the term theory)
  are OR-set from the pp descs; stashes `_term_const_int_dicts` / `_term_pp_names` / `_term_pp_mc`.
  A byte-safe `needs_array` gate: a term-ctor dataclass with a `tuple` field emits an `array int`
  RECORD field → pull `use array.Array` (gated on needs_term → corpus byte-identical; the term
  mirrors already pull Array). **dispatch** (`functions.py`) tried after the other term algebras.
- **Certificate: UNCHANGED.** The `term` inductive's well-formedness / distinctness / injectivity
  (the facts the total-match + positional-projection + structural `variant` rely on) are ALREADY
  certified axiom-free in `Phase2i_TermIR.v` / `TermIR.lean`. The string BUILD uses the same
  constructors as projectors; no new fact. Ledger stays 3.

### Gate battery (driver-verified fresh)
- count 928 → **927** (`_pp` un-`\trusted`); ledger **3** (no cert/allowlist/formal-semantics
  edit — `git diff` on proof_axiom_allowlist.py / src/formal-semantics EMPTY).
- `--fun _pp` **SUCCESS**; **whole-file** `emit_why3.py` proof **SUCCESS**; the other two
  needs_term mirrors re-proven no-cascade: `ir.py` **SUCCESS**, `canonical.py` **SUCCESS**. L3-tc
  ✓ whole file.
- **corpus byte-diff 0** (804 common == 804, mine vs detached-HEAD worktree with `.venv`
  symlinked, IDENTICAL; only the new 0958/0959 fixtures are mine-only). The recognizer +
  collector are fail-closed + gated on `needs_term` → fire on 0 corpus programs.
- Vacuity `--emit` exit 0: **0 input-blind**, no NEW erasure (`_pp` reads `v_t` + `parent_prec`;
  the 3 KNOWN erasures unchanged).
- mirror-check **52/52**; drift **2 == HEAD** (`_pp` verbatim = in sync; the 2 pre-existing
  `_handle_var_expr` / `_handle_for_stmt` still-blocked).
- **MUTATION TEST (Gate C, decisive):** the 0959 twin (Quant separator ` . ` → ` ; `) emits
  `str_concat_op … " ; " …` where 0958 emits `… " . " …` — the separator genuinely flows into
  the `.mlw`. Non-facade (real variant fields + real string ops, no int-hash / oracle to hide
  behind; the carrier forces `ensures True`, so mutation + vacuity are the non-vacuity lock).
- fixtures (`git add -f`): `0958_term_string_pp.py` (positive witness — exercises field read /
  `str()` / bool-ifexpr / f-string / binder-join / App-arg join-recursion / `_OPPREC` table /
  int-arith / conditional paren-wrap / `pystr_eq` guard; PROVES) + `0959_term_string_pp_twin.py`
  (the separator DISCRIMINATING TWIN; PROVES, byte-different emission).

### §RESIDUAL-after-TS — the pp family remaining ([COST/SCALE], the record-bridge)
`ir.py` App/BinOp/UnaryOp/Forall/Exists `.pp` (5) stay `\trusted` behind the RECORD⇄VARIANT
bridge above — a bounded but genuinely-distinct session-scale build (record-field-type fix +
synthesized `pp_term` + per-class injection/delegation, co-dependent across the family, with
corpus-byte-diff exposure). No 4th axiom (the `term` cert covers it). `Module2_Parser._csl_to_str`
(CSLNode ADT) stays [CORRECTNESS] (its int is `str_to_int` = the oracle).

## §OUTCOME-CC — 2026-07-24 driver run: crosscheck_ir self-state carrier BUILT + 1 conversion (922 → 921), rest [COST/SCALE]

**Verdict: the crosscheck_ir.py self-state boolean-predicate carrier is BUILT and
converts `IRCrossCheckResult.registry_skipped` (922 → 921) — the ONE method
reachable by presence/string-empty ALONE (no `term` inductive, no `term_eq`). The
correctness spike PASSED for the WHOLE sub-cluster (term_eq DEFINABLE, no 4th
axiom), so the frontier is [COST/SCALE]; the remaining 4 term-structural methods
stay `\trusted` behind a full-`term`-inductive-source + `term_eq`-emitter build,
precisely enumerated below. NO new certificate (no term theory emitted); ledger 3;
src/formal-semantics/ + proof_axiom_allowlist.py UNTOUCHED.**

### THREE emitter obstacles discovered (why this is not the "reuse Phase2i + a record" the target framed)
1. **`@property` methods are SKIPPED pre-IR** (`Module5._should_skip_method`) — the 6
   crosscheck `@property` stubs never reach WhyML, so removing `\trusted` alone would be a
   count-only FACADE. SOLVED cleanly by DROPPING `@property` in the MIRROR (both gates ignore
   decorators: mirror-check compares `(func, qualname, n_params)`; sync compares
   `ast.unparse(node.body)`) → the method emits as a normal `ircrosscheckresult__<m>` with a
   verbatim body. NO Module5 un-skip / no cross-file cascade.
2. **`Optional[Term]` fields ERASE the Term arm at IR** — Module5 desugars `Optional[Term]` into
   a synthesized `_union_..._N` variant whose `Term` arm is dropped as `Any` (GT1), leaving only
   `Arm_N_None` → the field is effectively a unit (`is not None` VACUOUS). SOLVED via the
   existing `_M5_OPTION_FIELD_ALLOWLIST` (class,field-keyed → corpus/other-mirror-inert): added
   the 3 `IRCrossCheckResult` canon fields + `_m5_get_option_field_inner` returns "opaque_term";
   Module6 maps value_type "opaque_term" → an inhabitable `option int` (opaque payload — faithful
   for a presence-only reader). `_has_opaque_term_fields` gate pulls `use option.Option`.
3. **`compute_term_adt_spec` cannot derive the `term` ADT here** — the file has NO isinstance-
   dispatch over the ctor set (methods use `==` (term_eq) + only `isinstance(c, Unsupported)` on a
   loop var), and imports only `Term`+`Unsupported` (not the 9 ctor dataclasses). So the certified
   `type term` inductive + `term_eq` CANNOT be sourced/emitted from this file's contents. This is
   the wall for the 4 term-structural methods (below).

### Make-or-break spike — PASSED (CORRECTNESS-clean, the WHOLE sub-cluster)
`scratchpad/cc_spike.mlw`: hand-wrote the `option term` self-state record + a program `let rec
term_eq`/`term_list_eq`/`strlist_eq` (structural mutual recursion, `variant { a }`/`{ xs }`) + the
5 method bodies (`any_unsupported`/`all_present_unsupported`/`registry_skipped`/`provers_agree`/
`all_agree`). **ALL 8 VCs Valid (alt-ergo)** incl. `term_eq'vc` (termination) — Why3 ACCEPTS
`option term` record fields + mutual-recursive term_eq; NO 4th axiom (`term_eq` DEFINED; `pystr_eq`
a `val`). Frontier = [COST/SCALE].

### What was BUILT (all source-only in `src/pycsl`, NOT the mirror → 0 new stubs; ledger 3)
- **`recognize_crosscheck_selfstate_bool` + `emit_crosscheck_selfstate_bool_group`**
  (`generic_fold.py`) — a 0-formal-param self method whose body is a single `return <bexpr>` over
  the STRICT fail-closed fragment `and|or|not(self.<strF>)|self.<optF> !=/== None`. Emits
  `(pystr_eq self.<strF> "")` for the string-empty test and inline `match self.<optF> with Some _
  -> true|false | None -> ...` for is_some/is_none over the opaque `option int`. TOTAL `let`,
  `ensures True`.
- **Module5** `_M5_OPTION_FIELD_ALLOWLIST` + `_m5_get_option_field_inner` ("Term"→"opaque_term").
- **Module6** `_emit_type_decls` option branch ("opaque_term"→`option int`); `_scan_preamble_needs`
  sets `_has_opaque_term_fields` + `needs_selfstate_streq`; `_emit_preamble_helpers` emits
  `val pystr_eq` (gated, never double-declared); `_emit_preamble_uses` pulls `use option.Option`
  under `_has_opaque_term_fields`. **functions.py** dispatch tries the recognizer first, gated on
  `_has_opaque_term_fields` → fires on 0 corpus + 0 other mirror files.
- **Certificate: NONE emitted** (no `type term`, no `term_eq` — the opaque `option int` payload
  needs no inductive). Ledger 3 unchanged.

### Gate battery (driver-verified fresh)
- count 922 → **921** (`registry_skipped` un-`\trusted`); ledger **3** (no cert/allowlist/
  formal-semantics edit).
- **whole-file** `crosscheck_ir.py` proof **SUCCESS** (added to the suite gate). L3-tc ✓ whole file.
- **corpus byte-diff 0** (808 common == 808, mine vs detached-HEAD worktree, `.venv` symlinked,
  IDENTICAL; only new 0962/0963 fixtures mine-only). **suite-mirror byte-diff 0** (36 common
  identical). All gated on `_has_opaque_term_fields`/allow-list → byte-inert everywhere else.
- Vacuity `--emit` exit 0: 0 input-blind, no NEW erasure (`registry_skipped` reads
  `registry_raw`/`rocq_canon`/`lean_canon`; the 3 KNOWN erasures unchanged).
- mirror-check **52/52**; drift **2 == HEAD** (`registry_skipped` verbatim = in sync; the 2
  pre-existing `_handle_var_expr`/`_handle_for_stmt` still-blocked).
- **MUTATION TEST (Gate C, decisive):** `rocq_canon`→`registry_canon` flips emitted `match
  self.registry_canon`; `registry_raw`→`rocq_raw` flips emitted `pystr_eq self.rocq_raw ""`.
  Non-facade (real record fields flow; no int-hash/oracle — carrier forces `ensures True`, so
  mutation + vacuity are the non-facade lock).
- fixtures (`git add -f`): `0962_crosscheck_selfstate_registry_skipped.py` (positive; PROVES) +
  `0963_..._twin.py` (registry_canon-vs-rocq_canon discriminating twin; PROVES, byte-different).

### §RESIDUAL-CC — the 4 term-structural methods stay [COST/SCALE] (reopening capability)
`any_unsupported`, `all_present_unsupported` (destruct `Unsupported`), `provers_agree`, `all_agree`
(structural `term_eq`) — REACHABLE (correctness spike PASSED) but each needs the certified 9-ctor
`term` inductive + (for the eq pair) a DEFINED `term_eq`/`term_list_eq` EMITTED in this file, which
`compute_term_adt_spec` cannot derive here (obstacle 3). REOPEN: (F3) a canonical-`term`-spec
SOURCE independent of isinstance-dispatch (e.g. import the ctor dataclasses in the mirror +
harvest the Term-subclass set) + (F4) a `term`-theory + `term_eq` EMITTER (a new defined-function
emit, gated). No 4th axiom (the `term` inductive is Phase2i-certified; `term_eq` is DEFINED). A
2-ctor `Unsupported|Other` collapse is a Gate-C FACADE (mutation test on `isinstance(c, Var)`
would not flow) → the FULL inductive is required. `pairwise` (returns `Dict[str, Optional[bool]]`)
is a distinct dict-result algebra on top of `term_eq`.

## §OUTCOME-F3F4 — 2026-07-24 driver run: F3+F4 BUILT + 4 conversions (921 → 917), the crosscheck term-structural cluster CLOSED

**Verdict: F3 (the certified `term` inductive made available in crosscheck_ir
WITHOUT an in-file isinstance-dispatch) + F4 (a DEFINED structural `term_eq`
emitter) are BUILT, the make-or-break spike PASSED, and ALL FOUR residual
term-structural methods convert: `any_unsupported` + `all_present_unsupported`
(F3-only, `isinstance(c, Unsupported)` over `option term`), `provers_agree` +
`all_agree` (F3+F4, structural `term_eq`). NO new certificate — the SAME
Phase2i `term` inductive (well-formed / distinct / injective, axiom-free)
covers `term_eq`; `pystr_eq` is a VC-free `val`, NOT an axiom. Ledger stays 3;
src/formal-semantics/ + proof_axiom_allowlist.py UNTOUCHED. This CLOSES the
§RESIDUAL-CC 4-method cluster.**

### GATE-S census + make-or-break spike — PASSED (CORRECTNESS-clean)
`scratchpad/cc_spike.mlw`: hand-wrote the 9-ctor `term` variant, the `option
term` self-state record, a program `let rec term_eq`/`term_list_eq`/`strlist_eq`
(structural mutual recursion, `variant { a }`/`{ xs }`), and the 4 method bodies.
**All 7 VCs Valid (alt-ergo)** incl. `term_eq'vc` (termination) — Why3 ACCEPTS
`option term` fields + mutual term_eq; NO 4th axiom. Census: `any_unsupported`/
`all_present_unsupported` need F3 only; `provers_agree`/`all_agree` need F3+F4.

### F3 — the certified term spec WITHOUT an in-file isinstance-dispatch
`compute_term_adt_spec` derives the `term` inductive from an isinstance-DISPATCH
over the imported ctor dataclasses. Obstacle 3 (§OUTCOME-CC) said crosscheck_ir
imports only `Term`+`Unsupported` → no dispatch → no spec. **SOLVED cleanly by
importing the full 9-ctor union in the MIRROR** (`from proof2why3.ir import App,
BinOp, BoolLit, Exists, Forall, IntLit, Term, UnaryOp, Unsupported, Var`):
imports are NOT diffed by the mirror-sync gate (module-level statements are
ignored), and the import ALSO pulls the module-level `free_vars`/`mk_arrow_chain`/
`flatten_arrow_chain` folds whose isinstance-dispatch seeds the EXACT certified
9-ctor spec (App.args : list term, BinOp lhs/rhs : term, Forall/Exists.binders :
list string — verified identical to emit_why3/canonical/ir). NO canonical-spec
fallback / hardcoded ctor set was needed (that would have risked a facade) — the
spec is genuinely derived from the imported dataclasses + their fold usage. The
`Optional[Term]` canon fields then become the FAITHFUL `option term` (Module6
`opaque_term` branch, gated on `_term_adt_spec` present — else the §OUTCOME-CC
`option int` presence-only degrade).

### F4 — the DEFINED structural `term_eq` emitter
`_emit_term_eq_defs` (preamble.py) generates `term_eq`/`term_list_eq`/`strlist_eq`
GENERICALLY from the term spec (per-ctor arm ANDs the field-wise equality chosen
by each field's WhyML type: string→pystr_eq, int→`=`, bool→iff, term→term_eq,
list term→term_list_eq, list string→strlist_eq), TOTAL, structural `variant`
(Why3-intrinsic termination over the Phase2i-certified inductive — NO measure, NO
axiom). Gated on `needs_term_eq` = a CONVERTED eq-method present (a still-
`\trusted` stub body `return False` never matches the recognizer) → term_eq
emits ONLY once `provers_agree`/`all_agree` are converted.

### What was BUILT (all source-only in `src/pycsl`, NOT the mirror → 0 new stubs)
- **`recognize_crosscheck_term_method` + `emit_crosscheck_term_method_group`**
  (`generic_fold.py`) — STRICT fail-closed recognizers for the 4 shapes (ANY
  genexp with inline `!= None` filter; LISTCOMP-QUANT `canons=[...]; if not
  canons: return False; all/any(...)`; PROVERS `if F1 is None or F2 is None:
  return True; return F1 == F2`). `isinstance(c, Ctor)` → a `Some (Ctor _..)`
  arm (arity from the spec); `c == d` → `term_eq`; `c == canons[0]` → a
  first-present nested destructure. Reads the ACTUAL fields / quantifier /
  isinstance target / eq operands (mutation-flowing, non-facade).
- **Module6** (`preamble.py`): `opaque_term` → `option term` when `_term_adt_spec`;
  `_emit_term_eq_defs` under `needs_term_eq`; pystr_eq never double-declared
  (excluded when `needs_selfstate_streq` already emits it).
- **dispatch** (`functions.py`): tried after the selfstate-bool recognizer,
  gated on `_has_opaque_term_fields` + `_term_adt_spec` → 0 corpus / 0 other mirror.

### Gate battery (driver-verified fresh, per conversion)
- count 921 → **920** (`any_unsupported`) → **919** (`all_present_unsupported`)
  → **918** (`provers_agree`) → **917** (`all_agree`); ledger **3** (`git diff`
  on proof_axiom_allowlist.py / src/formal-semantics EMPTY).
- **whole-file** `crosscheck_ir.py` proof **SUCCESS** (all 4 methods + term_eq;
  28s). L3-tc ✓ whole file. The sibling term mirrors (emit_why3/canonical/ir/
  from_sexp/parser) emit BYTE-IDENTICAL to HEAD (mirror-emission diff = only
  crosscheck_ir differs) → their proofs carry (the full suite exceeds the 10-min
  foreground cap; verified by byte-identity + the changed file's whole-file proof).
- **corpus byte-diff 0** (810 common == 810, mine vs detached-HEAD worktree with
  `.venv` symlinked, IDENTICAL, 0 changed / 0 only-in; new 0964/0965 fixtures
  mine-only). All machinery gated on `_has_opaque_term_fields`/`_term_adt_spec`.
- Vacuity `--emit` exit 0: **0 input-blind**, no NEW erasure (the 4 methods read
  their canon fields; the 3 KNOWN erasures unchanged).
- mirror-check **52/52**; drift **2 == HEAD** (the 4 methods verbatim = in sync;
  the 2 pre-existing `_handle_var_expr`/`_handle_for_stmt` still-blocked).
- **MUTATION TEST (Gate C, decisive):** (M1) `isinstance(c, Unsupported)`→`Var`
  flips `Some (Unsupported _ _)`→`Some (Var _)` (ctor + arity flow); (M2)
  `all`→`any` flips the AND+exists form→OR; (M3') `lean_canon`→`registry_canon`
  flips the `term_eq` operand field; (M4) tuple field-order flips the match
  scrutinee. Non-facade (real `option term` fields, real ctor destructure, real
  term_eq — no int-hash / 2-ctor-collapse / oracle).
- fixtures (`git add -f`): `0964_crosscheck_term_structural.py` (positive; the
  full 3-ctor `Term = Unsupported | Var | Bin` union + `has_unsup` dispatch fold
  + `IRCrossCheckResult` with all 4 methods; PROVES) + `0965_..._twin.py` (the
  `isinstance(c, Var)` DISCRIMINATING TWIN; PROVES, byte-different emission).

### §RESIDUAL-after-F3F4 — the crosscheck term-structural cluster is CLOSED
The 4 methods are converted; `pairwise` (returns `Dict[str, Optional[bool]]`) is
a distinct dict-result algebra on top of `term_eq` (a separate small carrier, not
built). `diagnostic` (str-build via `.pp()`) rides the record-bridge pp family.
`Module2_Parser._csl_to_str` (CSLNode ADT) stays [CORRECTNESS] (its int is
`str_to_int` = the oracle). This is the IO/parser boundary band — the driver
consolidates from here.
