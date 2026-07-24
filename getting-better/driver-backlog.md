# driver-backlog.md — the standing, PRE-AUTHORIZED escalation ladder for autonomous runs

The self-tcb-reduction-driver autonomous loop works THIS list, top-to-bottom, without stopping to
ask. Every item here is user-authorized for autonomous pursuit (including session-scale and
certificate-touching builds). The loop escalates to the next item when the cheaper work above it is
exhausted, and only STOPS at the deadline or when every item below is BROKEN / CERTIFIED-BOUNDARY.

**Authority (set by the user, 2026-07-24): FULL.** Auto-pursue every item, including
certificate-touching builds. The only things still gated per-instance are IRREVERSIBLE / OUTWARD
actions — `git push`, anything destructive/outward-facing — never the build/verify itself.

**Discipline that still applies to every item (non-negotiable):** spike-first + refutation-exit (a
wall that refutes is CERTIFIED-BOUNDARY, recorded, NOT ground on); lesson (p) census-first ("does an
existing certified capability already do this?" — enumerate the value models / recognizers before
scoping a new build); the full three-plane gate battery driver-verified fresh; ledger stays 3;
foreground-only sub-agents (lesson n). A checkpoint (commit + one line to
`getting-better/driver-progress.log`) marks each item transition — a breadcrumb, never a stop.

## Ladder (priority order — work top-down)

1. **Cheap drain (always first, §P).** Any `\trusted` stub a fresh census rates `cheap_win==true`.
   Re-run after every wall breaks (a break may unlock cheap follow-ons).

2. **Recognizer-reach extensions (bounded, low-ROI but real).**
   - set-membership + subject-first-param discriminant for `recognize_type_existence` → unblocks
     `_union_c8_test_references_union_var` (measured: ~1 stub; over-engineering-adjacent, do it only
     if item 1 is dry and nothing richer is ready).

   **CENSUS + SPIKE DONE (2026-07-24, count 942) — CERTIFIED-BOUNDARY (3-features-for-1-stub + item-7
   string-set dependency). ROI gate stops here.**
   - STEP-0 census (lesson p): the subject-first + set-membership BOOL-existence-fold shape is EXACTLY
     ONE stub. AST scan of every `\trusted` mirror stub with an `Any`-first + `set`/`Set[str]`-second
     signature yields 7 candidates, but 6 are the WRONG algebra: `_collect_call_targets`,
     `_hp_collect_written`, `_check_typeddict_access`, `_check_namedtuple_access` return `None` (void
     collectors/checkers via `acc.add`/side-effect), `find_calls_in_ir` returns `Set` (set-builder),
     `find_named_expr_targets` returns `None` (void). Only `_union_c8_test_references_union_var` is the
     recursive bool existence fold with a set-membership leaf. **No cluster.**
   - STEP-0 spike: ported the LIVE body VERBATIM into the mirror, `--no-proof --keep-mlw`. Current
     recognizers do NOT fire — neither `recognize_type_existence` (subject is FIRST not LAST, carried
     param is `set` not `str`) nor `recognize_named_field_existence` (2 params, not 1). It lowers to
     `let rec function _union_c8_test_references_union_var (test: int) (union_vars: map int (option int))`
     — `test` erased to `int`, discriminant `(typeof_op 448) = 4` reads a HASH CONSTANT (vacuous,
     lesson l), set membership `Map.get union_vars (test_get_1 1878939832)` int-hashes the key, and the
     `any(genexp)` lowers to `_any_fold_59885` referencing a FREE unbound `union_vars` (L3-tc FAILS).
   - Feature count to convert non-vacuously (references `test` AND `union_vars`, real string-keyed
     membership, no int-hash): **≥3 genuinely-new recognizer features** — (F1) subject-FIRST param
     ordering (`recognize_type_existence` hard-codes `subj = params[-1]`); (F2) a `set`-typed carried
     param (the carried handling requires each leading param annotated `str`, declared `(c: string)`);
     (F3) a set-membership leaf discriminant `<subj>.get("<k>") in <set param>` (a new matcher + a new
     emit arm) — PLUS (F4) to be non-vacuous the membership needs a STRING-KEYED set (bare `set` →
     `map int (option int)`, int-hash = lesson l), which is exactly item 7's session-scale
     string-keyed-set model (already CERTIFIED-BOUNDARY 2026-07-24). So even a full F1–F3 recognizer
     build stays VACUOUS until item 7 lands. 3 recognizer features + a session-scale dependency, for 1
     stub, no cluster ⇒ ROI-gate STOP (§10c, lesson q refutation-exit).
   - REOPEN: only worthwhile if item 7's string-keyed-set model lands FIRST (then F4 is free), AND a
     future shape-census surfaces a ≥3-stub cluster sharing the subject-first + set-membership
     existence-fold shape. Until then this is a lone marker behind a session-scale wall — leave-trusted.

3. **The structure-returning `Any`-walker class (session-scale, the big remaining vein).** The mirror
   is dominated by walkers that RETURN a string/dict/list (`_expr_to_whyml`, `_to_bool`, the
   `_build_method_*_ensures_map` family, the `visit_X` unparse family) rather than a bool. The
   bool-existence recognizer cannot model these. This needs a value-PRODUCING tree-transform model
   (not just existence). Spike whether the certified pyval/pydict/stmt_ir catamorphisms can carry a
   RETURNED value before scoping anything new (lesson p). Highest count-ROI if it opens.

   **PARTIALLY BUILT 2026-07-24 (count 941 → 940, commits 8def3372 feature + 1e1066b6 conversion) —
   the general value-returning pyval STRING walker is IN-TREE. See `pyval-walker-impl.md`.** The
   §OUTCOME-2 "[COST/SCALE], no bounded non-facade entry" is SUPERSEDED for the self-contained
   `Optional[str]` fold shape: `recognize_pyval_string_walker` + `emit_pyval_string_walker_group`
   (`generic_fold.py`, source-only → 0 new stubs) is a STRUCTURAL translator over the pyval ADT with 3
   inline TOTAL projectors pv_nth/pv_len/atom_of (DEFINED not axiomatized; ledger 3). Converted
   `from_sexp._binder_name` (the one self-contained cluster stub). Mutation test decisive, corpus
   byte-diff 0, mirror byte-diff touches only the converted file, whole-file proof SUCCESS.
   **C1 LIST-accumulator carrier BUILT 2026-07-24 (count 940 → 939) — see `pyval-walker-impl.md`
   §OUTCOME-C1.** `recognize_pyval_list_walker` + `emit_pyval_list_walker_group` (`generic_fold.py`,
   source-only → 0 new stubs): a `List[str]` (`list string`) walker BUILT via `.append`/`.extend`/
   `reversed` over the pyval spine + inline TOTAL app/rev + an axiom-free per-function
   `{n}__size_nthl` lemma for TREE self-recursion termination (Alt-Ergo-proved, ledger 3). Converted
   `from_sexp._walk_modpath` (the ONE C1 stub reachable by the List carrier ALONE — self-recursion, no
   cross-call). Mutation test decisive ("MPfile"→"MPZZZ"), corpus byte-diff 0 (789 common identical),
   suite-mirror byte-diff 0, `--fun`+whole-file proofs SUCCESS, drift 2, fixture 0943.
   **C1b DONE (2026-07-24, 939→936):** TWO carriers converted ALL 3 remaining C1 stubs. (i) CROSS-CALL
   support (`recognize_pyval_list_walker(func, sibling_walkers)` + `compute_pyval_list_walker_names`
   fixpoint) → `_walk_kername`. (ii) SEARCH catamorphism (`recognize_pyval_list_search`/
   `emit_pyval_list_search_group`: mutual `let rec {n}(v) variant{pv_size v} with {n}__list(l)
   variant{size_list l}`, cross-decreasing structural measures = AUTO termination, NO new axiom) →
   `_find_kername_components`; + Return-listexpr generalization → `_full_const_path`. **CENSUS CORRECTION:**
   the cluster is a DAG, NOT mutual-recursion — the EXISTING SCC topological ordering (scc.py) handles
   forward-refs, so no `let rec…with` mutual-group emission was needed (the residual premise was wrong).
   Mutation test decisive on both emitters; corpus byte-diff 0; fixtures 0944/0945; drift 2; ledger 3.
   Commits bb3c497b/76fb3ee9/e9762a4e/23e1dd55/f7a73ffb. See pyval-walker-impl.md §OUTCOME-C1b.
   **C2 DONE (2026-07-24, 936→934):** the STRING walker `recognize_pyval_string_walker` now takes the
   module's pyval-list-walker fixpoint set, so a `<var> = <sibling>(vref)` assign binds a `list string`
   local and `<var>[-k] if <var> else None` reads its NEGATIVE-index end. The neg-index lowers TOTAL to
   `nths sl (lens sl - k)` (two inline `list string` projectors, DEFINED not axiomatized → CORRECTNESS-
   clean, NO OOB assumption, NO 4th axiom), composing with the `Optional[str]` union. Converted BOTH
   `_const_name` (935) and `_ind_short_name` (934). Mutation test decisive incl. neg-index-offset
   discrimination (`[-1]`→`- 1`, `[-2]`→`- 2`); `--fun` each + whole-file from_sexp proof SUCCESS; corpus
   byte-diff 0 (792 common identical, only new 0946/0947 fixtures mine-only); suite-mirror byte-diff only
   from_sexp.mlw; drift 2; ledger 3. Fixtures 0946 (positive) + 0947 ([-2] discriminating twin). See
   pyval-walker-impl.md §OUTCOME-C2.
   **C3 DONE + VEIN CLOSED (2026-07-24, 934→933):** the census REFUTED the target's "int via
   pv_nth/pv_len + int accumulator" framing — the int is `int(<pyval string atom>)` = the unconstrained
   `str_to_int` ORACLE (expressions.py:5743; rejected by no-more-int). Split:
   • `_flatten_tuples` (`List[Any]` = `list pyval`, a list-of-NODES accumulator — a DIFFERENT algebra,
     NO int/oracle) → **BUILT + CONVERTED (933)** via `recognize_pyval_flatten`/`emit_pyval_flatten_group`
     (`generic_fold.py`): the certified mutual `{n}(v) with {n}__list(l)` group + inline TOTAL `list pyval`
     append; spike all-Valid Alt-Ergo, NO axiom; `--fun`+whole-file from_sexp proof SUCCESS; corpus
     byte-diff 0 (794 identical); suite-mirror byte-diff only from_sexp.mlw; drift 2; ledger 3; mutation
     test decisive (the `head` knob: drop `out.append(t)` → emission loses `Cons v_t`). Fixtures 0948
     (positive) + 0949 (head-knob discriminating twin). See pyval-walker-impl.md §OUTCOME-C3.
   • `_find_construct_idx` (`Optional[int]`) + `_construct_indices` (`Optional[Tuple[str,int]]`) →
     **[CORRECTNESS] boundary — NOT COST.** Their int is the `str_to_int` oracle (the tuple's int
     component transitively so); a faithful lowering needs a 4th cited axiom (a real string→int parse) or
     the oracle (any_1, forbidden). **No further pyval carrier reaches them → the from_sexp pyval-walker
     vein is CLOSED at the value-model boundary** (10 of 12 from_sexp stubs verified; the final 2 are a
     str→int-parse-oracle correctness wall).

   **CENSUS + SPIKE DONE (2026-07-23, count 971) — CERTIFIED-BOUNDARY for existing/minimal machinery.**
   - STEP-0 census (lesson p): **0 of the 8 clean candidates are reached by any existing recognizer**
     (`recognize_frt`/`sawalk`/`substmap`/`dictfold`/`setfold`). Demonstrated verbatim-porting
     `monomorphize._type_str`: the `Any` param lowers to `int` (default int-hash model), `typeof_op 422`
     reads a HASH CONSTANT (vacuous, lesson l), and the sibling call `_sanitize_type_name node` fails to
     typecheck (int-vs-string). The value-producing recognizers are each **bespoke to ONE live-method
     shape** over pydict/pyval and match none of the candidates.
   - STEP-1 spike: **NOT refuted.** A value-returning `: string` catamorphism over pyval proves
     non-vacuously — `emit_frt_group` already emits `find_return_type (stmts: list pyval) : string` that
     BUILDS a string from the tree (`str_concat_op "(" (str_join_arr ", " (Array.make nn "int")) ")"`,
     tuple arity `nn` read via real spine readers), variant-terminating, axiom-free, and it is un-`\trusted`
     + gated in the mirror. So provability is NOT the wall.
   - The real wall: the 8 candidates sit behind **four distinct un-built value carriers**, none a small
     extension to an existing recognizer:
       * Python **tuple / sexp** ADT (indexed `t[1]`, tag-at-`[0]`): `from_sexp._const_name`,
         `_ind_short_name`, `_binder_name` — **CERTIFIED-BOUNDARY (2026-07-24, sexp-carrier-impl.md
         §OUTCOME).** Both spikes re-verified axiom-free by the driver (SexpCert.v coqc 8.20.1 "Closed
         under the global context" ×3; sexp.mlw z3 pos Valid / evil Timeout / nth1 Valid), so
         PROVABILITY is not the wall. The RECOGNIZER walls: the verbatim bodies use heterogeneous
         positional index `t[i]` consumed as BOTH string (`return inner[1]`, `out.append(iid[1])`) and
         sub-sexp (`_walk_modpath(mp[1])`) at the same syntactic form (BLOCKER 1 — needs consuming-
         context-directed `atom_of` coercion the emitter's emit_ir-node-only subscript lowering lacks),
         the helpers build a `List[str]` result via `.append`/`.extend`/`reversed`+for-over-slist that
         the `last_atom` oracle sidesteps (BLOCKER 2), plus string-tag dispatch/`len>=3` guards
         (BLOCKER 3). REOPEN needs a bespoke sexp recognizer = 3 new features for net −3 (session-scale,
         §10.3 generic-Any class). Cert + value oracle banked in getting-better/sexp-carrier-oracles/.
         **REFINED 2026-07-24 (sexp-carrier-impl.md §OUTCOME-2): "net −3" is a genuine count DECREASE /
         0 new stubs (recognizer lands in UNmirrored generic_fold.py) — NOT a giants-trap; pyval REUSE
         (PStr=SAtom, PList=SList) kills the new-cert cost (3 projectors on the certified pyval theory,
         ledger 3). Residual = the §10.3 value-returning-pyval walker, no bounded/non-facade entry.**
       * **class-instance variant** ADT (`isinstance(t,Var)` + `t.name`/`node.left`) — **CARRIER BUILT
         2026-07-24 (count 933 → 932, `class-variant-impl.md`).** CENSUS: the proof2why3 `Term` union
         (Var|IntLit|BoolLit|App|BinOp|UnaryOp|Forall|Exists|Unsupported) is the LARGEST reachable
         cluster (~18 stubs: canonical.py ×10 transforms, ir.py ×2, emit_why3.py ×2, crosscheck_ir.py
         ×2). NO existing value model fits a 9-way isinstance dispatch on distinct dataclasses → a NEW
         variant ADT + co-landing cert. BUILT `compute_term_adt_spec` + `recognize_term_isinstance_fold`
         + `emit_term_isinstance_fold_group` (generic_fold.py) + `_emit_term_theory` (preamble.py, gated
         `needs_term`) + dispatch (functions.py); co-landed AXIOM-FREE `Phase2i_TermIR.v` (Print
         Assumptions closed ×9) + `TermIR.lean` (no axioms ×14), ledger 3. Converted
         `emit_why3.contains_unsupported` (the bool existence fold) → total positional `match` over the
         `term` variant. Both spikes PASSED (cert Valid all algebras / recognizer falsifier); mutation
         test decisive; corpus byte-diff 0 (796==796); whole-file emit_why3 proof SUCCESS (added to
         suite, lesson 10); drift 2; fixture 0950.
         **T-TRANSFORM BUILT 2026-07-24 (count 932 → 931) — see class-variant-impl.md §OUTCOME-T.**
         `recognize_term_isinstance_transform` + `emit_term_isinstance_transform_group` (generic_fold.py,
         source-only → 0 new stubs): the Term→Term constructor-rebuild algebra (identity leaf / single-ctor
         rebuild w/ COPY|REC|MAPREC fields / same-kind `kind=A if isinstance else B` rebuild / const-map
         op-swap via `pystr_eq`). NO new cert (same `Phase2i_TermIR` inductive; pystr_eq is a `val`, not an
         axiom; ledger 3). **CENSUS CORRECTION: the transform-algebra-ALONE cluster is 1, NOT "most of 10".**
         Only `_flip_comparisons` is clean; `_iff_app_to_binop` = RESIDUAL [COST/SCALE] (list-len-guard +
         index + termination-proof-cost — spike TIMES OUT on both alt-ergo AND z3); the other 8 are OUT
         (cross-call the still-`\trusted` `mk_arrow_chain`/`flatten_arrow_chain`/`substitute`/`_camel_to_snake`,
         or a `Dict[str,str]` map param). Converted `_flip_comparisons`. Mutation test decisive (map value
         `>=`→`>>`; UnaryOp recursion drop); corpus byte-diff 0 (797==797); `--fun`+whole-file canonical.py
         proof SUCCESS; drift 2; fixture 0951.
         **T-SET/LIST LEAVES BUILT 2026-07-24 (count 931 → 928) — see class-variant-impl.md §OUTCOME-TL.**
         The 3 `proof2why3/ir.py` leaf utilities converted over the SAME `term` inductive (no new cert;
         ledger 3): `mk_arrow_chain` (recognize_term_list_build — a (list term, term) accumulator BUILDER,
         930), `flatten_arrow_chain` (recognize_term_flatten_arrow — a while-spine (list term, term) TUPLE
         walker, 929), `free_vars` (recognize_term_free_vars — a set-of-strings catamorphism over
         `map string bool`, structural mutual variants, bare-`val` __set_add = no assumed fact, 928). Plus
         the FAITHFULNESS fix (mirror `App.args: Tuple[Term,...]`/`binders: Tuple[str,...]` = live) +
         `_term_field_names_selfiter` For-loop detection. SHARED-LEAF cascade (importers canonical/emit_why3/
         parser) benign — all re-prove SUCCESS. Mutation tests decisive; corpus byte-diff 0; full suite PASS;
         drift 2; fixtures 0952–0957 (3 positive + 3 discriminating twins). **CASCADE CALLERS did NOT
         unblock** — the 4 `canonical.py` transforms cross-calling the leaves (`_expand_nat_to_int`,
         `_dedup_arrow_chain`, `_sort_arrow_hypotheses`, `_flatten_foralls`) each carry an INDEPENDENT wall
         beyond the leaf call (genexp-to-termlist / `not in`-dedup+term-eq / `sorted` closure / mutable
         gather-loop) → the leaves are the yield, not a cascade.
         **T-STRING BUILT 2026-07-24 (count 928 → 927) — see class-variant-impl.md §OUTCOME-TS.**
         `recognize_term_string_pp` + `emit_term_string_pp_group` (generic_fold.py, source-only → 0 new
         stubs): the term→string BUILD catamorphism (the `_pp` shape) — f-string/`str()`/`" ".join` build
         threading a `parent_prec: int` inherited attribute + a `_BINOP_PREC` str→int const table (new
         `collect_module_const_int_dicts` collector, gated → corpus-inert) + int-arith + conditional
         paren-wrap. PROGRAM `let rec` (calls `val pystr_eq`/`str_concat_op`/`str_of_int` — all `val`s, NO
         axiom; same `Phase2i_TermIR` cert; ledger 3). Converted `emit_why3._pp` + its §10.4 caller-cascade
         `ir_to_whyml_axiom_body` (new `recognize_term_pp_wrapper`, re-proven same commit). **CENSUS
         REFUTES the "~7 stub" framing: 1 single-function (`_pp`) + 5 RECORD-BRIDGE.** Mutation test
         decisive (separator ` . `→` ; `); corpus byte-diff 0 (804==804); whole-file emit_why3/ir/canonical
         proofs SUCCESS; drift 2; fixtures 0958 (positive) + 0959 (twin). **RESIDUAL [COST/SCALE]:** the 5
         `ir.py` per-class `pp` methods (App/BinOp/UnaryOp/Forall/Exists) are per-variant METHODS on the
         frozen-dataclass RECORDS (`self: app`, `args: array int`) recursing via VIRTUAL `a.pp()` — the
         record model erases recursive children to int; reaching them needs the record⇄variant bridge
         (record-field-type fix + synthesized unified `pp_term` + per-class injection/delegation,
         co-dependent across the family, corpus-byte-diff exposure). No 4th axiom.
         **CROSSCHECK SELF-STATE CARRIER BUILT 2026-07-24 (count 922 → 921) — see class-variant-impl.md §OUTCOME-CC.**
         `recognize_crosscheck_selfstate_bool` + `emit_crosscheck_selfstate_bool_group` (generic_fold.py,
         source-only → 0 new stubs): the `IRCrossCheckResult` `@property` self-state boolean fragment
         (presence `is_some` / string-empty `pystr_eq`) over `Optional[Term]` canon fields typed as an
         inhabitable OPAQUE `option int` (M5 allow-list "opaque_term"). Dropped `@property` in the mirror
         (both gates decorator-blind) to un-skip the pre-IR-dropped property. Converted `registry_skipped`.
         Correctness spike PASSED the WHOLE sub-cluster (`term_eq` DEFINABLE, no 4th axiom → [COST/SCALE]).
         **RESIDUAL [COST/SCALE]:** the 4 term-STRUCTURAL methods (`any_unsupported`/`all_present_unsupported`
         destruct `Unsupported`; `provers_agree`/`all_agree` need `term_eq`) require the certified 9-ctor
         `term` inductive + a DEFINED `term_eq` EMITTED here, which `compute_term_adt_spec` cannot derive
         (no isinstance-dispatch over the ctor set) — REOPEN needs (F3) a canonical-`term`-spec source +
         (F4) a `term`-theory/`term_eq` emitter. No 4th axiom. Mutation tests decisive; corpus+suite-mirror
         byte-diff 0; whole-file proof SUCCESS; drift 2; ledger 3; fixtures 0962/0963.
         **RESIDUAL [COST/SCALE] (unchanged carriers):** `_iff_app_to_binop` (list-index/len + proof cost),
         the 4 cascade-caller transforms above (need the genexp-to-termlist / dedup-membership / sorted /
         gather-loop recognizers), `substitute` (`Dict[str,str]` map-param), T-string (`_pp` f-string build)
         — all CERT-covered by the SAME `term` inductive (no new cert), distinct recognizers.
         `Module2_Parser._csl_to_str` (CSLNode ADT) stays [CORRECTNESS] (its int is `str_to_int` = oracle).
       * Python **`ast.*` node** hierarchy (`isinstance(x,ast.Subscript)`, `x.value.id`): M5
         `_normalize_literal_annotation`, `_encode_callable_annotation`, `_typeddict_field_type` — reopen
         with an `ast`-node value model (plus self-state mutation / `\trusted`-sibling calls / raise+encode).
       * **pyval-dict flat projection** (`_type_str`) + **runtime-string ops** (`ir_inline._global_call_target`:
         `partition(".")`, `"." in f`, `recv in globals_set`, `g_class[recv]`) — `_type_str` is the ONLY
         candidate on an existing carrier (pyval) but is a LONE stub (no cluster) needing a bespoke
         ~flat-projection recognizer; not worth a per-method build (§10.7 VALUE-not-count, lesson p).
   - Cluster measurement: 113 `str`- + 25 `Optional[str]`-returning `\trusted` stubs exist, but the
     population is **heterogeneous non-fold** (I/O `_find_coqc`, regex `_strip_rocq_comments`, self-state
     `errors.message`, string manip) — no single small recognizer unlocks a cluster. A worthwhile build
     is a per-carrier value model (biggest = the `ast.*` M5 family), gated by its own measure-before-build
     carrier census + authorization — NOT a bespoke per-stub recognizer. Fell through to item 4.

**AST-NODE CARRIER SIZED (2026-07-23, count 942):** 47 `\trusted` stubs dispatch on `isinstance(_,ast.*)`
   (24 in Module5_IREmitter, 14 in Module3_Weaver). BUT the top users are HEAVY transforms —
   `_build_function_symbol_table` (30 ast-dispatches → 3-tuple of dicts), `_build_function_ir`,
   `visit_Module`, `_synthesize_*` — i.e. the emitter's core AST→IR construction. A faithful `ast`-node
   value model for these is re-implementing the emitter in WhyML, the campaign's DEEPEST wall (§10.3
   int-AST / generic-Any), NOT a bounded carrier. So the biggest cluster is the least tractable. The
   TRACTABLE carriers remain the small ones (tuple/sexp: 3 from_sexp stubs; class-variant: 2). Deprioritize
   the ast-node model until a small carrier proves the certificate+emitter pattern is repeatable in-window.

4. **The closure / nested-`def` walker family (dropped-closure blocker).** `_check`-style wrappers
   solved; the `found=[False]` / nested-`def` lambda-lift family (`_body_has_raise`,
   `_body_has_diverging_construct`, `_lemma_*`) still drops the closure at emission. Needs the
   emitter to recognize a nested-def existence walker whole. Spike-gate.

   **CENSUS + SPIKE DONE (2026-07-23, count 942) — CERTIFIED-BOUNDARY for existing/bounded machinery.**
   - STEP-0 census (lesson p): ported the LIVE closure body of `_body_has_raise` VERBATIM into the
     mirror (`found=[False]; def walk(node): ... for v in node.values(): walk(v)`), `--no-proof
     --keep-mlw`. **The closure is DROPPED at emission** and lowers input-blind/VACUOUS:
     `let _body_has_raise (body: int) : int = let found = Array.make 1 0 in let _ = walk body in ();
     found[0]` — `body` erased to `int` (default int-hash, no `list` value model), the nested `walk`
     lifted to a free/erased symbol, `found` a constant array. **No existing recognizer fires on the
     nested-def `found=[False]` closure.** Blocker = nested-`def` lambda-lift drops the walk AND the
     mutable-closure idiom erases the subject to int. (The already-converted sibling `_body_has_return`
     right below emits the certified `stmt_ir` catamorphism — it was flat-rewritten live+mirror to the
     `recognize_stmt_has` shape; that is the ONLY working precedent for this family.)
   - STEP-1 spike (recognize the nested-def walker as a WHOLE) = a nested-`def` + mutable-closure
     lowering SUBSYSTEM = **session-scale**. The bypass (flat-rewrite to `recognize_stmt_has`, the
     `_body_has_return` precedent) reaches AT MOST `_body_has_raise` and even that is CERTIFICATE-COUPLED:
     the certified `stmt_ir` ADT (WhyML preamble + Lean `StmtIR.lean` + Rocq `Phase2d_StmtIR.v`, w/
     round-trip completeness + tag-distinctness theorems) has **no `SRaise` constructor** — "Raise" is
     not in `_STMT_LEAF_TAG_CTOR`/`_STMT_COMPOUND` and cannot be, so the typed catamorphism can't return
     `SRaise -> true`. The other 9 of 10 are each SEPARATELY blocked, so SRaise unlocks 1, not the cluster:
       * `_body_has_diverging_construct` — detects `type=="Call"` in EXPRESSION positions; the stmt_ir
         catamorphism deliberately does NOT descend into `emit_ir` expr children, so the typed route
         structurally cannot see it; plus a compound multi-tag+`type` discriminant. Needs generic-expr descent.
       * `_lemma_returns_value` — needs the `SReturn` `iropt_ir` PAYLOAD guard (value present & non-`None`);
         the catamorphism arm `SReturn _ -> true` discards the payload. Not expressible as-is.
       * `_returns_string_seq` / `_func_returns_string_seq` — self-state `_seq_value_types` map read +
         string-element value model.
       * `_is_linear_expr` — an AND-fold (universal) expression whitelist over `emit_ir`, not an
         existence-OR walk; different algebra.
       * `_has_set_op_on_map` — self-state map-locals + `_rhs_yields_map`/`_test_contains_map` sibling
         calls + compound discriminants.
       * `_should_auto_trust_tuple_return` — self-state `array_vars` + `IRScanner` + nested tuple-slot walk.
   - VALUE verdict (lesson 7 / §10.5): even the certificate-coupled `SRaise` build (WhyML preamble +
     both certs + round-trip/distinctness re-proof + the `emit_ir`→`stmt_ir` marshalling) unlocks exactly
     1 of 10; it does NOT open the cluster. Not worth a both-prover ADT extension for a lone marker.
     **Reopening capabilities (record for a future ladder edit):**
     (R1) a nested-`def`+mutable-closure (`found=[False]`) existence-walker RECOGNIZER that lifts
     `def f(root): found=[False]; def walk(x): if <cond>: found[0]=True; <descend>; walk(root);
     return found[0]` WHOLE onto the certified `emit_bool_existence_group` (pyval) / `emit_stmt_has_group`
     (stmt_ir) target — the pyval route is the natural carrier because its `__d` already generically
     descends ALL dict values (incl. expr children); (R2) `SRaise` added to the certified stmt_ir ADT
     (axiom-free co-landing cert) for the "Raise" tag; (R3) generic-EXPRESSION-position Call detection +
     compound multi-tag/`type` discriminant → `_body_has_diverging_construct`; (R4) an `SReturn`
     iropt-payload predicate → `_lemma_returns_value`; (R5) self-state map/dict value-model threading
     (`_seq_value_types`, map-locals) → the auto_trust/functions self-state members.
     Fell through to item 5.

5. **R2c — contract-grammar genexp** (`#@ assert all(x >= 0 for x in a)` does not parse). Repairs the
   spec plane of the any/all fold. Independent of R2d/R2e. Grammar work in `Module2_Parser.py`; may
   be its own subsystem — SPLIT and record if so.

   **BUILT (2026-07-23, count 942 unchanged — spec-plane integrity, count-neutral by design).**
   NOT its own subsystem: a genexp arg to `all`/`any` inside a `#@` clause desugars to the ALREADY-
   CERTIFIED bounded quantifier. `all(P for x in dom)` builds exactly the CSLNode `\forall x in dom; P`
   builds (via `_mk_in`, quantification.md P3); `any(...)` builds `\exists x in dom; P`. So the IR,
   lowering, AND 3-axiom certificate are ENTIRELY reused — no new value model, no new lowering path.
   - Grammar: ONE branch in `_ContractParser._parse_atom_name` (`src/pycsl/frontend/Module2_Parser.py`) —
     when `name in ("all","any")` and a `for` follows the first expr, parse `for VAR in DOMAIN`, close
     `)`, emit `Forall`/`Exists` via `_mk_in`. A non-genexp `all(arr)`/`any(arr)` keeps the CallExpr path.
   - SPIKE (STEP 1) PASSED: `#@ assert all(x >= 0 for x in a)` now (a) PARSES, (b) lowers to a real
     `forall x. (exists m. 0<=m<len(a) /\ a[m]=x) -> x>=0` — grep 0 `all_1`/`any_1` oracle in the emitted
     .mlw, (c) proves a POSITIVE fixture and the EVIL TWIN (`all(x>=5 ...)` under `a[i]>=0`) does NOT
     prove (lesson l). The genexp `.mlw` is BYTE-IDENTICAL to the hand-written `\forall x in a; P`.
   - Fixtures (git add -f): `0938_spec_genexp_all_any.py` (positive `all`+`any` asserts, PROVE) +
     `0939_spec_genexp_evil_twin.py` (`# pycsl-expected: FAIL`, MUST NOT prove). Also fixed the
     PRE-EXISTING red `0937` (R2b's evil twin lacked the `# pycsl-expected: FAIL` marker → spurious FAIL;
     comment-only, emission byte-identical) — opportunistic gate hardening (item 8).
   - GATES (all fresh, driver-verified): corpus byte-diff 0 over 784 existing files (base 784 / mine 786
     = +2 new fixtures, 0 existing differ, detached-HEAD worktree); mirror-check 52/52; L3-tc 52/52;
     ALL 52 mirror `.mlw` emission BYTE-IDENTICAL to HEAD ⇒ self-annotation proof suite provably
     unaffected (identical WhyML ⇒ identical proof); sync drift 5 == HEAD; ledger 3 (no cert/allowlist/
     formal-semantics touched); count 942 unchanged (correct — spec-plane repair does not lower the
     count). Fell through to item 6.

6. **R2e — string/capture folds** (element-type parameterization + string-predicate lowering +
   closure-capture threading + `startswith`). 4 coordinated capabilities; clears
   `_handle_fieldassign_stmt` + `_union_arm_tag` (~2 sites) + 11 banked. Session-scale.

7. **The 3 session-scale vacuity residuals** (`_emit_new_ghost_ref`, `_handle_mktuple_expr`,
   `_collect_class_constants`) — each erases a param that flows only into a `\trusted` sibling; needs
   the sibling converted + a value-model feature (e.g. set-param-by-reference). Also the live-tool
   `Set[str].add(param)→()` faithfulness bug (lesson h family) — a real all-users fix worth doing
   under item 7.

   **`Set[str]` STRING-KEYING — CERTIFIED-BOUNDARY (2026-07-24, count 942 unchanged, tree reverted clean).**
   The driver's spike is CORRECT and PROVEN for STANDALONE functions, but landing it consistently across
   the self-annotation mirror is the "set-membership/`Fset`/`SetApp` model rework" the refutation clause
   names — NOT a bounded param-type change.
   - **Root diagnosis (verified):** a `Set[str]` PARAM already lowers by-reference; the real bug is the SET
     branch (`functions.py::_emit_param` L96) hard-codes `map int (option int)` while a string element
     should drive `map string (option int)` (the DICT branch already consults `_dict_key_types`; the set
     branch ignored it).
   - **SPIKE PASSED (standalone):** with 4 emitter edits — (a) `_emit_param` set branch consults
     `_dict_key_types`; (b)+(c) `_build_method_param_types_map` + `_build_method_param_whyml_types_by_name`
     string-key a `set` param when `_kt[name]=="string"`; (d) Module5 `_build_function_symbol_table` param
     loop pins `dict_key_types[arg]="string"` from a `Set[str]` annotation via `_m5_get_set_elem_type` —
     the fixture `def add_it(s: Set[str], x: str) with #@ ensures x in s: s.add(x)` L3-tc ✓ AND **PROVES**
     Valid (`map_update_some !s x 0` typechecks; `x in s` discharges). Real all-users faithfulness repair
     for standalone code.
   - **WHY IT CASCADES (the boundary):** `local_refs`/`declared_refs` are a `Set[str]` of variable NAMES
     threaded through the ENTIRE statement/expression-emission subsystem, and the mirror was built on the
     int-keyed (`str_hash_op`) set model. Making the param string-keyed breaks — measured, each revealing
     the next — (1) the set-union `|` lowering (`expressions.py` L3660) `str_hash_op`-hashes the string
     element to an int key (needed a raw-key branch for a string-keyed left, incl. the `<set>.copy()` left
     variant); (2) the cross-mixin `#@ requires_method _seq_operand: (…, local_refs: set)` decls — the
     `requires_method` GRAMMAR doesn't parse `Set[str]` (fell back to `int`, worse); (3) membership `in`
     and `.add`/`.discard` write sites all `str_hash_op`-hash (not yet reached but same shape); (4) the
     mirror's own INCONSISTENT annotations — 60 `local_refs: Set[str]` vs 15 `local_refs: int` vs 1 bare
     `set` — so no single inference is globally consistent; (5) cross-file self-method-call bridges default
     the callee param to `map int` when the callee's real sig isn't in the emitting file. The
     mirror-wide L3-tc sweep broke `expressions.py` + `stmt_control_flow.py` (both green at HEAD) — §10.4
     shared-lowering cascade — and full consistency needs every set-op lowering (union/copy/membership/
     add/discard) made string-key-aware + the requires_method grammar extended + the mirror re-annotated,
     with corpus byte-diff risk on every set-of-strings program. Session-scale, refutation-exit taken.
   - **DE-VACUIFY `_emit_new_ghost_ref` — SEPARATELY BLOCKED (stays in `KNOWN_ERASURES`).** Even with the
     key-type fix, `declared_refs.add(target)`/`local_refs.add(target)` still emit `()` (dropped) → `target`
     stays erased. Reason: `_seed_mutated_collection_params` (functions.py L4143) EXCLUDES methods from
     by-reference promotion ("ref promotion would desync the abstract-op call map"), and `_emit_new_ghost_ref`
     is a method. So `.add` on its by-value set param is dropped; the key-type change cannot de-vacuify it.
   - **REOPEN capability:** (R1) a string-keyed set-operation lowering pass — union `|`, `.copy()`,
     membership `in`, `.add`/`.discard`/`.remove` all emit the RAW string key (retiring `str_hash_op`) when
     the set is `_dict_key_types`-string; (R2) extend the `#@ requires_method` type grammar to parse
     `Set[str]`; (R3) reconcile the mirror's `local_refs`/`declared_refs` annotations to a single `Set[str]`
     (the 15 `int` + 1 bare `set` sites) + cross-file bridge string-key inference; (R4) for the de-vacuify,
     lift the method by-ref-promotion exclusion + resync the abstract-op call map for set-ref params. The
     4-edit standalone spike is banked (proves) and is the clean seed for R1.

8. **Soundness/gate hardening (do opportunistically, never a reason to stop).** The self-state vacuity
   gate's LOWER-BOUND partials; a `check-self-annotate-sync.sh` audit; the 5 flagged judgment-call
   lessons (i,k,g,j',m) carve-outs. Small, bounded, always-available filler between walls.
   - **STATUS 2026-07-23 — fidelity-drift repair, 5 DIVERGED → 4 (1 verified re-port, 4 STILL-BLOCKED).**
     The §10.4 fidelity gate was RED with 5 un-`\trusted` mirror methods proving stale bodies. Per-drift
     verbatim re-port + full gate:
     - `_handle_return_stmt` (stmt_control_flow) — **RE-PORTED & VERIFIED** (commit, drift 5→4). Added the
       `_pyval_seq_locals` return branch, the `emit_ir`/`_union_` raise branches, the tail bool→int block.
       `--fun` SUCCESS (13 goals all Valid, ~3m46s); L3-tc whole-file ✓; emitted body faithful (dispatches
       on real `func_ret` tags, references `val_ir`/`py_val`, no `any_1`); vacuity no-NEW-erasure/0-input-blind;
       mirror-check 52/52; count-neutral 942; mirror-only (byte-diff 0 by construction).
     - `_pattern_has_constructor` — **RESOLVED 2026-07-24 (drift 3→2).** Built the missing recognizer:
       `recognize_named_field_existence` + `emit_named_field_existence_group` (generic_fold.py) — the
       single-node named-field self-recursive existence fold (`p = pat.get("pattern"); if p == "Constructor":
       return True; if p == "Or": return any(self(a) for a in pat.get("alternatives", [])); return False`).
       Emits the SAME certified scalar pyval/pydict/list-pyval catamorphism as `emit_type_existence_group`,
       differing only in (i) the discriminant is keyed via the theory's built-in `K_dyn "<key>"` computed-key
       cell (non-`type` dispatch — NO new interned constant, NO theory change) and (ii) the `[assign, if-tag,
       if-recurse, return-False]` shape. The named-field recursion is subsumed by the universal structural
       descend (insight-C over-approx, the SAME doctrine the 8 IRScanner predicates use). Body re-ported
       VERBATIM from live (`any(genexp)`, mirror `pat` un-annotated so it lowers to the pyval carrier).
       Emitted body: `let rec …(pat: pyval): bool = match pat with PDict d -> …__key_is pat "Constructor"
       || …__d d | PList xs -> …__l xs | _ -> false end` with `variant { pv_size pat }` — REAL fold, `pat`
       referenced, mutation-sensitive tag, NO `any_1`/int-hash. GATES: drift 3→2; count 942 (unchanged —
       fidelity fix, not a marker move); mirror-check 52/52; corpus byte-diff 0 (786/786, clean HEAD
       worktree — recognizer gated on the exact shape, corpus-inert); vacuity --emit exit 0 (0 input-blind,
       no new erasure); whole-file L3-tc ✓; `--fun controlflowstmtmixin___pattern_has_constructor` full
       proof SUCCESS; ledger 3 untouched. Whole-file proof HEAVY (>cap) — driver re-runs uncapped to confirm.
     - `_union_arm_whyml_type` — **RESOLVED 2026-07-24 (drift 4→3, commit pending).** Fixed by a
       byte-inert `src/pycsl` emitter recognizer — but NOT the map-local pre-decl proposed below; the
       cleaner FAITHFUL fix is the **opaque-selfmap-reader SPLIT form**. The existing opaque-nested-map
       machinery (`_opaque_selfmap_aliases`, built for the CHAINED `record_types[tag]["whyml_name"]`) was
       extended to the two-statement SPLIT binding `_rt = getattr(self,"_record_types",{}).get(tag)` +
       `_rt["<lit>"]`/`_rt.get("<lit>")`: `_opaque_selfmap_inner_aliases[_rt] = (base, key_ir)`, the
       assignment is SUPPRESSED, and the three read sites lower to the SAME abstract readers the chained
       form uses, keyed on the REAL outer key — `if _rt` → `(record_types_mem tag : bool)`,
       `_rt.get("whyml_name")`/`_rt["whyml_name"]` → `(record_types_whyml_name tag : string)`. NO int-hash,
       NO opaque `subscript_get`/`_rt_get_str`, `tag` flows into every reader (non-vacuous, lesson l).
       Gated on the 1-arg leaf-string read shape present → corpus byte-diff 0 (786/786), mirror-diff
       confined to the target, whole-file L3-tc SUCCESS, `--fun` proof SUCCESS. `_record_types` field
       annotated `Dict[str,Dict[str,str]]` on the mirror class; body ported VERBATIM (added `emit_ir`
       map entry + `_record_types` tail). The map-local pre-decl below was the OTHER viable path but is
       superseded (it int-hashes the inner key; the opaque-reader is more faithful and reuses precedent).
       Historical diagnosis (kept for context):
       The prior "missing cap: nested string-field projection" was WRONG. With the field annotated
       `_record_types: Dict[str,Dict[str,str]]` AND the intermediate local annotated `_rt: Dict[str,str]`
       (both mirror-only, sync-gate drops local annotations), BOTH projections lower FAITHFULLY —
       `_rt := (match Map.get self._record_types tag with Some v_ -> v_ | None -> const None end)` (real
       outer map get) and `match Map.get !_rt "whyml_name" with Some v_ -> v_ | None -> "" end` (real inner
       STRING projection, NO int-hash, NO opaque `subscript_get`/`_rt_get_str`). The residual blocker is
       DIFFERENT and smaller: the verbatim body binds `_rt = getattr(...).get(tag)` in the early-return→
       if-else ELSE branch, so the emitter HOISTS it as `let _rt = ref 0 in` (int default, statements.py
       `_emit_body_code` `pfx="0"`), and `_rt := <map string (option string)>` fails L3-tc "expected int".
       The map/dict typed-local classifiers (`find_array_and_dict_vars`, `_rhs_yields_map`) are RHS-pattern-
       driven and don't recognize `.get(tag)`, and there is NO symbol-table-driven map-local classifier
       (unlike `string_vars`/`_union_locals` which DO read `_current_symbol_table`). Since all `_rt` uses are
       inside the else branch, a let-bind there would typecheck. **Missing cap = a byte-inert emitter
       recognizer: classify a local whose symtab type is a nested string-map as a typed local (let-bound at
       first assign / pre-declared `ref (const None)`), the map analogue of the existing `ref ""` string and
       `ref (IrOther "")` emit_ir pre-decls.** That is a src/pycsl edit (out of this mirror-only task's scope),
       but bounded and count-moving — a candidate menu-B build. The driver's spike (`d[tag]["whyml_name"]`,
       direct double-subscript on a plain local) genuinely lowers, but does NOT exercise the verbatim body's
       hoisted guard-local `_rt` — which is the real wall.
     - `_handle_var_expr` (expressions) — **STILL-BLOCKED (genuinely heterogeneous, confirmed 2026-07-24).**
       Needs helper `_union_local_read_projection`, whose verbatim body reads nested
       `_variant_types[st]["constructors"][cn]["arity"/"payload"]`. Unlike `_union_arm_whyml_type`, this read
       is genuinely HETEROGENEOUS and NOT annotatable to a faithful map: it iterates `constructors.items()`
       in a find-loop with mutable accumulators (`some_ctor`, `some_pay`), compares `c.get("arity") == 1`
       (INT), and indexes `c.get("payload") or []` then `_pay[0]` (LIST → str). No single carrier
       (`Dict[str,Dict[str,str]]` fails on `arity`/`payload`; a pyval carrier can't do the `.items()` find-loop
       + list-index in VALUE position). This is squarely the generic-`Any` recognizer wall (§10.3 / lesson q):
       multiple recognizer features (dict-items find-loop, heterogeneous constructor record, list-payload
       projection), all emitter-side. Adding the helper `\trusted` would be a +1 regression.
     - `_handle_for_stmt` — **STILL-BLOCKED (missing subsystem).** Verbatim body needs ~12 helpers absent from
       the mirror (`_string_char_iter`, `_classbody_psl_recv`, `_pyast_walk_recv`, `_keyword_iter_recv`,
       `_tparam_iter_recv`, `_mktuple_elts_recv_ir`, `_tparam_bases_recv`, `_add_abstract_op`) + 5 new self-state
       fields + a widened frame; the string-char-iter / pyast-stmt / keyword / tparam ADT-reflection is the V1/V2
       census wall. Supplying stubs would raise the count (forbidden).
     Net: fidelity gate greener (5→4), count-neutral 942, tree clean, no axiom. The 4 residuals are the V1
     `Dict[str,Any]`/genexp-list-field value-model wall (census-known), not a bounded transcription backlog.

## Exhaustion = STOP (the ONLY early-stop condition now)
The loop stops before the deadline ONLY when EVERY item 1–8 is either BROKEN or a **CORRECTNESS/SOUNDNESS
CERTIFIED-BOUNDARY** — a spike that proved the build IMPOSSIBLE/UNSOUND for reasons a bigger budget cannot
fix (Why3 type-rejection, would-need-a-4th-axiom, value model genuinely inexpressive). A **COST/SCALE
CERTIFIED-BOUNDARY** ("session-scale", "N features for M stubs", "cyclic but tractable") is NOT exhaustion:
a funded window is the budget that pays it — PROMOTE its reopening capability to a live item and BUILD it.
"Bounded work ran out" is NOT a stop condition either; escalate. **Before stopping, re-read this file from
disk and classify every boundary CORRECTNESS vs COST/SCALE — never assert "ladder empty" from memory** (the
2026-07-24 false stop did exactly that: called it floor at 9h of an 18h window while two COST/SCALE reopening
capabilities — the sexp recognizer and the R1 I4 cross-mixin κ fixpoint — sat un-built and Full-authorized).
When you record a CERTIFIED-BOUNDARY, TAG it `[CORRECTNESS]` or `[COST/SCALE]` and note the reopening
capability, so the stop-classification is mechanical, not a judgment call.

### Live COST/SCALE reopening capabilities (Full-authorized — BUILD these before any early stop)
- **R1 I4 — cross-mixin/method κ=string fixpoint. PARTIALLY BUILT 2026-07-24 (count 942 → 941, commit
  ef753230).** The FIELD half is realized MIRROR-ONLY: a sibling mixin that reads an owning-mixin `Set[str]`
  field just DECLARES it as a class-level annotation (the existing `_array_locals: Set[str] = None` pattern)
  → `_self_field_dict_kappa` recognizes it string-keyed, membership lowers to the raw key, non-vacuous. NO
  src/pycsl edit; byte-inert. Converted `_resolve_effective_ghost_type` (types.py). REACHABLE SUBSET = 1 of
  19: the other 18 carry independent `[CORRECTNESS]` walls (Dict[str,Any] `.values()` iteration, `rpartition`/
  `.lower`/`.split`/`.format` string ops, in-body imports, `List[str]` returns, `.add`/`.discard` mutator
  frames) that the field recognition does not touch. I6's claimed "f-string-of-int wall" was refuted
  (`int_to_string` handles it). The PARAM/method half (`local_refs`/`declared_refs`, 44 methods/81 sites/
  cyclic, expr↔stmt mutual recursion) + I5 de-vacuify STAY CERTIFIED-BOUNDARY — session-scale, no consistent
  sound κ signal. See `r1-setop-impl.md` run 3.
- **sexp recognizer / value-returning pyval walker — PARTIALLY BUILT 2026-07-24 (count 941 → 940,
  commits 8def3372 + 1e1066b6).** The general walker is now in-tree (`pyval-walker-impl.md`) and
  converted `from_sexp._binder_name`. The remaining 6 from_sexp stubs stay [COST/SCALE] behind the
  enumerated carriers C1 (`List[str]` accumulator) / C2 (trusted-helper pyval hook + `[-1]`) / C3
  (tuple/int returns) — see item 3. Below is the pre-build record (superseded for `_binder_name`):
- **sexp recognizer** — the 3 `from_sexp` tuple/sexp-carrier stubs. **REOPENED + REFINED 2026-07-24
  (count 941 held, tree clean, nothing committed) — still [COST/SCALE], but the record improved on two
  axes (see sexp-carrier-impl.md §OUTCOME-2):**
  (i) **NET accounting RESOLVED the §10.7 concern: net is POSITIVE, NOT a giants-trap.** The recognizer
  lands in `generic_fold.py`, which is NOT mirrored (mirror-check is a declared-SUBSET gate; source-only
  emitter methods force 0 new `\trusted` stubs — precedent: the named-field recognizer added 0). Net =
  +3 (count −3), 0 new stubs. The "net −3" is a genuine count DECREASE, not surface growth.
  (ii) **pyval REUSE eliminates the new-ADT + new-cert cost.** The certified `pyval` ADT (`PStr`=SAtom,
  `PList (list pyval)`=SList, with `pv_size`/`size_pos` proven axiom-free) IS the carrier; the build
  needs only 3 small total projectors (`pv_nth`/`pv_len`/`atom_of`) on the existing pyval theory — NO
  `Phase2*_Sexp.v`/`Sexp.lean`, ledger stays 3. The banked `sexp-carrier-oracles/` encode a SEPARATE ADT
  that pyval-reuse supersedes. Build-step 1 (new cert) is unnecessary.
  (iii) **Residual wall precisely located (concrete verbatim spike of `_const_name`), all [COST/SCALE],
  no bounded entry.** Current lowering is vacuous (`const_node: int`, `isinstance_op 0 0` on hash
  constants) + fails L3-tc (Optional-union can't absorb `subscript_get: int`). `_const_name`/
  `_ind_short_name` need the trusted helper `_find_kername_components` (emitted `val (payload:int):array
  string`) to carry a pyval param — NO annotation→pyval hook exists, and converting the helper hits
  BLOCKER 1+2. `_binder_name` is self-contained but needs a value-returning pyval-list for-fold with
  early return + BLOCKER 1 `atom_of` coercion. The genuine build = the §10.3 general value-returning-
  pyval walker (== item 3); a shape-specific recognizer = Gate-C facade reject. Sound throughout (no 4th
  axiom, no unsound guess). REOPEN: build pyval `pv_nth`/`pv_len`/`atom_of` + the general value-returning-
  pyval walker + a param-annotation→pyval hook + negative-index-from-end; do it once, generally.

### item 3 — F3+F4 crosscheck term-structural: CLOSED (2026-07-24, 921->917)
The §RESIDUAL-CC 4-method cluster (any_unsupported/all_present_unsupported/
provers_agree/all_agree) is CONVERTED. F3 = the certified `term` inductive made
available in crosscheck_ir by importing the full 9-ctor union in the mirror
(imports aren't sync-diffed; the imported folds seed compute_term_adt_spec);
opaque_term fields -> `option term`. F4 = a generic DEFINED `term_eq` emitter
(structural, no axiom, Phase2i-covered). Remaining crosscheck stubs: `pairwise`
(Dict[str,Optional[bool]] result algebra over term_eq) + `diagnostic` (str-build,
record-bridge pp) + the non-term `_load_axiom_registry`/`_preprocess_whyml`/
`crosscheck_file_ir`/`main` (IO/parse boundary). See class-variant-impl.md
§OUTCOME-F3F4.
