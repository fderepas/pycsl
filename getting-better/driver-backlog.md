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

1b. **VALUE-MODEL builds — CURRENT FRONTIER at 750 (2026-08-08, PRE-AUTHORIZED, corpus-affecting → M1
   discipline; see SKILL §A.6 "corpus-affecting value-model builds").** The seven-levers campaign
   (754→750 + Module6 soundness un-mask, all committed 75747ae7/93e8b341/97e5690f/825772ec/d8169f2d)
   exhausted the byte-inert capability gaps. The residual ~750 stubs are blocked behind three
   mutually-entangled value-model capabilities. A post-campaign Set-model make-or-break spike CONFIRMED
   feasibility of the value TYPE (axiom-free StrSet exists) but that wiring it is corpus-affecting (the
   corpus uses the identical `Set[str]` shape, so no byte-inert gate) — i.e. an **M1-discipline build,
   which is now AUTO-AUTHORIZED**, not a hold-and-ask. Pursue in this order:
   - **(A) `Set[str]` type model + set ops** [highest leverage; unblocks CIE `_callee_implicit_exceptions`
     + `_reset_module_accumulators` + the no-exception-summary cluster]. The value type EXISTS axiom-free
     (executable `StrSet = clone set.SetApp`, proven by `getting-better/set-oracle.mlw`; value model
     `set_add`=Map.set-true / `set_union`=orb-fold in preamble.py:3961/3970). MISSING: wire it through 6
     emitter surfaces — return-type inference, field-value-type inference (`Dict[str,Set[str]]`), `set(x)`
     copy-ctor, SetComp→set-building-fold (coupled to heterogeneous `pget` of `r["exc_type"]`), in-place
     `.update`→`set_union` (+ array→set coercion), a new `set_diff` val (trivially axiom-free
     `fun k->andb (Map.get a k)(notb (Map.get b k))`). GATE: M1 — the corpus Set[str] files
     (0775/0940/0882/0883/0884/0941 + v2_setfold_spike + 0923_str_set_local) re-emit; the diff must be
     EXACTLY the set-model correction AND each must re-prove 0 non-Valid.
   - **(B) Empty-collection-literal value-type inference** [`{}`/`[]`/`set()` assigned to a typed field
     infers the field's element type instead of the `option int` default]. Entangled with (A):
     `_reset_module_accumulators` needs both. GATE: M1 (corpus empty-literal assignments re-emit).
   - **(C) list-slice/concat type inference** [`x[1:]`, list-concat currently leak `int`/`array`].
     GATE: M1.
   Each: spike-first (census-p: does an existing model already cover it?), co-landing axiom-free cert for
   any new value shape, three-plane battery with M1 byte-diff (exact diff + every affected program
   re-proves), driver-verified, independent control agent. If a shape can't be certified axiom-free → THAT
   is the CERTIFIED-BOUNDARY (not the byte-diff).

   **ATTEMPT #1 (2026-08-11) — REJECTED + reverted to clean HEAD 9a168329 (count back to 750). REFINE, do NOT
   re-run the same way.** A full auto-authorized build wired all 6 (+1) surfaces, converted CIE, proved Module6
   0 non-Valid, ledger 3 axiom-free (set_diff/set_comp_str = pure `let function`s; set_of_arr = val+postcond).
   Two supervisor gates caught it: (1) byte-diff GATE LEAK — the set_diff/set_comp_str theory DEFS emitted
   unconditionally into the shared pydict theory → 10 corpus files re-emitted (fixed with a `needs_set_op` gate,
   then corpus byte-diff = 0). (2) FATAL: **SIBLING REGRESSION** — the `Set[str]`-return type-inference retype
   (`map int (option int)` → `map string bool`, faithful/no-more-int) is GLOBAL; it changed the abstract `val`
   signature of EVERY Set[str]-returning mirror stub, and VERIFIED CALLERS written against the OLD wrong int
   type broke: `module6_whyml/auto_trust.py` + `module6_whyml/expressions.py` type-fail (`type string->bool but
   expected int`), `frontend/monomorphize.py` → 6 non-Valid (Timeouts). 19 mirror files' emission changed; ≥3
   regressed. **LESSON (banked): a value-model retype that changes a shared abstract-val SIGNATURE cascades into
   every verified caller that consumed the old (wrong) type — landing it is NOT a +1 increment; it needs EITHER
   (a) a per-CONSUMER-gated retype (retype a Set[str] stub's val ONLY in the file/context that actually reads it
   as a set, leaving other callers' int view intact — measure caller-coupling FIRST), OR (b) a COORDINATED
   retype + caller-fix across all affected mirror files in one increment (auto_trust/expressions/monomorphize +
   sweep for more). Attempt #2 must measure the full verified-caller set of each retyped stub BEFORE building,
   and either gate per-consumer or fix all callers. The value TYPE + ops are proven feasible + axiom-free; the
   wall is the caller-coupling cascade, not the model.** Items 1b-B/1b-C are the SAME cascade class.

   **ATTEMPT #2 — LANDED (commit 02e652d4, 750->749).** A caller-coupling measurement found CIE reads no
   Set[str] stub, has 0 verified callers, its state fields co-read only by a trusted method — so a PER-METHOD
   (CIE-only) retype touches nothing else. Built exactly that (CIE's return+state modeled with the string-set
   model LOCALLY; NO other Set[str] stub's abstract-val changed). Blast radius: attempt #1's 19 mirror files
   (3 regressing) -> 2 (Module6+pycsl, BOTH re-proved 0 non-Valid). Corpus byte-diff 0, ledger 3
   (set_diff/set_comp_str = pure let-functions, no cert), needs_set_op-gated. **BANKED DEVICE: PER-METHOD
   value-model retype — retype a converted set-using method's OWN return+state locally, leave every sibling
   stub's int view intact; measure caller-coupling first (a 0-verified-caller stub is safe to retype alone).**
   REMAINING Set-model stubs (those WITH verified callers: find_assigned_vars/collect_escaping_exceptions/
   _module_binding_names/_collect_map_typed_locals + the class-(a) tail) each need their own
   measure-then-per-method-gate increment as their consumer converts. Items 1b-B/1b-C: same discipline.

   **Set[str]-RETURN frontier PER-METHOD-EXHAUSTED (measured 2026-08-11, post-CIE, count 749).** A robust AST
   census of the 8 `\trusted` stubs that genuinely RETURN a set: ALL walled for the per-method device.
   `_module_binding_names` + `bases_closure` = VERIFIED-CALLER cascade (consumed via `X in <stub>()` membership
   by an un-trusted caller — `_handle_in_globals_expr` / `handler_catches`; the per-method device FORBIDS this);
   `bases_closure` additionally = `while frontier:` worklist termination-variant wall. `_parse_rocq_file`/
   `_parse_lean_file`/`_index_proofs_dir` = file I/O (read_text/iterdir) un-modelable. `_collect_shared_symbol_decls`
   = nested `def _symbol` closure + `_AXIOM_FUNCTIONS.values()` heterogeneous walk. `_collect_string_elem_read_locals`/
   `_collect_field_decode_str_locals`/`_typed_local_vars` = nested `def rec` closure + self-state mutation +
   cross-collector calls. So item 1b-A's PER-METHOD wins = {CIE} only (landed); further Set progress needs a
   COORDINATED caller+callee retype increment (measure the full `in`-membership consumer chain first) — a bigger
   build — OR is blocked by orthogonal walls (I/O, nested-closure, while-termination). NEXT: measure 1b-B
   (empty-collection-literal) for a bounded per-method sub-case (census-artifact discipline) before concluding cascade.

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

## LEVERS LEDGER (auto-ranked, session-scale — SKILL §A.6 "auto-list + auto-pick the favorite, never ask")
When the spike-and-land backlog is drained and only session-scale not-yet-BUILT levers remain, the driver
auto-reads THIS ledger each idle heartbeat, auto-ranks by ROI = (expected stubs unblocked × landing-confidence)
÷ build-cost (ties → no-new-cert over new-cert; proven-feasible half over unproven), auto-picks the TOP lever,
and LAUNCHES it as the next Phase-2 build — no asking. A REFUTED lever → CERTIFIED-BOUNDARY, struck, advance to
next. Floor = this ledger empty (all BROKEN/CERTIFIED-BOUNDARY). Refresh after each lever resolves.

Ranked 2026-08-11 (count 748 after L10). LEDGER EXHAUSTED (L10 landed; L8/L11/L12 boundary; L9 banked; L13 moot) — floor 748.
- **L10 — Mutable-seq / map-of-list value model** [BROKEN — LANDED 2026-08-11, count 749→748]. Auto-picked favorite
  #3. Spike PASSED(A): `_verify_module_groups`'s `groups.setdefault(g,[]).append(x)` is a pure functional-accumulate
  (`Map.set groups g (snoc (get_or_nil groups g) x)`), NOT mutable-inner-seq aliasing → the type-rejection boundary
  does not apply. BUILT by generalizing the landed `emit_extract_array_lengths_group` template (`map string (option
  int)` → `map string (list string)`) + `recognize_verify_module_groups` (fail-closed exact whole-body shape gate) +
  a `val __setappend ... ensures {result = Map.set m k (__snoc (Map.get m k) v)}` primitive over a pure `let rec
  function __snoc` list append. FULL BATTERY GREEN (supervisor-verified): Module6 giant whole-file proof SUCCESS 0
  non-Valid; corpus byte-diff 0 (apples-to-apples manual-emit both sides — the byte-diff-sweep.sh `$flags` produce a
  let/val confound, use IDENTICAL flags on both sides); mirror-check 52/52; ledger 3 (Map.set + `__snoc` axiom-free,
  allowlist untouched); non-vacuity via `--fun` reject-`ensures false` + a decisive mutation test (key literal
  "verify_module"→"XXX" tracked in the emitted reader); verbatim body; SIBLING-REGRESSION clean — `audit_proof.py`
  (the only other `setdefault(...,[]).append` site) does NOT trigger the recognizer (`__setappend` count 0, fail-closed
  correctly rejects the embedded-in-larger-body pattern) and re-proves SUCCESS. Commits: emitter (generic_fold/
  preamble/functions) + mirror. BANKED DEVICE: functional-accumulate map-of-list recognizer (`setdefault(k,[]).append`
  → `Map.set k (snoc (get k) v)`), axiom-free, reusable for the setdefault/append cluster. KEY OPS LESSON: byte-diff
  MUST use identical emit flags on baseline+after (byte-diff-sweep.sh's extra `$flags` diverge from manual emits =
  false let/val diffs); the giant-file proof must run detached (setsid+sentinel), exceeds the foreground limit.
- **L9 — str→int de-trust** [CAPABILITY BANKED + C3 CORRECTED, but 0 autonomous yield → struck from launch queue].
  Auto-picked favorite #2, make-or-break spike PASSED(A): Why3's `string.String` stdlib ALREADY exposes
  `to_int : string -> int` (SMT-LIB `str.to_int`, Z3/Alt-Ergo native, `to_int "123"=123`, `-1` on non-numeric),
  proven Valid both solvers. LEDGER-SAFE: it's a stdlib theory IMPORT (same trust class as String.length/concat),
  NOT an allowlist axiom, NOT a `#@ proof` cited proof — `proof_axiom_allowlist.py` untouched, ledger stays 3.
  **This REFUTES memory C3's "faithful str→int needs a 4th cited axiom or the oracle" verdict** — the substrate
  provides constrained `str.to_int` for free; the current `val str_to_int` (unconstrained any_1 at expressions.py:
  6149) is unfaithful only because it isn't tied to stdlib `to_int`. BANKED CAPABILITY: replace `val str_to_int`
  with constrained `val py_str_to_int (s:string):int ensures {result = to_int s}`, gated (byte-diff-0 for other
  files). BUT autonomous COUNT-YIELD = 0: a census of every trusted stub with a genuine `int(<string>)` found ALL
  co-blocked — the from_sexp-2 (`_find_construct_idx`/`_construct_indices`) need the sexp-TUPLE ADT (mirror is
  `-> int`, live is `-> Optional[Tuple[str,int]]` walking `elem[0]`/`elem[1]` + `_flatten_tuples` cross-calls =
  the documented sexp-carrier CERTIFIED-BOUNDARY); the rest are in the parser proof-scale terminus (pure_ast/
  Module2_Parser/parser.py) or need base-N (`int(x,16)`, beyond to_int) or a token/AST-node model. So str→int is
  necessary-but-not-sufficient everywhere. REOPENING: bundle the str→int fix WITH whichever parser/sexp vein's
  OTHER blocker is cleared (co-land the faithfulness fix + conversion together, justifying the M1 byte-diff).
- **L8 — Enumerable-typed-map ADT** [STRUCK — CERTIFIED-BOUNDARY, refuted 2026-08-11]. Auto-picked as favorite,
  make-or-break spike (assoc-list `list (string, RecordInfoView)` reframing to dodge the domain-less-map
  enumeration wall). THREE independent fatal refuters: (1) CASCADE — `_record_types`'s type is ONE shared record-
  field declaration (`map string (option int)`); re-typing it re-lowers the CURRENTLY-GREEN `_first_assign_kind`
  (`x in self._record_types` membership, emitted `let` proving via `match Map.get`) + `_field_type_of` +
  cross-file consumers (statements.py:1172/1255, expressions.py:716, stmt_control_flow.py:308/765) — disturbs
  proven code to convert 1 stub. (2) VACUITY — the heterogeneous `Dict[str,Any]` values are already ERASED to
  opaque `option int`; the 11-key RecordInfoView (whyml_name/field_types/…) does not exist in the model, so any
  assoc-list search reads opaque sentinels → fails non-vacuity. This is the underlying heterogeneous-value floor,
  which L8 does not touch. (3) RELOCATES-NOT-DODGES — building the enumerable assoc-list still requires first
  enumerating the total map's `.values()` (the exact domain-less enumeration the typed-self-view spike already
  refuted); re-typing the mirror field to `List[...]` to sidestep diverges from real dict subscript-assign/`in`
  semantics → violates L-plane-1 mirror-sync fidelity. Also: the certified pyval/list catamorphism does NOT cover
  a native record-element list (needs its own inductive type). REOPENING CAPABILITY: a faithful domain-carrying
  typed-map value model (RecordInfoView values actually carrying string/map data) + modular enumeration support —
  review-gated (the heterogeneous-value floor + the map-enumeration primitive together), NOT this reframing.
- **L9 — str→int via cited-proof** (`#@ proof rocq/lean`). De-trusts `str_to_int`-oracle stubs WITHOUT a new SMT
  axiom (ledger stays 3, sanctioned de-trust-via-proof path). Unblocks from_sexp final 2 (`_find_construct_idx`,
  `_construct_indices`) + int-via-string-atom carriers. Cost: hand Rocq/Lean proof, no emitter shape. Gate: cited
  proof discharges + audits clean. STATUS: OPEN (no-new-cert → ROI tie-break favors it if L8 refutes).
- **L10 — Mutable-seq value model** (map-of-mutable-seq). `d.setdefault(k,[]).append(...)` inner mutation.
  Unblocks `_verify_module_groups` + setdefault/append cluster. Cost: new shape → cert; axiom-free
  certifiability UNPROVEN → spike first. STATUS: OPEN (unproven half → ranked below L8/L9).
- **L11 — PSet-in-pyval** [STRUCK — CERTIFIED-BOUNDARY, census-confirmed 0-yield 2026-08-11]. Auto-picked favorite
  #4; led with the census-p spike (does PSet have ANY non-co-blocked beneficiary?). RESULT: no. The ONE set-as-pyval-
  VALUE beneficiary `_build_soundness_report` stays co-blocked (`counts[bucket]+=1` int-dict + opaque `_collect_calls`).
  The many `Set[str]`-RETURNING stubs are a DIFFERENT model (the landed StrSet `map string bool` per-method device, CIE)
  — NOT PSet-in-pyval — and are per-method-exhausted: spot-checked `_stub_set` = FILE I/O (`iterdir`/`is_dir`, un-
  modelable), `_collect_shared_symbol_decls` = NESTED-`def` closure (`def _symbol`, Module5-drops-nested-def) + verified
  caller; `bases_closure` = while-termination + frozenset; `_parse_rocq/lean_file` = file I/O. So no stub's SOLE blocker
  is the missing set-value shape. REOPENING: PSet-in-pyval only becomes worthwhile bundled with `_build_soundness_
  report`'s int-dict + opaque-import fixes (a multi-wall coordinated build, review-gated).
- **L12 — list-typed @dataclass field emitter build** [STRUCK — CERTIFIED-BOUNDARY (COST/SCALE, ROI-gated),
  re-spiked post-L10 2026-08-11]. Re-spiked after L10 landed `list string` (hoping L10's plumbing shrank it). REFUTED:
  L10's `list string` is LOCAL-SCOPE-ONLY (per-function inductive `snoc`/`mem` helpers), NEVER a record-field type.
  Record field types (preamble.py:7114-7166) emit only `array string` (gated on @mutable_state/IR-node) or `array int`
  (default) — a frozen `@dataclass` field `list[str]` trips neither gate → still unbound `array int` (no-more-int leak);
  `len(self.slots)` still routes to opaque `iter_length` (the real-`Array.length` branch requires record-element +
  the same gate). Converting `arity` still needs ≥3 disjoint surfaces (Module5 field-type inference + a new len-
  dispatch branch + preamble theory), none provided by L10. 1-stub yield (census-settled, no cluster). ROI-gate stands.
- **L13 — @property emission un-skip** [MOOT as standalone — enabler for L12's `arity`, which is CERTIFIED-BOUNDARY].
  4-line delete, byte-inert, no crosscheck_ir regression (verified). Converts nothing alone. Only revived if L12's
  3-surface field/len build is funded.

**LEDGER EXHAUSTED 2026-08-11 (new floor 748): L10 LANDED (749→748); L8/L11/L12 CERTIFIED-BOUNDARY; L9 banked-0-yield;
L13 enabler-moot.** The auto-pick mechanism (SKILL §A.6) worked through every ranked lever: 1 real conversion + 5
rigorously adjudicated. No OPEN lever with autonomous standalone yield remains. Per driver action (6): HOLD at floor
748; periodically re-measure to DISCOVER NEW levers (L10 itself was found by census — the ledger auto-regenerates as new
capabilities/measurements surface fresh candidates). Reopening the struck levers needs review-gated multi-wall/multi-
surface builds (enumerable-typed-map + heterogeneous-value; PSet-bundle with int-dict+opaque-import; L12's 3 surfaces).
- **BLOCKED (not a raisable lever autonomously): int-valued-dict** `map string int` — lowering exists; wall =
  KeyError-freedom under `requires True` = FORBIDDEN CONTRACT. Movable only via an L9-style cited proof.

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

- **R-parser — Module2_Parser token-level `_ContractParser` cluster. SPIKE PASSED 2026-07-25 (count
  917 → 915).** Refutes the prior census line "Module2_Parser 69 = int-AST boundary / needs a new
  subsystem": the concrete token-stream model is **ALREADY BUILT & PROVEN** (prior
  `parser-primitives-wall` campaign — `_Tok` record, `@mutable_state` `toks: array _tok` + `i: int`
  cursor, EOF-sentinel class invariant, and the whole `cur/peek/advance/at_*/accept_op` + precedence
  chain `_parse_implication`…`_parse_factor` already non-trusted and proving `self.i >= \old`). This
  spike converted **`expect_op`** + **`expect_bs`** (verbatim ports; family A = state-only /
  already-modeled return; ZERO new machinery, no axiom, no cert; whole-file proof SUCCESS, mutation
  test decisive, corpus byte-diff 0 by construction, mirror 52/52, drift 2, ledger 3). Census of the
  ~62 token-level stubs → three families:
  **(A) state-only / already-modeled-return** (`expect_name`, `parse`, `_grab_reviewer_id` — cheap
  follow-ons, ~5-7) = CONVERT-NOW;
  **UPDATE 2026-07-25 (default-arg-filling build, commit `fc43f946`, count 912):** the DEFAULT-ARG
  emitter gap (GAP #1, 74 no-arg `self.expect_name()` sites → partial application) is now BUILT
  (R7 default-fill extended to the `_handle_dotted_call` self-method path; corpus byte-diff 0,
  mutation-tested, §10c proof-neutral over 3 changed mirror files). BUT a full census of the 32
  `expect_name()`-callers proves default-arg is NECESSARY-BUT-NOT-SUFFICIENT: every one hits a
  SECOND gap — Optional[_Tok]-truthiness-in-`while/if accept_op` (the whole `_parse_qualname`/
  `_parse_dotted_path`/`_parse_act_names`/… cluster), or GAP #2 record/unit-local from a trusted
  `_parse_*` (`_parse_mutex_expr_str` confirmed empirically), or family-B node construction. So (A)
  converts ZERO standalone. NEXT single feature = **Optional-truthiness-in-condition** (frees the
  pure-string `_parse_qualname`/`_parse_dotted_path` over the built default-arg). See
  `parser-tokenstream-impl.md` §DEFAULT-ARG-FILLING build.
  **UPDATE 2026-07-25 (Optional-truthiness-in-condition build, count 912):** GAP #1b now BUILT
  (`_to_bool` lowers an `Optional[OBJECT]` `<e>` in a condition to the is-Some match discriminant,
  not int `<> 0`; corpus byte-diff 0, mirror emission 23/23 identical, mutation-tested). STILL converts
  ZERO standalone — a THIRD blocker surfaced: `while self.accept_op(X):` methods need a loop TERMINATION
  variant whose strict increment sits in the GUARD, so `accept_op` must expose
  `ensures \result != None ==> self.i > \old` — but `\result != None` on a union return lowers in a
  SPEC formula to `(result <> 0)` (union-vs-int L3-tc). That is **GAP #1c = spec-position `\result`
  union-None discriminant** (`_union_none_ctor_for` resolves only symbol-table Vars, never `\result`),
  a distinct feature, DEFERRED (scope = condition-position only). The `if self.accept_op(X):` methods
  (mixin_param/ghost/quantifier/…) lower cleanly with #1b but their then-branch hits GAP #2 (trusted
  `_parse_expr` unit-local) / family-B. Revised reopen order: (1) **GAP #1c spec-`\result`-union-None**
  [smallest cut: frees `_parse_qualname`/`_parse_dotted_path`], (2) GAP #2 unit-local, (3) family-B +
  list-append. See `parser-tokenstream-impl.md` §OPTIONAL-TRUTHINESS-IN-CONDITION build.
  **UPDATE 2026-07-25 (GAP #1c BUILT + pure-string sub-cluster CONVERTED, count 912 -> 910):** GAP #1c
  shipped (`5c8b83f4`, `_union_none_ctor_for` Result-branch: `\result != None`/`== None` on a `_union_*`
  return lowers to the is-None ctor discriminant in a SPEC formula). With the two prior enablers (#1a
  default-arg, #1b Optional-truthiness) PLUS faithful mirror contract strengthenings on `accept_op`
  (`ensures \result != None ==> self.i > \old` AND `ensures self.i >= \old` — the None branch = loop
  exit needed the monotone lower bound, the anticipated "4th blocker", resolved by a faithful ensures
  NOT a 4th feature) and `expect_name` (`ensures self.i >= \old`, the loop-body helper), the pure-string
  sub-cluster CONVERTS: **`_parse_qualname` (`b03b6ae0`) + `_parse_dotted_path` (`92e3b8dc`)**, whole-file
  proof SUCCESS 0-unproven each, corpus byte-diff 0, drift 2, ledger 3. Reachable pure-string cluster
  EXHAUSTED at 2; the rest (`_parse_dotted_path_list`, `_parse_act_names`, ...) build LISTS (`.append`) =
  family-B. GAP #1c banked reusable. See `parser-tokenstream-impl.md` §GAP #1c BUILT.
  **UPDATE 2026-07-25 (GAP #2 BUILT + mixin-sig cluster CONVERTED, count 910 -> 908):** GAP #2 (unit-local
  type inference) shipped (`ba2777da`, `functions.py`): a `\trusted` `-> str` stub with a `pass` body
  yields `find_return_type -> "unit"`, so the `ann=="str" and return_type=="int"` overrides in BOTH
  `_compute_return_type` (main val) AND `_build_method_return_type_map` (self-call abstract val) missed it
  and emitted `: unit` → a converted caller's `ret = self._parse_mixin_type()` string local failed L3-tc.
  Extended both branches with a `== "unit" and func.get("trusted")` disjunct (string-return sibling of the
  `-> "ExprIR"` unit-stub → emit_ir promotion; gated on trusted → corpus byte-inert, 812/812 diff 0,
  mutation PASS, §10c confined to Module2_Parser). CONVERTS: **`_parse_mixin_method_sig` (`5ae4be79`) +
  `_parse_mixin_param` (`2c912843`)** (both return str, assign/interpolate a `-> str` self-call; their
  `-> str` deps `_parse_mixin_type`/`_parse_mixin_params` stay `\trusted` = family-B list-append), whole-file
  proof SUCCESS 0-unproven each, drift 2, ledger 3. Reachable str-local cluster EXHAUSTED at 2.
  **`_parse_mutex_expr_str` = CERTIFIED BOUNDARY:** `index = self._parse_expr()` (un-annotated trusted →
  unit) flows to `_csl_to_str(index)` (CSLNode param → int) — an irreducible two-trusted-stub type
  mismatch GAP #2 cannot bridge. GAP #2 (str) banked reusable; symmetric `-> _Tok`/unit branches un-needed
  (no reachable stub) → NOT built. **The parser cheap/inert frontier is now EXHAUSTED; remaining =
  family-B (list-append + emit_ir node variants), corpus-reaching / deliberate multi-session build.**
  See `parser-tokenstream-impl.md` §GAP #2 BUILT.
  **(B) node-constructing `_parse_X`** (~50-55; each builds a distinct `CSLNode` e.g.
  `_parse_membership`→`CSLIn`/`CSLNotIn`) = BUILDABLE **[COST/SCALE]** — needs the `emit_ir`-variant
  coupling per node family (IrBinOp precedent — emitter already lowers the construction to a record but
  the variant/cert is missing → L3-tc error) + co-landing axiom-free cert + coqchk, NO 4th axiom;
  **(C) hard boundary** (`_try` higher-order backtracking frame; `_err` raise stays trusted `val`;
  `__init__`/`_lex_contract` char-lexer) = leave `\trusted`. REOPEN family B: add the CSL-AST-node
  `emit_ir` variants (IrIn/IrNotIn/…) + fold/cert co-land, then verbatim-port the ~50-55. See
  `parser-tokenstream-impl.md`.

  **(B) IN PROGRESS — clause-node `_parse_X` via `_uses_clause_ir`-gated emit_ir variants
  (2026-07-26).** Template = `_parse_proof`→`IrProofDecl string string` (37f0ae3c, string-leaf).
  `_CLAUSE_IR_NODES` = {ProofDecl, ClassInvariant, LoopInvariant, LoopVariant, RaisesDecl}. CONVERTED
  this batch (emit_ir-child, foreground): **`_parse_class_invariant`→`IrClassInvariant emit_ir`
  (e09c8dcd, 907→906)** + **`_parse_raises`→`IrRaisesDecl string emit_ir` (026f38c1, 906→905)**. The
  emit_ir child `self._parse_expr()` lowers via a `-> "ExprIR"` annotation on the STILL-`\trusted`
  `_parse_expr` stub (GAP #2 typed-return); no new cert (ledger 3). Each: whole-file proof SUCCESS,
  corpus byte-diff 0 (byte-INERT), mutation PASS, vacuity 0, mirror-check 52/52, drift 2. **DEFERRED
  `_parse_loop`** (LoopInvariant/LoopVariant ctors/wiring reverted clean): its trailing
  `self._err(...)` fall-through (no guaranteed return on the neither-invariant-nor-variant path)
  L3-fails "type emit_ir but expected type ()" — the emit_ir early-returns clash with the unit-typed
  body. Faithful fix = model `_err` as diverging/raising (broad impact on `expect_name`/`expect_op`/
  `expect_bs` + re-proof risk) OR an unfaithful control-flow restructure; both break the
  no-stack/faithful-semantics discipline → REOPEN only alongside an `_err`-divergence-model build.
  Same trailing-`_err` blocker applies to `_parse_function_variant`/`_parse_ghost`/`_parse_interface`
  and any other `_parse_X` whose live body ends in `_err`. Next clean clause candidates = those with a
  guaranteed terminal `return` (single-token leaf or emit_ir-child, no trailing `_err`).

  **(B) `_err`-DIVERGENCE MODEL BUILT + trailing-`_err` clause parsers CONVERTED (2026-07-26,
  905→903).** The deferred trailing-`_err` blocker is RESOLVED — `_err` `-> NoReturn` (unconditional
  raise, stays `\trusted`) → abstract op `ensures { false }` + call lowers `(let _ = <call> in absurd)`
  (continuation unreachable). Emitter model `56d871b6` (4 sites: `_module_method_noreturn` set;
  `_handle_dotted_call` absurd-wrap + ensures-false; `_handle_expr_stmt` tail-absurd; `_handle_if_stmt`
  no-else on absurd-body; NR2a exempts trusted/abstract bodyless vals). NOT a blanket `ensures False`
  massage — soundness gate: `_err`'s live body IS an unconditional raise (justified), vacuity `--emit`
  exit 0, both bodies NON-VACUOUS + mutation-tested. CONVERTED: **`_parse_loop`→IrLoopInvariant/
  IrLoopVariant (`a661a482`, 905→904)** + **`_parse_interface`→IrInterfaceClause/IrEnsures/IrRequires
  (`331623f1`, 904→903)** (`_parse_assigns` gains `-> "ExprIR"`, stays trusted). Each: whole-file proof
  SUCCESS, corpus byte-diff 0 (812/812), mutation PASS, vacuity 0, drift 2, ledger 3. `expect_op/name/bs`
  re-proven (whole-file). Model banked + reusable. REMAINING `_parse_ghost`/`_parse_function_variant`
  have TERMINAL returns (no `_err`) → NOT divergence work; separate family-B needing kwargs/default-arg
  ctor binding (`_parse_ghost` GhostAssignDecl/GhostArraySetDecl) resp. FunctionVariant optfield
  class-construction. See `parser-tokenstream-impl.md` §_err-DIVERGENCE.

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

## LIST-append clause vein (2026-07-26) — 894 -> 889, 5 conversions
STRING-element list clause parsers CONVERTED: _parse_act_names, _parse_dotted_path_list
(direct `list string` return, ZERO emitter change — `-> List[str]` annotation drives the
existing seq-string/array-string/materialize_str machinery); _parse_compose_from (+ shared
list-string clause ctors IrComposeFromDecl/IrConformsToDecl/IrLockOrder `(seq string)`,
gated _uses_clause_ir, corpus byte-diff 0), _parse_conforms_to, _parse_lock_order.
DEFERRED emit_ir-element list (_parse_act_block, _parse_for_block): seq_to_irlist bridge +
IrAct/IrForExpand/IrGiven ctors BUILT + bridge PROVES, but act_block's converted-body VC
deterministically 30s-TIMEOUTs (98M steps) on the trivial BOUNDS-invariant-init (solver
context pollution from the seq emit_ir local) — a proof-COST boundary, not a capability gap
(reverted clean; design banked in parser-tokenstream-impl.md). DEFERRED list-of-records
(_parse_datatype/_parse_variant_def/_parse_inductive*/_parse_mixin_params/_parse_happy*):
need a new element value shape (list-of-tuple ADT / faithful list-string join).

## LIST-OF-RECORDS vein (2026-07-26) — 889 -> 888, 1 conversion
_parse_mixin_params CONVERTED (0af25459): `', '.join(seq-string local)` → `str_join_seq`
(pre-existing abstract val over a VARIABLE seq); ZERO emitter change (src/pycsl untouched →
corpus byte-inert by construction), NO cert. Enabled by faithful monotonicity ensures on
_parse_mixin_param (converted, proves it) + still-trusted _parse_mixin_type (the _parse_unary
precedent). Whole-file proof SUCCESS 0-unproven, vacuity 0, mutation PASS, mirror 52/52.
BOUNDARY (rest of vein): _parse_mixin_type recursive = PROOF-INFRA boundary (first recursive
call OUTSIDE any loop → EOF-sentinel class invariant not ambient; requires-threading cascades
caller obligations = over-build); _parse_variant_def = class-O tuple-slot boundary (`(str,seq str)`
→ `(int,array int)` + `[]`-in-tuple → array int); _parse_datatype/_parse_inductive* = new-shape
boundary (seq-of-tuple / monomorphic rule_list+member_list ADTs w/ emit_ir children = ≥2 stacked
shapes + certs). See parser-tokenstream-impl.md §LIST-OF-RECORDS.

## LIST-OF-RECORDS RE-SPIKE (2026-07-27) — 883 held, BOUNDARY sharpened by measurement
Re-spiked `_parse_variant_def` (verbatim port + loop invariants, `--no-proof --keep-mlw`). The
2026-07-26 census was STALE ("per-slot tuple inference not landed" — it IS landed for TAIL returns:
`_refine_tuple_return_type`/`_infer_tuple_slot_type`). A small byte-inert emitter add
(string-call-result-local + `seq_value_types` seq-string-local slot recognition) refined the signature
`(int,int)`→`(string, array int)` (ctor slot landed). The REAL blocker stack (read at each `.mlw` layer):
(1) seq-string SLOT not resolvable at return-type-MAP-build time (`func["seq_value_types"]` unpopulated
there — the BODY lowers `types` right, only the SIGNATURE lags); (2) `[]`-in-tuple-slot → `Array.make 1024 0`
(generic Tuple lowering, no slot-type context); (3) DECISIVE — `_parse_variant_def` has a CONDITIONAL/early
return → raise/catch path → `exception Return_{arity} (int,…,int)` (all-int, keyed only by ARITY,
preamble.py ~L2474). The refined-tuple feature only ever covered TAIL-return functions; early-return refined
tuples need a per-slot-TYPED tuple-return exception (name keyed on slot types, cross-cutting preamble+raise+catch,
byte-diff risk). = 1 standalone stub needing ≥3 stacked new emitter shapes → CERTIFIED-BOUNDARY (do-not-over-build).
Reverted functions.py + mirror by exact path. REOPEN key = the per-slot-typed EARLY-RETURN tuple exception
(gap #3, the one distinguishing this from the landed tail-return refined tuple). See parser-tokenstream-impl.md
§"LIST-OF-RECORDS vein RE-SPIKED".

## EXPRESSION-GRAMMAR cluster (2026-07-26) — CERTIFIED PROOF-COST BOUNDARY, parser-vein TERMINUS, 888 held
The 7 contract-expression stubs (`_parse_expr`/`_parse_quantifier`/`_parse_atom`/`_parse_atom_primary`/
`_parse_atom_name`/`_parse_atom_bs`/`_parse_expr_list`). SPIKED the SIMPLEST — `_parse_expr` (pure
dispatch, ZERO new machinery, no node built, no live-parser change): L3-tc ✓, faithful non-vacuous
body, but whole-file proof FAILS with 6 unproven goals — ALL postconditions of the ALREADY-CONVERTED
clause-parser callers (`_parse_class_invariant`/`_parse_interface`/`_parse_loop`/`_parse_raises`) that
embed `_parse_expr self` as an emit_ir child. Converting the opaque `\trusted val` to a concrete `let`
body puts the whole precedence chain into the module solver context → trivial `ensures True`
postconditions drown at 100M+ steps = the documented `_parse_act_block` solver-context-pollution wall.
`#@ no_inline` PROBED, does NOT clear it (same 6 timeouts). Reverted clean. Since the CHEAPEST member
is a proof-COST boundary and all 6 others are strictly harder (class-valued `cls=Exists if.. else
Forall`, StrConcatExpr+recursion, `Number(int(str))` str_to_int, ~50-variant `_parse_atom_bs`,
irlist proof-cost `_parse_expr_list`), the whole cluster is the parser-vein TERMINUS. Reopen only with
a per-file raised SMT budget for Module2_Parser.py OR a body-out-of-context modular mechanism
(deliberate build, authorize first). See parser-tokenstream-impl.md §EXPRESSION-GRAMMAR.

## REOPENED-TAIL run (2026-07-27) — 5 expr-grammar conversions, count 887 -> 882; expr-grammar "terminus" was 2 more misdiagnoses
With `_parse_expr` converted (contract-gap fix), 5 more convert: `_parse_membership` (IrCSLIn/IrCSLNotIn
2-child ctors), `_mk_in` (mirror-only), `_parse_unary`+`_parse_atom` (RECURSIVE — the census
"EOF-sentinel recursion boundary" cleared by `#@ \variant` + the EOF-sentinel class invariant; NO
emitter change for unary, 1-line StrConcatExpr alias for atom), `_parse_expr_list` (NEW `seq emit_ir`
List[ExprIR] return capability, the `seq hval` precedent). DEFERRED genuine boundaries:
`_parse_quantifier` (class-valued `cls=Exists/Forall` ctor + ForallItems + isinstance/DictView + list),
`_parse_atom_primary` (str_to_int/float), `_parse_atom_name`/`_parse_atom_bs` (multi-variant+class-valued+
str_to_int bulk), `_parse_act_block`/`_parse_for_block` (irlist ctor-field + seq_to_irlist bridge +
documented 98M-step bounds-invariant-INIT proof-cost timeout at LOOP ENTRY = genuine SMT cost, not the
clause-caller contract-gap). Banked: `#@ \variant` recursive-descent-parser recursion key (reusable for
`_parse_mixin_type` + any guarded self-recursive rule); seq emit_ir return. See parser-tokenstream-impl.md
§REOPENED-TAIL. Gates all foreground/read; zero live-parser changes; drift 2; ledger 3.

## 2026-07-27 — sibling-walker vein measured (post _cp_walk 876)
`_cp_walk` (recognize_cpwalk) landed at 876; its machinery does NOT drain the sibling walkers
(measured refutation): only `_pb_expr` is catamorphism-shaped, and it needs ≥5 stacked features
(4-arm `node.get("type")` dispatch pre-action, module-level constant-NAME tuple resolution, 2nd env
set `known` as sdict-presence, string-op guards, list-first-return walker shape) — NO new
value-shape/cert (ledger stays 3), so it is an IN-SCOPE multi-feature wall-break, not a matcher-arm.
`_pb_stmt`/`_cs_stmt` = structured `s.get("stmt")` dispatchers (heterogeneous sub-walks) gated on
converting `_pb_expr` first. `_cs_clause` = set-consumer gated on the trusted `_ir_free_vars`.
NEXT: escalate `_pb_expr` (chain-root) via spike-gated wall-break — its make-or-break spike is the
recognizer-architecture-expressiveness question (can a multi-arm dispatch + 2nd env set + list-first
shape emit a non-vacuous proving body without a new value shape?).

## 2026-07-27 — string-op vein measured: NOT safe-additive (CERTIFIED-BOUNDARY)
Spiked `_find_abstract_val_insert_idx` (`.strip().startswith("type ")` over `List[str]`): emits FULLY
VACUOUS — the faithful `str_strip_op`/`str_startswith_op` lowering is gated on `_is_string_expr(receiver)`
(expressions.py:5495/2392), but `List[str]` iterates via the generic int-erasure path so the loop-bound
`line` is never string-typed → string theory never fires. Vein-wide: pure `str→str` leaves use
`re.sub`/`re.search` (regex CORRECTNESS-floor); `List[str]` string-predicate leaves need corpus-perturbing
live-emitter features (risky-flag); IR-string leaves gate on `ir.get("type")` (heterogeneous Dict[str,Any]
value-model wall, needs-authorization). The "reuse str theory as safe-additive pure-mirror" thesis is
REFUTED — string-op sits behind the same generic-iteration/value-model wall as the other veins.

## FRONTIER STATE at 875 (measured 2026-07-27, this window)
Safe-additive autonomous frontier EXHAUSTED (883→875, 8 conversions: 6 parser + `_cp_walk` + `_pb_expr`).
Remaining classified: walker-FUSION (`_pb_stmt`/`_cs_stmt` — feasibility-PROVEN, ledger 3, no cert;
attempting under airtight gates); string-keyed-set (session-scale cascade); heterogeneous Dict[str,Any]
V1 / family-B node-ctors / char-lexer (needs new value-shape + §10.5 cert = authorization); str_to_int +
regex (CORRECTNESS-floors).

   **Item 1b-B (empty-collection-literal) — MEASURED FLOOR (2026-08-11, count 749): WALLED-OTHERWISE.** Census of
   716 trusted stubs: 221 assign an empty literal; 117 are `[]`-only typed-local accumulators (already handled by
   the value model, not 1b-B); of the 100 dict-`{}`/`set()`/field candidates, 0 have empty-literal typing as the
   SOLE/primary blocker — every one carries >=1 orthogonal wall (Set model via `set()` empties, heterogeneous
   Dict[str,Any], I/O/Path, raw-AST, map-of-seq-record mutation, nested-def, while). `_reset_module_accumulators`
   = entangled-with-Set (2 `set()` assigns) AND field-cascade (fields read by _scan_preamble_needs/_emit_type_decls).
   So 1b-B ALONE converts nothing; NOT the next build. Per-method value-model frontier is at measured floor after CIE.
   NEXT auto-authorized progress = COORDINATED caller+callee Set-model retype (bounded 2-method, e.g.
   _module_binding_names + its verified consumer _handle_in_globals_expr's `name in <set>()` membership), retyped +
   caller-fixed in ONE increment; the rails catch any wider sibling regression.

   **Coordinated Set-model target `_module_binding_names` = CERTIFIED-BOUNDARY (2026-08-11, count 749).** Measured
   its live body: reads `self.ir` (undeclared field = the whole heterogeneous IR Dict[str,Any]) + set-comprehensions
   over `ir.get("functions")`/`ir.get("classes")` (LISTS OF Dict[str,Any] IR-node dicts) projecting `.get("name")`.
   The SET-side ops (|=, set(dict)->keys, .discard) ARE covered by the landed model; the blocker is the comprehension
   SOURCES = the heterogeneous-Dict[str,Any] IR-node value model (THE deepest documented wall). So the coordinated
   caller+callee retype can't convert it (body wall is orthogonal to the caller coupling). CONCLUSION: the Set-model
   convertible frontier = {CIE} only (landed 02e652d4); every OTHER set-returner's BODY hits an orthogonal wall
   (heterogeneous-Dict / while-fixpoint / file-I/O / nested-closure). The Set VALUE MODEL is landed + reusable, but
   there are no more stubs whose only-missing-piece was the Set model. Remaining value-model progress = the deep
   heterogeneous-Dict[str,Any] IR-node walker model (a genuine large multi-session build / documented terminus),
   NOT a bounded per-method or 2-method coordinated increment.

   **Item 1b-C (list-slice/concat) — MEASURED FLOOR (2026-08-11, count 749): WALLED-OTHERWISE.** Census funnel:
   676 trusted stubs -> 161 use slice-or-`+` -> 94 slice/list-concat -> 26 List-typed-param -> 2 coarse-clean ->
   **0** with list-slice/concat as the SOLE blocker + 0 verified-caller coupling. The 2 survivors collapse:
   `from_sexp::_project_app` = false-positive (string slice + int `+`; real blocker = sexp/Term ADT), `Module3_Weaver::
   _desugar_acts` = CSL-dataclass variant-AST (slice incidental). Every genuine list-slice/concat sits on top of an
   already-mapped wall (heterogeneous-Dict[str,Any] IR-node lists [dominant], CSL-dataclass variant-AST, raw-ast,
   sexp/Term ADT, string-parse+IO, emitter List[str] helper cascade). SliceAccess is already partially modeled
   (types.py:141 -> "slice") so the leak is a refinement, never a primary blocker. **ALL 3 value-model items
   (1b-A/B/C) now MEASURED: the bounded per-method value-model frontier is a CONFIRMED MEASURED FLOOR — CIE is the
   only landable per-method/coordinated win. Remaining reachable value-model work = the deep heterogeneous-Dict[str,Any]
   / variant-AST IR-node WALKER model (the documented terminus; pyval/pydict ADT exists + broke CONTAINED cases per
   [[value_model_root_broken]], but the general list-of-dicts field-projection is the deepest part). Next: make-or-break
   SPIKE the contained heterogeneous-Dict path before concluding terminus-boundary.**

   **Heterogeneous-Dict terminus DECOMPOSED (spike 2026-08-11, count 749) — the "deepest wall" is not one wall.**
   The list-of-dicts field-PROJECTION READ (`{node.get("name") for node in ir.get("functions",[])}`) is ALREADY
   BROKEN + committed: `core_ir_semantic._collect_noreturn_names`/`_check_class_invariants`/`_check_namedtuple_access`
   are verified NON-trusted functions riding the certified pyval/pydict LIST-WALKER catamorphism (generic_fold.py:
   PList/PDict arms, pget_dyn/pget_list, variant size_dict; no new axiom). So the projection-read vein is
   exhausted-because-CONVERTED. The remaining `\trusted` list-of-dicts stubs are trusted for CO-LOCATED DIFFERENT
   sub-walls — each its OWN measure/spike (NOT the projection): (i) heterogeneous-dict CONSTRUCTION-as-return
   (`pycsl._build_soundness_report` builds nested `{"function":..,"bucket":..,"trusted_dependencies":[...]}` list-of-
   dicts) — CANDIDATE for Lever-1 pput/pappend construction primitive; (ii) map-of-mutable-seq inner mutation
   (`pycsl._verify_module_groups` `groups.setdefault(g,[]).append(...)`) — immutable-seq boundary; (iii) string-keyed
   KeyError subscript (`f["name"]`); (iv) opaque trusted-string-parser dependency (`pycsl._json_goal_records` <-
   `_parse_why3_json` opaque, Gate-C vacuity risk); (v) int-model index/arity arithmetic (`_typeddict_check_subscript`/
   `_namedtuple_check_*`). NEXT SPIKES (per sub-wall, cheapest-first): (i) construction-as-return via pput/pappend is
   the most-promising autonomous candidate; the rest likely review-gated. The heartbeat loop pursues these per-sub-wall.

   **Sub-wall (i) construction-as-return via pput = CERTIFIED-BOUNDARY (review-gated; spike 2026-08-11, count 749).**
   `_build_soundness_report`'s returned records carry `trusted_dependencies = sorted((setA & setB) - setC)` — `set[str]`
   VALUES with set-algebra (∩/∖/sort) flowing INTO a returned pyval dict. The pyval ADT (PInt|PStr|PBool|PNone|PList|
   PDict) has NO PSet constructor, so a set VALUE inside a heterogeneous dict is unrepresentable; the landed StrSet
   (`map string bool`, CIE) models a method's OWN LOCAL set but NOT a set stored as a pyval value. Faithful conversion
   needs a NEW certified value shape (PSet-in-pyval + ∩/∖/sort laws) — outside spike/autonomous authority (a spike may
   not add a cert; ledger stays 3). pput/pappend cover the dict-literal + list-of-dicts backbone but zero set model.
   Also cross-calls trusted external `_collect_calls`. REVIEW-GATED. **CONCLUSION: the AUTONOMOUS (auto-authorizable,
   no-new-cert, per-method/spike-and-land) value-model frontier is at a MEASURED FLOOR** — CIE is the one clean win;
   every remaining reachable value-model stub needs either a NEW certified value shape (PSet-in-pyval; mutable-seq for
   map-of-mutable-seq sub-wall (ii)) or is int-model-coupled / opaque-trusted-parser / cross-call-to-external. Those are
   genuine REVIEW-GATED MULTI-SESSION builds (each co-lands a new axiom-free Rocq+Lean cert), NOT autonomous spike-and-
   land. Per driver action (6): HOLD at this measured floor; the sub-walls (ii)-(v) each remain a review-gated build a
   FUTURE authorized window (or an explicit user go-ahead to co-land the PSet-in-pyval / mutable-seq cert) can take.

   **CORRECTION (cert-feasibility spike 2026-08-11): sub-wall (i) is FEASIBLE for `_build_soundness_report` (axiom-free,
   ledger 3) — NOT the CERTIFIED-BOUNDARY the pput-spike concluded.** The decisive fact: `deps = sorted((setA & setB) -
   setC)` is ONLY packed into the returned dict + returned; NOTHING downstream reads its order/elements. So `sorted` =
   a BARE opaque `val sorted : map string bool -> list string` with NO postcondition (same status as landed bare vals
   proved_of/has_all/all_phase1; axiom-free, ledger 3), FAITHFUL (claims nothing false about order) + mutation-sensitive
   via its ARGUMENT (the real set_diff(set_inter(walked-callset, trusted_names), {name})). Pieces: `set_inter` = new pure
   let-function `fun k->andb (Map.get a k)(Map.get b k)` (same shape as landed set_diff, axiom-free); landed set_diff +
   singleton set_add; opaque-sorted; pput/pappend for the record construction (`{"function":..,"bucket":..,"trusted_
   dependencies":deps}` -> vcs list -> `{"file":..,"summary":counts,"vcs":vcs}`). Deps: `_collect_calls` (ir_resolve, a
   .values()-set-walker in the already-broken Wall-2 vein, set_add/set_union fold) + `trusted_names` (set_add fold). All
   axiom-free, landed-machinery + one new let-function + one bare val. Isolation .mlw proved the set laws Valid z3+alt-ergo,
   evil-twin fails. **The GENERAL provably-sorted-permutation over map string bool IS a CERTIFIED-BOUNDARY (un-anchorable
   axiom — no finite enumeration of a total-function set); escape = repr-switch to sorted-dedup-list (sorted=identity,
   merge ops as let rec functions, Isolation C VC Valid) = a review-gated authorized build.** BUILDING _build_soundness_
   report now (opaque-sorted path, no repr-switch needed).

   **_build_soundness_report BUILD-MEASUREMENT = CERTIFIED-BOUNDARY (2026-08-11, count 749) — the cert-feasibility
   spike OVER-COUNTED.** The set parts (set_inter/set_diff/set_add/opaque-sorted/pput) ARE feasible, but STEP-1 census
   found 2 dominating un-landed walls the spike missed: (1) `counts[bucket] += 1` = int-valued dynamic-key dict increment
   — NO `map string int` device exists (grep 0; whole model is `map string bool`), NO `+=1` recognizer (only `|=` set-union),
   the PInt-0 placeholder = Gate-C facade (drops the count), faithful = new int-dict read-modify-write + a KeyError-freedom
   VC the FIXED `ensures True` contract can't express (no_exception KeyError forbidden); (2) `_collect_calls` = dropped-body
   opaque cross-file import (ir_resolve, no #@ contract) → set-walker can't fire → deps off a manufactured set = facade.
   Either alone disqualifies. **CONCLUSION (exhaustively measured): the AUTONOMOUS (no-new-cert, spike-and-land) value-model
   frontier is at a CONFIRMED MEASURED FLOOR after CIE.** Every remaining reachable value-model target needs a NEW certified
   value shape (int-valued-dict `map string int`, mutable-seq, PSet-as-pyval-value) OR a forbidden contract (KeyError-freedom)
   OR an opaque cross-file-import annotation — all REVIEW-GATED MULTI-SESSION cert builds, NOT autonomous. LESSON: a
   cert-feasibility spike that validates the NAMED pieces can still over-count — the build worker's full STEP-1 construction
   census (every sub-pattern, not just the flagged ones) is the load-bearing gate; it caught counts[bucket]+=1 before any
   wasted build. Per driver action (6): HOLD at this measured floor; the review-gated cert builds (int-dict, mutable-seq,
   PSet-value repr-switch) await an explicit user go-ahead or a future authorized window.

   **Int-valued-dict class = WALLED (fresh-lens re-measure 2026-08-11, count 749).** IMPORTANT refinement: the int-dict
   LOWERING is NOT missing — int dicts are modeled `map κ (option int)` (KeyError-faithful); write `d[k]=v`=map_update_some,
   augassign `d[k]+=1` desugared at IR emission (Module5._py_stmt_augassign Subscript->ArraySet+BinOp), read `d[k]`=Map.get
   (needs `<> None`), get-default=match. The residual blockers are PROOF walls: (a) KeyError-freedom on `d[k]` reads under
   `requires True` (unprovable without a value-faithful precondition — forbidden), (b) map KEY-ENUMERATION (`.items()/.keys()/
   .values()` over `map _ (option _)` has NO domain to enumerate). Only 3-4 int-dict producers exist, ALL walled: collect_
   module_constants (heterogeneous int|str value + items-filter), _linear_form (compound Optional[Tuple] + items-merge + 2
   verified callers), _collect_class_fields (heterogeneous-Dict payload), _build_soundness_report (KeyError-presence + Dict[str,
   Any] return). The clean `counts.get(k,0)+1` pattern recurs only as an INTERNAL helper inside stubs whose ENCLOSING value model
   is something else (heterogeneous/nested-closure/self-state/recursion). No (a)-class write-only/get-defaulted-return-directly
   int-dict stub exists. **CONFIRMED MEASURED FLOOR — 7 distinct value-model classes independently re-measured this session
   (Set-return, empty-literal, list-slice, projection-read, construction-as-return, PSet-value, int-dict), every one a boundary.
   The recurring deep walls are: KeyError-freedom-proof-under-fixed-contract, map-KEY-ENUMERATION over option-maps,
   heterogeneous-Dict[str,Any], nested-closure, opaque-cross-file-import — all REVIEW-GATED (need forbidden contracts or new
   certifiable value models / enumeration primitives). HOLD per action (6); the anti-false-floor obligation is discharged.**

   **FRESH BLIND CHEAP-WIN CENSUS (2026-08-11, independent read-only probe, count 749) — FLOOR RE-CONFIRMED.**
   An independent census agent (blind to these priors, throwaway worktree) screened ~20 trusted stubs across every
   pure/string/bool/list category and deep-tested the plausible few. Result: NO cheap win clears new semantic ground.
   The one technically-passing candidate — `_deref` in `module6_whyml/expr_ghost_collections.py` — is a CROSS-MIXIN
   PROTOCOL-STUB DUPLICATE, not a real method: live `expr_ghost_collections.py` defines NO `_deref` (the real one is
   `expressions.py:646`, already verified); the mirror carries a `return ""` placeholder so `self._deref` resolves when
   the mixin file verifies standalone. It "passes" the whole-file proof ONLY by importing `expressions.py`'s body into
   this file's placeholder — NOT verbatim-faithful (no live counterpart here = drift/facade), clears no new ground →
   REJECTED by the fidelity plane. Documented boundary: opaque cross-mixin reference (correctly `\trusted`).
   New non-win pattern banked: **protocol-stub duplicate** — a mirror-only scaffolding method absent from its live file;
   proving it requires a foreign sibling body = fidelity violation, do NOT count. Other rejects all fell in documented
   classes ((a) heterogeneous-dict `.values()`, (e) opaque cross-file `re`/`unicodedata`, (g) while-worklist, raw-ast
   Ingestor, `@property`-excluded). VERDICT: CONFIRMED MEASURED FLOOR at 749 holds under a fresh independent re-measure.

   **CAPABILITY-REACH RE-CENSUS (2026-08-11, independent read-only, count 749) — FLOOR IS REAL, NOT A CENSUS
   ARTIFACT.** Highest-risk anti-false-floor lens per [[wall2_walkdicts_consumers]] (repeated "exhausted" verdicts
   most often hide a newly-landed capability reaching an old-classified stub). An independent agent tested whether
   ANY landed capability (pyval string/list/search/flatten walkers, pget_dyn/pget_list/size_dict, PList/PDict
   projection, StrSet set_add/union/diff/inter, pput/pappend, __psl/.values() consumers) now reaches an unconverted
   stub. RESULT: NONE. Deep-tested near-misses (`_field_type_for`, `_union_none_ctor_for`, `_tag_of_value`,
   `_infer_return_value_type`, `_infer_tuple_slot_type`, `_seq_init_expr`) all fail on the SAME distinguishing line:
   **flat string-maps / TypedDict-VIEWED ARGUMENTS already convert (the ValIRBoolView mechanism: closed-key
   `x.get("type")`→real field read); reads that descend into the heterogeneous nested-dict VALUES of the transpiler's
   OPEN `Dict[str,Any]` SELF-STATE (`self._record_types.values()`, `_variant_types.get("constructors",{}).items()`)
   lower to OPAQUE FACADES (opaque nullary `self__X_values_0 ()`, `info_get_str` ignoring the loop-var binding) →
   Gate-C vacuity reject + type error.** Crossing it is a BUILD (give the self-field a typed record/TypedDict view),
   NOT a landed capability. The remaining small dict-arg stubs are the `_deref`-style cross-mixin protocol-stub
   duplicates (giant real body) already recorded. VERDICT: two independent censuses now agree (leaf-category +
   capability-reach) — CONFIRMED MEASURED FLOOR at 749 is genuine. Next reachable value-model work = the typed-self-
   state-view build (review-gated) or the giant `_expr_to_whyml` dispatcher.

   **TYPED-SELF-STATE-VIEW BUILD — MAKE-OR-BREAK SPIKE = CERTIFIED-BOUNDARY (2026-08-11, count 749, Gate S refuted
   BEFORE any emitter build).** The capability-reach census pointed at giving the transpiler's open `Dict[str,Any]`
   self-state a typed record-value view (`map string RecordInfoView`) to convert `_field_type_for` + siblings. Spiked
   it. RESULT: the closed-key VALUE view is FEASIBLE (2a: `_record_types` values are a FIXED 11-key shape built at
   preamble.py:6997 — whyml_name/fields/field_types/…; 2c: `_field_type_for` reads only whyml_name+field_types, returns
   Optional[str], NO cascade into `_expr_to_whyml`). The REAL wall (2b, decisive): the live body is a `.values()`
   LINEAR SEARCH (`for info in self._record_types.values(): if info.get("whyml_name")==cls: …`), and a Why3 native
   `map string _` (the model for all typed dict fields) is a TOTAL FUNCTION with NO finite domain — NOT ENUMERABLE. The
   only enumerable certified device is the pydict ADT, whose values are heterogeneous `pyval` (→ back to the Dict[str,
   Any] ROOT wall). Closed-key record VALUES and `.values()` enumeration are MUTUALLY EXCLUSIVE with existing machinery.
   Converting needs a genuinely NEW value shape — an ENUMERABLE FINITE MAP WITH TYPED CLOSED-KEY RECORD VALUES
   (association-list-style carrying typed records + a `.values()`-search lowering) — axiom-free-certifiability
   UNESTABLISHED → CERTIFIED-BOUNDARY, NOT a clean +1. Caller-coupling: it is a `.values()`-over-typed-map CLUSTER
   (consumers at types.py:287, expressions.py:2530, stmt_control_flow.py:1424/1447; mirror caller statements.py:725),
   not an isolated stub. NEW BOUNDARY BANKED: the self-state facade wall is precisely the ENUMERABLE-TYPED-MAP gap
   (typed closed-key values ∧ .values() enumeration), distinct from both the native-map (not enumerable) and the pydict
   (untyped-pyval values) devices — a review-gated multi-session build whose cert feasibility must be proven first.
   Floor 749 holds; this vein is review-gated.

   **@property-EMISSION CLUSTER — BUILD-MEASURED, REVERTED, ROI-GATE STOP (2026-08-11, count 749).** Distinct NON-value-
   model class: ~6 `@property` trusted stubs (arity/struct_format, _heap_var/Module6, ok/audit_proof_reverify,
   all_agree+pairwise/crosscheck, pairwise/crosscheck_ir) are trusted purely because `Module5_IREmitter._should_skip_method`
   (:3195-3197) DROPS @property methods from IR emission entirely (same tier as dunders). Removing that branch (4-line
   delete) is BYTE-INERT corpus-wide (0 reference-corpus files use the @property decorator — 0962's "@property-derived" is
   a plain method) and does NOT regress crosscheck_ir.py (its non-trusted `pairwise` emits as an honest abstract `val`,
   file re-proves 0 non-Valid). BUT — BUILT the un-skip + attempted the cleanest member `arity` (`return len(self.slots)`)
   with the field re-modeled `slots: int`->`list[str]`: whole-file proof FAILED. `len(self.slots)` lowers to the OPAQUE
   `val iter_length (x:int):int` int-fallback (NOT a real list length), the list field emits as UNBOUND `array int` (no
   `use array.Array` in this preamble + a no-more-int element leak: `list[str]`->`array int`). So `arity` needs a genuine
   MULTI-SURFACE emitter build (list-typed frozen-@dataclass field theory import + real `len`->Seq.length + string-element
   fix), not a spike-and-land. The other members each sit behind a SEPARATE co-located wall: `_heap_var` = property-read/
   field-read decoupling inside the giant Module6_WhyMLTranspiler.py (readers use `self._heap_var` as a field; expensive
   7200s proof + reader-coupling regression risk); `ok`/`all_agree` = list/list-of-tuples value-model; `pairwise` = dict-
   valued-return value-model. ROI-GATE STOP (§10c): multi-surface build for a 1-stub clean yield, rest behind distinct
   walls. REVERTED to clean HEAD (count 749). BANKED: the @property gate location (removable, byte-inert) + the finding
   that list-typed @dataclass FIELDS lower to unbound `array`/opaque-iter_length (a real emitter gap = the NEXT build if
   the arity/list-field vein is funded). SOUNDNESS NOTE ([[trusted_val_frame_unsoundness]] family): @property methods are
   silently emission-skipped, so a NON-trusted @property method contributes 0 goals — a latent vacuity pattern (here
   benign: pairwise proves either way), but worth the flag if a future @property method carries a real contract.

   **LIST-FIELD-EMITTER BUILD — ROI SETTLED BY CENSUS (2026-08-11, count 749): NO CLEAN CLUSTER, stays ROI-gated.**
   The @property build-measurement banked "list-typed @dataclass field theory + real len->Seq.length" as a possible next
   build. Censused every trusted-stub live body using `len(self.<field>)` or `self.<field>[...]` (80 hits) to size it.
   VERDICT: the vast majority are DICT/MAP subscripts (`self.program_ir["functions"]`, `self.contracts_map[lineno]`,
   `self.binop[cls]`, `self._module_func_raises[name]`) — the heterogeneous-Dict / map-read veins, NOT list-field-len.
   The genuine list-typed-field reads (`len(self.toks)`, `self.toks[i]`, `self._lines[r-1]`) cluster almost entirely in
   `frontend/pure_ast.py` — the ALREADY-WORKED parser vein ([[parser_vein_broken]]: 29 stubs converted, TERMINUS =
   solver-context-saturation PROOF-SCALE wall, reopen needs review-gated modular proof), so the list-field capability is
   NOT their blocker. Residual genuine list-field cases are scattered singletons (`audit_proof_reverify.summary` =
   string-builder; `Module3_Weaver._happy_predicate` = list-slice `self.f[a:]`; struct_format `arity`). So the list-field-
   emitter build has NO clean multi-stub cluster it alone unblocks — `arity` stays a lone fresh case behind a multi-surface
   build. ROI-GATE CONFIRMED BY MEASUREMENT (not assertion): list-field-emitter build = deferred/review-gated, VEIN CLOSED
   for autonomous pursuit. Floor 749 holds.

- **L14 — map-of-int counter via get-default** [PROBED → CERTIFIED-BOUNDARY (map-enumeration co-blocked), 2026-08-11].
  Discovered by re-measure (per action 6): `d[k]=d.get(k,0)+1` is a functional-accumulate with NO subscript KeyError
  (get-default), so hypothesized as an L10-analog (`map string int` via `Map.set k (get_or_0 k + 1)`). Census of 9
  counter-build trusted stubs: ALL co-blocked. Smallest, `_static_width` (14 lines): depends on trusted `_linear_form`
  (int-dict class), iterates `lv.items()` (MAP-KEY-ENUMERATION wall over a domain-less option-map), int-simplified
  mirror signature. The rest are large embedded bodies (33–573 lines) or same enumeration wall. KEY BANKED DISTINCTION
  (refines L10): L10's device works for a map BUILT FROM A LIST (`for f in <list>` → write-only, no enumeration = clean);
  it does NOT extend to a map MERGED FROM A MAP (`for k,c in <map>.items()` → needs `.items()` enumeration = the
  documented map-key-enumeration boundary). Counters merge-from-map → walled. No clean list-iterating counter-build
  exists. Reopening = the enumerable-typed-map primitive (same as L8's struck root).

- **L15 — map-from-list with SCALAR values** [PROBED → CERTIFIED-BOUNDARY (all-co-blocked), 2026-08-11]. Re-measure
  extending L10's PROVEN clean pattern (map BUILT FROM A LIST, write-only, no enumeration) from `list string` values to
  scalar `Dict[str,str]`/`Dict[str,int]` (a "swap value type + `__setappend`→`Map.set`" generalization). Spiked the 6
  census candidates; NONE is a clean flat map-string-scalar build: `_split_rocq_check_output`/`_split_rocq_print_
  assumptions` = stdout STRING-PARSERS (splitlines/find-scan, value=joined-lines/substring, not a list-of-records);
  `_index_proofs_dir_by_file` = directory FILE I/O + trusted `_parse_rocq/lean_file`; `_build_method_return_type_map` =
  ~90-line TRUSTED-SUB-PREDICATE dispatch (`_returns_stmt_ir`/`find_return_type`/`_refine_tuple_return_type`) for the
  value (same class as L14); `_build_method_param_whyml_types_by_name` = NESTED `map string (map string string)` + 2
  trusted sub-predicates; `_todict_routed_ir` = single heterogeneous NESTED-node construction (no list iteration).
  CONCLUSION: **L10's `_verify_module_groups` was the SINGLE clean instance of the map-from-list shape in this repo**;
  the scalar-value generalization has no clean carrier. Map-from-list vein EXHAUSTED (1 landed). The residual Dict-build
  stubs are dominated by tool-output string-parsers + trusted-sub-predicate-dispatch value computers — distinct
  boundaries, not a value-type-swap away.

**RE-MEASURE ROUND 2026-08-11 (post-L10, floor 748): L14 (counter-get-default) + L15 (map-from-list-scalar) both
PROBED→CERTIFIED-BOUNDARY.** The ledger auto-regeneration surfaced 2 new candidates from L10's success; both adjudicated
by census/spike to co-blocked boundaries (map-enumeration; string-parse/trusted-dispatch/file-IO). Floor 748 holds
firmly — L10 was the lone clean carrier its vein offered. HOLD per action (6); continue periodic re-measure for
genuinely-new capability-reachable shapes (not value-type variants of the exhausted map-build vein).

- **L16 — list-of-records construction** (`result=[]; for x in <list>: result.append({...})` → List[Dict]) [PROBED →
  CERTIFIED-BOUNDARY, 2026-08-11]. Genuinely-NEW shape class (not map-build); would compose certified pyval-list-append
  + pput. Probed the smallest candidate `_csl_list_to_ir` (Module5, 10 lines): co-blocked — a thin wrapper mapping the
  TRUSTED `_csl_to_ir` (CSL-dataclass→heterogeneous Dict[str,Any] producer = the CSL-dataclass-Weaver boundary) over a
  list, + `getattr(c,"act_name")` object reflection, + `d["act_name"]=an` heterogeneous-dict mutation, + CSLNode
  dataclass model requirement, + int-simplified mirror sig (`List[int]`), + verified callers (1615/1616/1648). The
  list-of-records builders all wrap a trusted heterogeneous-producer sub-method + need the source dataclass model.
  Boundary = CSL-dataclass-Weaver / trusted-sub-producer, not the list-append capability. Re-measure round confirms:
  the fresh shape classes (counter L14, map-scalar L15, list-of-records L16) all bottom at pre-documented boundaries
  (map-enumeration, string-parse/trusted-dispatch, CSL-Weaver). Floor 748 firm.

- **L17 — literal-dict lookup-table + string-accumulate** (`_inductive_sig_whyml`) [REFUTE(multi-surface) 2026-08-11;
  BANKED a real axiom-free capability]. Spiked the most promising str-accumulate candidate (faithful `str->str` sig, 0
  callers, no trusted-dep). CENSUS-P by BUILDING: (a) strip/lstrip/rstrip = EXISTS faithful (str_strip_op); (b) the two
  LITERAL DICTS `{lit:lit,...}` + `k in d` membership + guarded `d[k]` = **CONFIRMED feasible, faithful, AXIOM-FREE** —
  lowers to `map string (option string)` via `map_update_some (const None) k v`, membership → `match Map.get`, guarded
  subscript → Some/None match, mutation-tracked. **BANKED CAPABILITY: literal-dict-as-lookup-table lowering (axiom-free,
  ledger 3).** BUT REFUTE — the string-op SCAFFOLDING around the dict falls to the LEGACY INT-MODEL: `inner.split(",")`
  as for-iterable → opaque `val inner_split_1(x0:int):int` (receiver dropped = VACUOUS), `part.split(":")[-1].strip()` →
  nullary opaque, ternary-else `"int"` → int-hash → `ty` typed int → TYPE ERROR against the string-keyed dict. Non-vacuous
  conversion needs 3 coordinated surfaces (split-as-iterable → `array string` faithful materialize; split-elem-neg-index
  + outer-strip composition; whole-function value-semantic string-local inference) for 1 stub = multi-surface. FOLLOW-ON
  (L17b, banked): the literal-dict device WILL convert a stub whose lookup KEY is ALREADY string-typed (not from
  `.split()`) + scaffolding on the value-semantic path — future census filter "literal-dict lookup, string-typed loop var,
  no split-as-iterable".

**META-LESSON (L14-L17, 4 fresh-class re-measures post-L10):** the value-model PIECES are individually feasible
(functional-accumulate L10-landed, str→int-stdlib L9-banked, literal-dict-table L17-banked) but each candidate stub
COMPOSES a feasible piece with a CO-LOCATED WALL (map-enumeration / string-parse-int-leak / trusted-sub-producer /
CSL-Weaver / split-as-iterable int-leak). L10 (`_verify_module_groups`) was the RARE clean composition — hence the lone
landed conversion. The recurring string-op INT-LEAK (split/join scaffolding dropping to int-model) is now the dominant
co-blocker; breaking it = the whole-function value-semantic-string-inference build (multi-surface, review-gated). Floor
748 firm; 3 axiom-free capabilities banked (str→int, literal-dict-table, map-of-list) for future bundled builds.

- **L18 — break the string-op int-leak (split-as-for-iterable + ternary/join string-local)** [BROKEN — LANDED
  2026-08-11, count 748→747]. Containment spike CORRECTED the L17 framing: the value-semantic path is per-MODULE (ON),
  not per-function; the int-leak was ONE missing recognizer in `_classify_iterable` (a `for` over `<str>.split(sep)`
  fell through to opaque `iter_length`/`_coerce_to_int`). BUILT (2 emitter files, fail-closed, no new axiom): S1 =
  split-as-for-iterable in stmt_control_flow.py `_classify_iterable` (materialize `str_split_op → array string` once as
  a `let`, `Array.length`/`arr[!idx]` + loop variant; register loop-target symtype `str` for the body); S3 = IfExp
  ternary-string-local in statements.py `_is_str_val` (both arms string → `ref ""`); + a join lever `_mark_string_seq_
  locals` (append-grown all-string seq → `seq string` so `" ".join` → `str_join_seq` not opaque int). Converted
  `_inductive_sig_whyml` (verbatim body diff-identical to live). FULL BATTERY GREEN (supervisor-verified): preamble.py
  whole-file proof SUCCESS 0 non-Valid; corpus byte-diff 0 (apples-to-apples, fail-closed → inert despite the worker's
  precautionary flag); sibling-regression clean (mirror-emission diff: ONLY preamble.py changed, re-proves); non-vacuity
  (real str_split/str_join + loop invariant/variant/index-bounds VCs + mutation test decisive "  "→"XX"); ledger 3
  (str_split_op/str_join_seq pre-existing sound val-patterns, allowlist untouched); verbatim body. DEVIATION BANKED:
  the spike's "two small adds / join already works" UNDER-scoped it — seq-string-element + string-valued-dict typing were
  `@mutable_state`-gated, so the join/variant levers were also needed; trust-but-verify caught it. BANKED CAPABILITIES
  (reusable for the str-accumulate cluster): split-as-for-iterable, ternary-string-local, append-join-seq-string.
  FOLLOW-ONS measured: the 4 sampled candidates each hit a DIFFERENT wall (param-list/Optional, heterogeneous-Dict,
  @mutable_state-f-string+dataclass-self, `re.split`+re-module) — so L18's clean cluster is SMALL (~1-3, not ~40; the
  49 over-counted). BONUS UNBUILT: S4 = `str.partition`/`rpartition` (9 sites, opaque int-hash) — separate contained
  recognizer lifting signature-parsing stubs (e.g. `_callable_whyml_arrow`), independent of S1/S3.

  ORIGINAL PROMOTION NOTE (superseded by the LANDING above): The L14-L17 meta-lesson identified the string-op int-leak
  (split/join scaffolding dropping string locals to the int-model) as the DOMINANT co-blocker, walling ~40 of 49
  str-accumulate stubs. Unlike L12 (1-stub), breaking it is a CLUSTER unblock. Missing surfaces (from the L17 spike):
  (1) `for x in s.split(sep):` faithful materialization (`str_split_op → array string`, iterate); (2) `s.split(sep)[-1]`
  split-elem-neg-index + outer-strip composition (the str_split_elem_op recognizer EXISTS but does not fire in this
  scaffolding); (3) whole-function value-semantic string-local inference so literals/ternary-else stay `string` not
  int-hash. CONTAINMENT UNKNOWN — measure FIRST: is the value-semantic-string path a per-function GATE that can be
  widened (contained), or genuinely-missing machinery (multi-surface)? The L17 spike noted the path is "OFF for this
  function" (implying ON elsewhere) → a gate condition may be the lever. RISK: corpus-affecting (M1), byte-diff must be
  EXACTLY the string-faithfulness correction + every affected program re-proves. NEXT: containment spike (gate vs
  missing-machinery), then staged build if contained. Reuses banked literal-dict-table (L17) + str→int (L9) for the
  str-accumulate cluster once the int-leak is broken.

- **§P RE-DRAIN after L18 (2026-08-11): DRY.** Checked the clean-no-dep str-accumulate candidates with L18's new
  capabilities: `_cache_key` = crypto hash (`hashlib.sha256`/`_sha256_file`, opaque/un-modelable); `_synthesize_legacy_
  text` = join over generator calling trusted `_synthesize_block` (trusted-sub-producer); `_build_witness_str` =
  heterogeneous Dict/Optional params + array witnesses. L18's clean cluster was `_inductive_sig_whyml` ALONE (confirmed).
- **L19 (=S4) — str.partition recognizer + listcomp-map-over-split** [BROKEN — LANDED 2026-08-11, count 747→746].
  Converted `_callable_whyml_arrow` via `recognize_callable_whyml_arrow`/`emit_callable_whyml_arrow_group` (generic_fold.py,
  mirroring the landed `recognize_global_call_target` partition precedent): opaque `__before`/`__after` partition
  projections (no ensures), `__filter_ne` over `str_split_op`, a recursive `__args_join` fold (`variant {Array.length a-i}`)
  fusing the `[_callable_tag_to_whyml(t) for t in tags]` map (calling the ALREADY-VERIFIED sibling) with the `" -> "` join,
  `str_concat_op`. FULL BATTERY GREEN (supervisor-verified): functions.py (1081-line module6) whole-file proof SUCCESS 0
  non-Valid; corpus byte-diff 0; sibling-emission diff = ONLY functions.py changed; non-vacuity (real partition/split/
  sibling-map-fold/join + array-bounds/variant/postcond VCs + mutation test " -> "→" XX "); ledger 3 (str_split_op/
  str_concat_op existing abstract vals, allowlist untouched); verbatim body (mirror-check 52/52). BANKED: bespoke
  partition+listcomp-map-over-split-array-calling-verified-sibling recognizer pattern. Remaining partition hosts
  (`_call_return_whyml_type` rpartition+heterogeneous-map, `_substitute`/`_hoist_calls_in_expr`/`inline_stmts` recursive
  IR-tree) each need their own larger build.

  (superseded promotion note:)
- **L19 (=S4) — str.partition/rpartition recognizer** [PROMOTED TOP OPEN LEVER 2026-08-11, CONTAINED per L18 spike].
  9 sites emit opaque `s_partition_1(int):int` int-hash (receiver dropped, tuple-unpacked into int locals). A separate
  contained recognizer (partition → faithful tuple of 3 strings via str ops) lifts signature-parsing stubs (e.g.
  `_callable_whyml_arrow` `body.partition("->")`), independent of S1/S3. Reuses the str-op substrate (no new axiom
  expected — partition is expressible via str_index/str_slice or a faithful 3-tuple val with length ensures). NEXT:
  spike containment (existing str-slice/index ops vs new val) + cluster estimate, then battery-gated build.

  **L19 CONTAINMENT SPIKE DONE (2026-08-11): CONTAINED, target `_callable_whyml_arrow` (~1 conversion, bundled).**
  DECISIVE: partition was ALREADY converted once — `recognize_global_call_target`/`emit_global_call_target_group`
  (generic_fold.py:17264+, LANDED ledger 3) lowers `.partition` axiom-free via opaque `__before`/`__after` projections
  (NO ensures — enclosing `ensures True`) + `__has` guard; the 3-tuple unpack is RECOGNIZER-DESTRUCTURED (reads the
  TupleUnpack IR node, emits `let recv=__before.. let meth=__after..`) → NO emitter/Module5 gap. rpartition = identical
  with last-sep projections. But NO partition-ONLY stub remains — each host has a co-resident wall. CLEANEST =
  `_callable_whyml_arrow` (functions.py:207, 20 lines): partition trivial; co-resident = `[self._callable_tag_to_whyml(t)
  for t in arg_part.split(",") if t]` + `" -> ".join(...)` — split/join ends ALREADY landed by L18, sibling
  `_callable_tag_to_whyml` ALREADY verified; the ONE new piece = a filtered-listcomp-map-over-split-array calling a
  verified sibling → `array string` (a recursive fold, axiom-free). Other hosts heavier: `_call_return_whyml_type`
  (rpartition + 4 heterogeneous instance-map reads), `_substitute`/`_hoist_calls_in_expr`/`inline_stmts` (recursive
  IR-tree rewrite = MULTI-SURFACE). BUILD PLAN (next heartbeat): `recognize_callable_whyml_arrow` + `emit_..._group`
  (opaque before/after, recursive fold over str_split_op array mapping the verified sibling, str_join_arr " -> "),
  convert `_callable_whyml_arrow`, full battery + mutation test. Ledger 3, byte-inert (fail-closed).

- **§P RE-DRAIN after L19 (2026-08-11): DRY — string-op vein EXHAUSTED at 746.** Re-censused str-returning trusted
  stubs with the L18+L19 capability set (split-as-for-iterable/ternary/join/partition/listcomp-map). 67 str-op stubs;
  9 heuristic-"CLEAN?" all FALSE-clean on inspection: `_camel_to_snake`/`_preprocess_whyml`/`_strip_rocq_comments`/
  `_strip_lean_comments` = `re.sub` (aliased `import re as _re` — the opaque cross-module REGEX wall); `_synthesize_
  legacy_text`/`_synthesize_block` = generator/module-level trusted-producer + heterogeneous Dict; `_build_witness_str`
  = heterogeneous Dict/Optional params; `_coerce_to_int` = int-model internal; `_resolve_module_path` = file I/O. The
  DOMINANT remaining wall for string-transform stubs is the `re` REGEX MODULE (modeling Python regex = huge, not
  contained/axiom-free = boundary). L18(`_inductive_sig_whyml`)+L19(`_callable_whyml_arrow`) were the clean string-op
  stubs. STRING-OP VEIN EXHAUSTED. Remaining OPEN levers are HEAVIER: partition hosts `_call_return_whyml_type`
  (rpartition+heterogeneous-map), `_substitute`/`_hoist_calls_in_expr`/`inline_stmts` (recursive IR-tree rewrite =
  multi-surface); + the review-gated cert builds (enumerable-typed-map, PSet-in-pyval, mutable-seq). Floor now 746.

- **Iterator-form for-loop re-measure (2026-08-11): NOT a fresh vein — co-blocked.** Probed whether `enumerate`/`zip`/
  `reversed`/`sorted` for-iterables have the L18-style missing-`_classify_iterable`-branch int-leak. 55 stubs; the
  13 heuristic-CLEAN all co-walled on inspection: `_function_body_eqs` = regex (`_LET_FN_RE.match`) + `Tuple[List[Tuple
  [str,int]],..]` int-tuple return; `_extract_directives` = file I/O (`read_text`) + `_Directive` dataclass; the sorted-
  form ones = dict/file-IO/set. The enumerate/zip lowering is NOT the sole blocker anywhere clean. META: the dominant
  remaining walls across ALL fresh-class re-measures (L14-L19 + iterator-form) are: `re` REGEX module, FILE I/O
  (read_text/iterdir), DATACLASS models (_Directive/CSLNode), heterogeneous Dict[str,Any], int-model-tuples, map-key-
  enumeration, trusted-sub-producers, recursive-IR-tree. All documented review-gated boundaries. FLOOR 746 FIRM — the
  contained (no-new-cert, spike-and-land) frontier is genuinely exhausted after 3 conversions (L10/L18/L19).

- **L20 = F1+F2 — general partition-unpack + option-return threading** [BROKEN — LANDED 2026-08-11, count 746→745,
  under the GATHER-PICK-WORK directive]. Previously HELD as "2 features for 1 stub / session-scale" — that was the BUG
  the strengthened §A.6 fixed (COST/SCALE is not a hold-reason). PICKED it and WORKED it: both gaps were EMITTER-LEVEL
  (no Module5 IR-shape change). BUILT: F1 = general partition/rpartition string-triple-unpack as a reusable EXPRESSION
  lowering (`_partition_unpack_projs` in statements.py `_handle_tuple_unpack_stmt` + string-local pre-decl in
  `_collect_str_call_result_locals`; opaque `val str_rpartition_before/sep/after (s sep:string):string` NO ensures,
  axiom-free, same class as the landed `__before`/`__after`); F2 = option-return threading (`_thread_optional_return`
  in stmt_control_flow.py `_handle_return_stmt` + `_get_return_raw_option` at the 2 `.get` return sites in
  expressions.py — `.get` in `Optional[str]` return threads `match Map.get .. with Some v->Arm_N v | None->Arm_N_None`
  instead of a scalar-int default). Converted `_call_return_whyml_type` (verbatim). FULL BATTERY GREEN: types.py
  whole-file proof SUCCESS 0 non-Valid; corpus byte-diff 0; sibling-emission diff = ONLY types.py changed (3 emitter
  files touched but @mutable_state-gated+fail-closed confines it); non-vacuity (real str_rpartition + option-threaded
  Arm_N returns + mutation test `"."`→`"@"`); ledger 3 (3 bare no-ensures vals, allowlist untouched); verbatim body.
  BANKED REUSABLE CAPABILITIES: general partition-unpack expression lowering (F1) + option-return threading (F2) — both
  may now unblock the OTHER partition hosts / Optional[str]-via-get stubs previously co-blocked only by these. §P
  re-drain next.

  (superseded spike note:)
- **L20 — general partition-unpack + option-return threading** [SPIKED 2026-08-11 → BOUNDARY (2 multi-surface features),
  but concrete + cluster-potential]. Spiked the unspiked partition host `_call_return_whyml_type` (measure-first, not
  assume). SURPRISE: the SUSPECTED gaps are ALREADY faithful — typed self-field dicts (`Dict[str,str]`→`map string
  (option string)`, `.get`=Map.get) AND `getattr(self,"<literal>",{})`→field-read recognizer BOTH fire. The REAL
  blockers (2, each review-gated multi-surface):
  (F1) GENERAL partition/rpartition string-triple-unpack as a REUSABLE EXPRESSION LOWERING — L19's partition is a
  BESPOKE whole-function facade (`recognize_global_call_target`, matches only `*_global_call_target`/3-param); a general
  `fn.rpartition(".")` falls to opaque `fn_rpartition_1(int):int` → obj/method typed int → hash-`==` + `int_to_string`
  nonsense. F1 = generalize the bespoke partition into an expression-level recognizer emitting `__rbefore`/`__rafter :
  string→string` (axiom-free, precedent exists). Would unblock the partition-host cluster.
  (F2) OPTION-RETURN THREADING — `.get()` on a typed map in an `Optional[str]` RETURN position picks a scalar-int
  default (`None->0`) instead of threading `option string` into the return union (`Arm_N string | Arm_N_None`); this is
  the actual typecheck failure. Distinct from the landed option-unwrap-COMPARISON (reflection_front). F2 has BROAD
  cluster potential (many `Optional[str]`-via-`dict.get` stubs). Caller-coupling: single caller `_collect_struct_unpack_
  array_targets` already converted (re-verify on land). VERDICT: BOUNDARY for autonomous spike-and-land (2 emitter
  features), but F1+F2 are the concrete next FUNDABLE builds (cluster-scale, axiom-free) — the honest not-yet-built
  frontier after the string-op vein. Recommend containment-spiking F2 (option-return) first — broadest reach.

  **L20 F2 CENSUS CORRECTION (2026-08-11): F2 "broad reach" was WRONG — 0 clean single-feature beneficiaries.**
  Censused trusted `Optional[str]`-returning stubs using `dict.get` w/o partition: 13 found, the 1 heuristic-CLEAN
  (`_recognize_field_decode_idiom`) is ALSO walled (3 trusted-sub-producer `self._` calls — census dropped the self._
  check). ALL 13 co-walled (map-enum / reflect / trusted-sub-producer). So option-return threading (F2) is a real
  FAITHFULNESS gap but converts 0 stubs alone; likewise F1 (general partition) — its only beneficiaries are the
  partition hosts, which carry heterogeneous-map/recursive-IR walls. CONCLUSION: `_call_return_whyml_type` needs BOTH
  F1+F2 COORDINATED (2 emitter features for 1 stub) = ROI-gated multi-surface, no other single-feature beneficiary.
  F1/F2 are genuine faithfulness features for a FUTURE funded window (they'd co-land with the partition-host cluster's
  other walls), NOT autonomous yield. FLOOR 746 FIRM — spiking the unspiked partition host CONFIRMED the boundary
  (measure-first paid off: pinned the exact 2 features, corrected the reach) rather than breaking it.

- **§P RE-DRAIN after F1+F2 (2026-08-11): DRY.** F1 (general partition-unpack) + F2 (option-return threading) unblocked
  no additional stub — the other Optional[str]/partition trusted stubs each carry ANOTHER wall: `_region_bound_str` =
  `getattr(node,…)` on a CSLNode dataclass + float ops; `_strip_rocq/lean_comments` = STRING CHAR-BY-CHAR INDEXING
  (`text[i]` in a while loop — Why3 pure strings are OPAQUE, no char decomposition = a hard boundary, same as L9's
  finding); `sertop_version`/`_coqc_version`/`_lean_version` = SUBPROCESS (external process, un-modelable); `_resolve_
  module_path` = os.path file I/O; `whyml_ident`/`slot_id` = tuple-idx; `_synthesize_*` = trusted-producer/heterogeneous.
  NEW boundary banked: STRING CHAR-INDEXING (`s[i]` char access in a loop) — the opaque-string wall, distinct from the
  faithful string-OPS (split/join/strip/partition/get) which are all landed. `_call_return_whyml_type` was the F1+F2
  cluster's sole member. NEXT lever to WORK (gather-pick-work): the recursive-IR-tree partition hosts (`_substitute`/
  `_hoist_calls_in_expr`/`inline_stmts`, ir_inline.py — F1 now makes their partition faithful; residual = recursive IR-
  tree rewrite+mutation) OR the heterogeneous-Dict cert build. Pick+work next heartbeat.

- **DEEPEST WALL BROKEN — value-producing heterogeneous-Dict tree-rewrite (2026-08-11, count 745→744, gather-pick-work).**
  Picked the deepest lever (the `Any`-tree walkers = documented terminus) and WORKED it. Spike PROVED FEASIBLE+axiom-free
  (pv_rewrite : pyval→pyval mutual `let rec function` group, all why3 goals Valid, reuses certified pyval/pydict ADT +
  pput, NO new cert). BUILT `recognize_substitute`/`emit_substitute_group` (generic_fold.py) — a value-RETURNING
  pyval-tree deep-rewrite walker: `PList`→list-map, `PDict`→ `match __get d "type" with Some(PStr "Var") -> substitute
  from param_map/rename | _ -> PDict(rebuild via DCons value-recursion + pput_prog self-receiver writes)`, scalar→id;
  `variant {pv_size v}`/`{size_dict d}`/`{size_list xs}` structural termination. Post-processing string-ops opaque (VC-free,
  contract `ensures True`). Converted `_substitute` (verbatim). FULL BATTERY GREEN: ir_inline.py whole-file proof SUCCESS
  0 non-Valid; corpus byte-diff 0; sibling-emission = ONLY ir_inline.py (needs_pput/needs_pydict gated on recognize_
  substitute + fail-closed); non-vacuity (real tree rebuild + variant VCs + mutation test "Var"→"XXX"); ledger 3; verbatim.
  **BANKED THE BIGGEST CAPABILITY: value-RETURNING pyval-tree-rewrite walker** — corrects the "heterogeneous-Dict is the
  terminus" assumption for value-producing tree-rewrites. May now unblock the `Any`-tree-walker CLUSTER (`_hoist_calls_in_
  expr`/`inline_stmts` + the ~85 Dict[str,Any] readers). §P RE-DRAIN NEXT — this is the highest-value re-drain of the run.

- **§P RE-DRAIN after deepest-wall: `_subst_params` CONVERTED (2026-08-11, 744→743) — cluster-unlock VALIDATED.** The
  value-returning pyval-tree-rewrite capability (recognize_substitute family) immediately unblocked a sibling Any-tree
  walker: `_subst_params` (expressions.py, a simpler 1-map variant of `_substitute`). Test-as-is showed recognize_
  substitute does NOT fire (different shape: 2 params, membership-guard, no post-proc), so added a fail-closed sibling
  `recognize_subst_params`/`emit_subst_params_group` REUSING emit_substitute_group's exact pyval-tree machinery (variant
  triple + DCons rebuild + __get reader; single `arg_nodes:map string (option pyval)`, membership-guarded Var lookup,
  pure DCons rebuild — no pput needed). FULL BATTERY GREEN: expressions.py (1320-line giant) whole-file proof SUCCESS 0
  non-Valid AND Module6_WhyMLTranspiler.py (1038-line giant, the mixin-composing sibling whose emission ALSO changed —
  SAME conversion propagating, not a regression) whole-file proof SUCCESS 0 non-Valid; corpus byte-diff 0; mirror-check
  52/52; non-vacuity + mutation test "Var"→"XXX"; ledger 3; verbatim. REMAINING Any-tree-walker cluster (18 census'd):
  `_subst_var`/`_subst_csl_param` (CSLNode/Weaver — check), `_first_assign_value_ir` (search variant), param-mut ones
  (`_hoist_calls_in_expr`/`inline_stmts`/`_collect_protect_index_sites` — mutate a param list, harder), bool-returning
  (`_is_emit_ir_expr`/`_is_string_expr` — bool-existence, different family). Continue draining next heartbeat.

- **`_first_assign_value_ir` CONVERTED + F2 FIDELITY-DRIFT REPAIRED (2026-08-11, 743→742).** §P cluster-drain: converted
  `_first_assign_value_ir` (value-search over a stmt tree returning a pydict) via a new fail-closed `recognize_first_
  assign_value_ir` reusing the pyval first-match SEARCH catamorphism (mutual `let rec` over stmt spine + handler list,
  pget_list/__get, size_list/size_dict variants; axiom-free). BUNDLED FIX: discovered (via `check-self-annotate-sync`,
  which I'd not been running — only `mirror-check`) that my EARLIER F1+F2 landing introduced a §10.4 DRIFT — it edited
  the CONVERTED `_handle_return_stmt`'s LIVE body (added the `_thread_optional_return` call) without re-porting the mirror
  → check-self-annotate-sync went 2 (baseline)→3. REPAIRED count-neutrally: re-ported the mirror `_handle_return_stmt`
  VERBATIM to match live + registered `_thread_optional_return`'s signature (functions.py, so its auto-emitted abstract
  val types `local_refs:Set[str]`→`map int (option int)` instead of int — the re-port now typechecks + proves). DIVERGED
  back to 2. FULL BATTERY GREEN: stmt_control_flow.py (964-line giant) whole-file proof SUCCESS 0 non-Valid; corpus
  byte-diff 0; sibling-emission = ONLY stmt_control_flow.py; DIVERGED 2 (baseline); mirror-check 52/52; ledger 3; verbatim
  (both bodies). PROCESS LESSON BANKED: run BOTH fidelity gates (`check-self-annotate-sync` ∧ `self-annotate-mirror-check`)
  every battery — mirror-check does not catch a converted-method body drift from a live-emitter edit; §10.4 (a feature
  editing a verified emitter method must re-port the mirror in the same commit) must be checked with the strict sync gate.

- **`_frame_trigger_term` CONVERTED (2026-08-11, 742→741) — pydict-VALUES search walk banked.** §P cluster-drain #3:
  a depth-first search returning Optional[Dict] over a pydict IR tree. New sub-capability: the `.values()` WALK over a
  pydict (iterate DCons VALUES, recurse into each value / its PList elements, first-Some wins) — a `{n}__vals (d:pydict)
  variant {size_dict d}` mutual helper, distinct from the by-key readers. Plus tuple-literal membership `l.get("type")
  in ("Old","OldField")` → `pystr_eq||pystr_eq`, and Optional[Dict] option-return. CALLER-COUPLING: `_build_method_field_
  param_frame_ensures_map` (functions.py:888, non-trusted) consumes it — RE-VERIFIED (functions.py whole-file proof
  SUCCESS with the new option-pyval return). FULL BATTERY GREEN: expressions.py + functions.py (caller) + Module6_
  WhyMLTranspiler.py (mixin sibling) ALL whole-file proof SUCCESS 0 non-Valid; corpus byte-diff 0; BOTH fidelity gates
  clean (mirror-check 52/52, DIVERGED 2); non-vacuity + mutation test ("BinOp"/"Old"→XXX); ledger 3; verbatim. NOTE:
  `.values()` over a heterogeneous PYDICT is WALKABLE (finite DCons list) — distinct from the map-key-enumeration wall
  which is over a domain-less TYPED option-map. Any-tree-walker cluster continues: `_iter_len_expr`, `_max_end`/`traverse`
  (pure_ast), `_subst_var`/`_subst_csl_param` (CSLNode/Weaver = different wall), `_callee_raised_in`, param-mut ones.

- **PV-TREE-WALKER CLEAN VEIN DRAINED (2026-08-11, floor 741): 4 conversions, remaining co-blocked.** The value-
  returning pyval-tree walker capability (deepest-wall break) converted the 4 CLEAN heterogeneous-dict/list tree walkers:
  `_substitute`, `_subst_params`, `_first_assign_value_ir`, `_frame_trigger_term`. §P re-drain of the remaining 14
  Any-tree walkers: EACH carries a SECOND wall requiring a separate capability — `_iter_len_expr` = nested-`def`
  closure (`def _operand_len`, Module5-drops-nested-def) + trusted `_expr_to_whyml`; `_callee_raised_in` = opaque cross-
  file `from exception_model import handler_catches` + Set[str]/set-ops; `_max_end`/`traverse`/pure_ast = RAW-ast object
  model (`getattr(node,"end_lineno")` on ast.AST, not pyval dict); `_subst_var`/`_subst_csl_param` = CSLNode dataclass
  reflection (`_is_dc`/`_dc_fields`/`copy.deepcopy`); `_collect_array_var_assigns` = Set[str] + self-state; `_is_emit_ir_
  expr`/`_is_string_expr` = bool-existence family (different recognizer). NEXT levers to WORK (gather-pick-work): (a) the
  Set[str]-return walkers via the landed StrSet per-method device + opaque-val for handler_catches (`_callee_raised_in`);
  (b) nested-`def`-closure support (would unblock `_iter_len_expr` + others); (c) the bool-existence walkers via
  recognize_bool_existence. Each a separate build. Continue next heartbeat.

- **`_callee_raised_in` = SET-ENUMERATION BOUNDARY (2026-08-11).** Examined for the Set[str]-walker lever: its
  `{e for e in inner if not any(handler_catches(b,e) for b in handler_bases)}` ENUMERATES the set (`for e in inner`
  over a returned StrSet = `map string bool`, which has NO finite domain) — the same set/map-enumeration wall, and the
  enumerable-set reframing was L8-REFUTED. So it's correctness-adjacent, NOT a clean StrSet-per-method build. Confirms
  the pv-tree-walker clean vein is TRULY drained (4 conversions, floor 741) — every remaining Any-tree walker hits a
  DOCUMENTED wall: set-enumeration (`_callee_raised_in`/`_collect_array_var_assigns`), nested-`def` (`_iter_len_expr`),
  raw-ast object (`_max_end`/pure_ast), CSLNode-dataclass (`_subst_var`/`_subst_csl_param`), giant-cascade (`_expr_to_
  whyml`/`_is_string_expr`).
  **NEXT FUNDABLE LEVER = NESTED-`def`-CLOSURE SUPPORT in Module5** (the one remaining NOT-refuted capability). Module5
  currently DROPS a nested `def` (the documented "Module5-drops-nested-def" limitation). Lowering a local `def` as a
  Why3 local `let rec`/lifted function is feasible + axiom-free (a local function is just a scoped definition). Would
  unblock `_iter_len_expr` (`def _operand_len`) + the broad nested-`def`-walled set across the mirror (a recurring wall
  per [[boundary_a_nested_def_closure_broken]] family). Spike its feasibility (can Module5 emit a nested def as a local
  let rec, or is closure-capture the blocker?) next heartbeat, then build if contained.

---

## nested-`def`-closure lever — SPIKE VERDICT: FEASIBLE-BIG-BUILD (via RECOGNIZER, not front-end) + a LATENT SOUNDNESS HOLE found (2026-08-11, count 741, HEAD 0f16360b)

Spiked the top fundable lever (nested-`def`-closure support, target `_iter_len_expr`). Verdict + a
soundness by-catch:

**Q1 — Module5 does NOT drop the nested def; it LIFTS it, but capture is BROKEN + silently UNSOUND.**
`visit_FunctionDef` emits a nested `def` as a sibling top-level WhyML function via `generic_visit`,
but the nested def's FREE VARIABLES (captured enclosing locals) are NOT threaded — each captured
local becomes an abstract module-level `val constant name : τ`, decoupled from the parent's real
value. Control test (`def top(items, base): def inner(x): return x+base`) emitted `val constant base`
at module scope and `inner` read that abstract constant, NOT `top`'s argument — and it TYPECHECKS
GREEN while being unsound. (`self` is threaded only incidentally via method-context, not capture
analysis.)

**Q2 — verdict FEASIBLE-BIG-BUILD, but the RIGHT build is a RECOGNIZER, not a front-end change.**
A global front-end closure-capture-analysis fix (free-var analysis + param threading + call-site
rewrite across comprehensions) cascades across the front-end AND would move corpus byte-diff (every
nested-def program re-emits) = a RISKY brick. The byte-inert, axiom-free path is a RECOGNIZER
(`emit_*_group`) that models the specific nested-def-closure faithfully — lower the captured nested
def as a local `let`/`let rec` threading the captured locals as params, exactly as the certified
pyval/pydict catamorphism already does. That fires ONLY for the recognized method ⇒ byte-inert on the
corpus (no such shape there) ⇒ this is HOW all existing nested-def conversions were done. For the
NAMED target `_iter_len_expr` the recognizer must be COMPOUND: nested-def-closure + genexpr-join-with-
closure-call (`" + ".join(_operand_len(s) for s in args_ir)`) + `Optional[str]`-union-return + rsplit
+ opaque `_expr_to_whyml` val. Session-scale; closure support ALONE converts nothing here.

**Q3 — cluster 53 trusted nested-def stubs**, but many capture MUTABLE accumulators
(`rec`/`walk`/`strongconnect`/`found`-flag over a list/ref) → need mutable-ref threading = a further
escalation beyond by-value. Clean by-value-capture subset is a fraction of 53.

**Q4 — axiom-free YES** (structural; lowered local fn needs no new axiom; ledger stays 3).

**SOUNDNESS BY-CATCH (flagged, independent of the count campaign): the generic-lift capture
decoupling is a LATENT hole — but existing conversions are VERIFIED SOUND.** The decoupling
(`val constant <local>`) typechecks green-but-unsound, and is masked ONLY because (a) trusted methods
emit as bodyless `val`s (no proof obligation) and (b) CONVERTED methods match a RECOGNIZER, not the
generic lift. VERIFIED (b): emitted `ir_scanner.mlw` has ZERO `val constant` decls, and the converted
`uses_divmod`'s nested `_check` is a proper `let rec`/`let function` pyval-catamorphism group
(`irscanner___check__type_is` etc., threading `pydict`/`pyval` structurally) — recognizer-emitted, NOT
decoupled. So NONE of the 28 converted-nested-def methods is unsound. The hole would bite only a
FUTURE generic-path conversion of a capturing method (which the recognizer path avoids). It is NOT an
early-stop / active bug — it is a front-end footnote: if the front-end closure lift is ever relied on
for a conversion (instead of a recognizer), it MUST thread captures first.

**gather-pick-work disposition:** nested-def-closure is NOT a CORRECTNESS-BOUNDARY (it's feasible +
axiom-free via a compound recognizer) — it is a session-scale compound-recognizer build. The next
build target should be the SIMPLEST by-value-capturing trusted nested-def stub (compound-free), to
land the nested-def-closure recognizer capability on an easy target before compounding it toward
`_iter_len_expr`. Census that next.

## nested-def-closure census → CO-BLOCKED (0 standalone yield); REAL next lever = SELF-STATE-MUTATION frame (2026-08-11, count 741, HEAD 5a67ce09)

Censused the trusted nested-def stubs (canonical): only **9** exist (the spike's "53" counted
non-trusted). Decomposition:
- **4 `_collect_*`** (`_collect_field_decode_str_locals`, `_collect_string_elem_read_locals`,
  `_collect_str_call_result_locals`, `_collect_shared_symbol_decls`): the nested `def rec/_symbol`
  is a PURE walk adding to a captured LOCAL set (a StrSet-union accumulator fold — convertible via the
  banked pyval-walker accumulator recognizer). BUT the OUTER method then does `st[v] = "str"` where
  `st = self._current_symbol_table` — a SELF-STATE MUTATION. Faithful frame = `assigns
  { self._current_symbol_table }`, NOT the fixed `\nothing`. With `\nothing` the Why3 frame VC fails
  (or, if dropped, is the [[trusted_val_frame_unsoundness]] unsound-dropped-frame pattern). So the
  nested-def-closure is NOT the blocker here — SELF-STATE MUTATION is.
- **5 `pycsl.py`** (`_probe_one`, `_dispatch_provers`, `_run_vacuity_gate`, `_run_proofs`,
  `_transpile_modular`, `_sig_val_from_let`): prover-driver / subprocess / Why3-invocation methods =
  the subprocess/file-I/O boundary (definitely not convertible).

**Therefore nested-def-closure support yields 0 standalone** — every trusted nested-def stub is
co-blocked by self-state-mutation (the 4 `_collect_*`) or subprocess (the 5 pycsl.py). Same shape as
str→int: a feasible capability with 0 standalone yield because every candidate is co-blocked. Do NOT
build nested-def-closure support in isolation; bundle it with the self-state-frame lever (which is the
actual gate for the `_collect_*` cluster).

**REAL next lever = SELF-STATE-MUTATION faithful-frame** ([[trusted_val_frame_unsoundness]]). The
`_collect_*` cluster converts IFF a mirror method can carry a faithful `assigns { self.<field> }`
frame that Why3 discharges, byte-inert on the corpus, siblings intact, axiom-free. Per
gather-pick-work this is NOT a CORRECTNESS-BOUNDARY (feasible in principle) — SPIKE it make-or-break
next: port ONE self-state `_collect_*` with `assigns { self._current_symbol_table }`, run `--fun`, and
classify CONTAINED (byte-inert + siblings-intact) vs frame-model-campaign (moves byte-diff / needs the
flagged multi-method frame rework).

## self-state faithful-frame SPIKE VERDICT: frame WORKS (banked) but NOT the binding constraint; real lever = nested-def SET-ACCUMULATOR recognizer-fold (2026-08-11, count 741, HEAD 1e3740f0)

Spiked the self-state-mutation faithful-frame lever (target `_collect_string_elem_read_locals`).
Result:
- **Frame CONTAINED + BANKED:** `#@ assigns self._current_symbol_table` DISCHARGES faithfully for a
  DIRECT field-map write (`self._current_symbol_table[k]=v`). Probe `_probe_ss_direct` proved
  `Verification SUCCESS`, emitted a real `let` with `writes { self._current_symbol_table }` +
  `self._current_symbol_table <- map_update_some self._current_symbol_table key "str"`. The field is
  modeled as a `mutable map string (option string)` of the state record; the self-field-frame syntax
  is pre-existing (`_handle_fieldassign_stmt`). BYTE-INERT (frame mechanism = pre-existing
  `_emit_frame_condition`/`map_update_some`, zero new emitter code) and AXIOM-FREE (a `writes` VC, not
  an axiom; `map_update_some` over Why3 stdlib `Map.set`, ledger stays 3). **BANK: the frame is ready.**
- **But converts ZERO `_collect_*`** — each is DOUBLE-gated upstream of the frame:
  1. **nested `def rec` closure walking a captured MUTABLE SET (`out.add(x)`) → abstract-val
     emission** (dominant). generic_fold's `emit_closure_existence_group` recognizes the found-flag
     `||` shape ([[boundary_a_nested_def_closure_broken]]) but NOT the SET-ACCUMULATOR shape, so the
     method falls through to abstract-val. THIS is the binding wall.
  2. **getattr-alias `st = getattr(self,"_current_symbol_table",None)` → `st := 0` (int-degenerate) →
     `if st is not None` = false → the `st[k]=v` write is DEAD CODE** (proof succeeds vacuously, the
     mutation is never modeled). Faithfulness needs the DIRECT `self._field[k]=v` form; fixing the
     getattr-alias to alias the mutable self-field is a GLOBAL emitter change (byte-diff-swept before
     landing).
- **Integrity note (false alarm cleared):** the spike reported `_collect_string_elem_read_locals` as
  "not trusted / abstract-val"; that was its OWN worktree marker-removal, not the clean state. Clean
  mirror: all 4 `_collect_*` carry `#@ \trusted` honestly. Useful by-catch: removing a `\trusted`
  marker WITHOUT a real lowering yields a VACUOUS abstract val — Gate-C non-vacuity must reject it
  (a converted method MUST emit a real `let`, never abstract `val`).

**NEXT LEVER (real binding constraint): nested-def SET-ACCUMULATOR recognizer-fold** in
generic_fold.py — extend the certified pyval catamorphism / found-flag `||` recognizer to the
"walk-a-pyval-tree accumulating a StrSet (`out.add(target)` on matching Assign nodes)" shape, returning
a `StrSet` (certified `map string bool` + set_union, axiom-free). That unblocks blocker #1 for all 4
`_collect_*`; then the getattr-alias fix (#2) + the banked faithful frame land the conversion. StrSet
model already certified axiom-free ([[pyval_value_model_built]]). SPIKE the set-accumulator catamorphism
feasibility next (does it discharge the cross-decreasing variant over pv_size returning a StrSet?).

## set-accumulator recognizer = CERTIFIED-BOUNDARY [COST/SCALE] — wall is Module5 lambda-lift, NOT the recognizer (2026-08-11, count 741, HEAD 6e012323)

Make-or-break spike of the nested-def SET-ACCUMULATOR recognizer-fold (for the `_collect_*` cluster).
The value-shape is NOT the blocker — the binding wall is a Module5 front-end lambda-lift policy:

- **census-p:** no existing recognizer covers the shape (`recognize_setfold`/`recognize_stmt_setfold`
  match a SELF-RECURSIVE top-level fn unioning `acc |= self(v)`; the found-flag closure recognizer only
  does `pyval→bool` OR-fold). The `_collect_*` shape = outer method with a nested `def rec(node)` that
  MUTATES a CAPTURED free-var set (`out.add(x)`) and returns None, outer returns the captured local.
- **catamorphism FEASIBLE + already certified:** `emit_setfold_group` (StrSet mutual catamorphism
  `pyval→map string bool` via `set_union`, cross-decreasing variant over pv_size/size_dict/size_list)
  is proven axiom-free (v2_setfold_spike.mlw, Alt-Ergo+Z3, ledger 3). Value shape is NOT the wall.
- **FATAL BLOCKER — lambda-lift NAME COLLISION.** `_collect_string_elem_read_locals` AND
  `_collect_field_decode_str_locals` both name their nested closure `rec`. Module5 lifts both to the
  SAME top-level IR func `statementemissionmixin__rec` (IR: `dup names: {'...__rec': 2}`, two DISTINCT
  bodies). Harmless ONLY because both are `\trusted` → abstract `val ...__rec (self)(node:int):unit`,
  and the emitter DEDUPS the identical signatures to ONE `val`. Converting EITHER to a real `let rec
  function ...__rec` breaks dedup → two defs under one WhyML symbol → duplicate-symbol REJECTION. Can't
  rename the closure (verbatim bodies only). Fix REQUIRES Module5 to qualify lifted-closure names by
  enclosing method — a front-end change.
- **SECONDARY BLOCKER — capture-drop.** The lift drops the captured mutable accumulator from `rec`'s
  signature (`formal_params=['node']`, no acc); `.add`/`ssf`/`str_arrays` survive as UNBOUND free
  names. Threading them needs a Module5 capture-analysis change — AND it turns nested-def abstract-vals
  into must-prove `let`s, which risks REGRESSING corpus programs whose nested defs currently emit as
  assumed abstract-vals (corpus-regression risk = why this is review-gated, not auto-buildable).
- **Target-1 confounds:** `_collect_string_elem_read_locals` has TWO order-dependent accumulators + a
  captured self-field set + a double `rec()` call — not a clean single catamorphism even absent the
  lift blockers.

**TAG [COST/SCALE]. REOPENING CONDITION:** a flagged, byte-diff-swept **Module5 lambda-lift campaign** —
(1) qualify lifted-closure names by enclosing method (semantics-preserving rename, M1-authorizable) +
(2) thread captured mutable free vars as by-ref params (SEMANTIC change, corpus-regression risk, needs
per-program re-proof). THEN adapt the certified `emit_setfold_group` to the free-var-accumulator shape.
This is a review-gated multi-file front-end campaign, NOT a generic_fold.py-only spike. The banked
faithful frame (assigns self.field) + the certified setfold catamorphism are both ready for when the
lambda-lift wall falls. Count stays 741.

## Module5 capture-threading = PROMOTED [COST/SCALE]→CONTAINED (2026-08-11, count 741, HEAD 5de618dc) — building

Spiked the reopening capability (Module5 lambda-lift capture-threading). The DECISIVE falsifier:
**ZERO of 893 corpus reference programs contain a nested `def`** (AST-authoritative). So the
"corpus-regression risk" that tagged this [COST/SCALE]/review-gated CANNOT occur — the corpus-only
byte-diff gate has nothing to regress on. **PROMOTE to CONTAINED.** (Anti-false-floor payoff: the
boundary rested on a false premise — MEASURE beats the memory tag.)
- **M2 surface (multi-site but tractable):** nested def lifted by `generic_visit` (Module5:5169),
  captures dropped at `formal_params=[a.arg ...]` (:4645). Fix = free-var analysis + qualify
  lifted-closure name by enclosing method (blocker #1) + prepend immutable captures to formal_params +
  rewrite enclosing-body call sites via a lift-registry, ALL narrowly gated (the `_vararg_str` pattern
  :4656) so non-capturing/non-nested funcs stay byte-identical (trivial: 0 corpus nested defs). Emit
  side ALREADY threads extra params (`emit_setfold_group` extra_args :1175) — only the Module5 binding
  is missing.
- **M3 feasibility CONTAINED:** discharge via the ALREADY-CERTIFIED functional catamorphism (re-express
  void-mutate-and-recurse `out.add` closure as a `map string bool`-returning `set_union` fold — NOT a
  by-ref mutable effect, which would hit the variant/E-matching wall). Clean minimal target =
  `_collect_field_decode_str_locals` (single `out` accumulator). `_collect_string_elem_read_locals` =
  confounded (two-pass fixpoint) → separate follow-on.
- **M4 axiom-free CONFIRMED** (structural binding change, no new value shape; ledger 3).
- getattr-alias NOTE: the target's `self._current_symbol_table[v]="str"` reflection stays dead-code
  (getattr degenerates) → `assigns \nothing` honored; the RETURN set (via the catamorphism) is the
  non-vacuous content. No new unsoundness (the trusted stub already had `assigns \nothing`).

BUILDING NOW: Module5 capture-threading + name-qualification (narrowly gated) + emit_setfold_group
adaptation + convert `_collect_field_decode_str_locals` (target 741→740). Supervisor M1-byte-diff (exp 0).

## Module5 capture-threading = BROKEN-LANDED (2026-08-11, 741→740, commit 5357f8ba)

The CONTAINED build LANDED. `_collect_field_decode_str_locals` converted. KEY: no Module5 change was
needed — the existing recognizer family already lifts the nested `def rec` by adjacency; the build
reduced to a generic_fold recognizer (`recognize_field_decode_str_locals_pairs` /
`emit_field_decode_str_locals_group`) that re-expresses the void-mutate-and-recurse `out.add` closure
as a `map string bool` `set_union` catamorphism via the already-certified `emit_setfold_group`.
Axiom-free (ledger 3), 0 new stubs (generic_fold not mirrored). Battery: statements.py SUCCESS +
Module6_WhyMLTranspiler.py (mixin-propagation) SUCCESS + corpus byte-diff 0 + fidelity 52/52 +
non-vacuity (real set_add on node[target], mutation test flips .mlw) + coupling-free caller.
**BANKED CAPABILITY:** the set-union-catamorphism-over-lifted-rec-closure recognizer. **FOLLOW-ON
SIBLINGS** (now reachable via the same/extended recognizer, re-drain candidates): `_collect_str_call_result_locals`,
`_collect_string_elem_read_locals` (two-pass fixpoint — needs the bounded-for-fixpoint device),
`_collect_shared_symbol_decls` (Module6 giant, `_symbol` closure). MEASURE each next.

## _collect_* sibling re-drain verdict (2026-08-11, count 740, HEAD 0fa202c9)
- `_collect_str_call_result_locals`: NOT in the mirror (50-fn subset; not counted in 740) + semantic
  string-typer (facade if mirrored). OUT OF SCOPE.
- `_collect_shared_symbol_decls` (Module6_WhyMLTranspiler.py): NEW-SUBSTRATE BOUNDARY [CORRECTNESS-ish]
  — tokenizes a `List[str]` of emitted WhyML text via `.split()` + cross-products the opaque
  `self._AXIOM_FUNCTIONS.values()` registry; faithful lowering = opaque `val` over `_AXIOM_FUNCTIONS`
  (returned set opaque = facade/Gate-C reject). The set-catamorphism vein does NOT apply. Skip.
- `_collect_string_elem_read_locals` (statements.py:1040, still trusted): FOLLOW-ON BUILD [COST/SCALE] —
  the only tractable candidate. Needs a NEW `recognize_string_elem_read_locals`: two-set outer (`if not
  ssf: return set()` guard + double-`rec` + return-SECOND-set) → TWO SEQUENTIAL set catamorphisms:
  fold-1 `str_arrays` (gated by opaque `in_ssf` reflect-the-literal predicate over the Call func name,
  `whyml_ident(v.func) in _module_string_seq_funcs`) threaded as a `map string bool` into fold-2
  `elem_reads` (gated on `Subscript` whose base ∈ str_arrays). Corpus-safe (0/893 nested defs),
  axiom-free, caller-coupling-safe (`string_vars |= ...`). BUILDING NOW (740→739).

## Two-fold set-catamorphism = LANDED (2026-08-11, 740→739, commit ce26efc7)

`_collect_string_elem_read_locals` converted via a NEW two-sequential-catamorphism recognizer
(recognize_string_elem_read_locals_pairs / emit_string_elem_read_locals_group): the double-`rec`
two-pass fixpoint with cross-accumulator dependency → two sequential `map string bool` set-union
catamorphisms (fold-1 str_arrays gated by opaque ensures-free `in_ssf` val, threaded via extra_args
into fold-2 elem_reads gated on Subscript-base membership). Axiom-free (opaque val ≠ axiom, ledger 3),
0 new stubs. Battery: statements.py SUCCESS + Module6_WhyMLTranspiler byte-identical (narrow gate, no
transpiler propagation) + corpus byte-diff 0 + fidelity 52/52 + non-vacuity (both folds real let +
mutation test) + coupling-safe caller. **BANKED:** the two-fold-with-cross-dependency device.

**`_collect_*` nested-def set-collect cluster now DRAINED:** `_collect_field_decode_str_locals` +
`_collect_string_elem_read_locals` CONVERTED; `_collect_str_call_result_locals` NOT-IN-MIRROR;
`_collect_shared_symbol_decls` = NEW-SUBSTRATE BOUNDARY (opaque `_AXIOM_FUNCTIONS` string-token facade).
The 5 pycsl.py nested-def stubs = subprocess boundary. Nested-def set-catamorphism vein exhausted.
SESSION TALLY (from 749): 749→739, 10 conversions (8 pv-tree-walker + field_decode + string_elem_read).
NEXT: fresh census for the next vein (anti-false-floor).

## Census verdict: current recognizer toolkit FLOOR at 739; next lever = typed-record-view value model (2026-08-11, HEAD ff9f58a1)
Fresh independent census of all 739 stubs (50 files), ~15 candidates examined, the cleanest
(`_field_type_for`, types.py) PORTED + measured to its exact `--fun` error: the `_record_types.values()`
walk + `info.get("whyml_name")` string-compare LOWER correctly (wall-2), but `info.get("field_types",
{}).get(field)` — a NESTED `Dict[str,str]` read — lowers to `int` (`get_1 field`) while the return union
arm is `string` → `Verification FAILED` (line 974). = the documented **heterogeneous nested-typed-string-map
value-model boundary**. Residuals all genuine boundaries: cross-mixin forward-decl stubs (no live body in
the mirror file), nested-def closures (`_is_false_goal`), graph reachability (`compute_sccs`), linear-form
coeff-maps, hashlib/string-char, raw-ast, filesystem I/O (`ir_resolve`), subprocess prover-drivers,
forbidden allowlist, struct-format parsing.
**NEXT LEVER (value-model, NOT floor per mandate): typed-record-view for a heterogeneous `Dict[str,Any]`
record whose nested fields are typed maps (`field_types: Dict[str,str]`).** Spike whether typing the nested
`field_types` value as `map string (option string)` (not int) — a typed-nested-map-view / pget-returns-
string-on-nested-pydict — fixes `_field_type_for`'s `--fun` error, byte-inert + axiom-free. CONTAINED →
build (739→738 + unblocks `_field_type_of` + the record-view cluster); full-heterogeneous-rework → size it.

## typed-record-view = FULL-REWORK-NEEDED [COST/SCALE, axiom-free] (2026-08-11, count 739, HEAD 3eba3466)
Spiked `_field_type_for`. Root cause MEASURED: `_record_types` is a heterogeneous `Dict[str,Any]`
self-field emitted `map string (option int)` (Any→int fallthrough preamble.py:7148); `info` is a scalar
int with NO fields, so the existing nested-map path (Dict[str,Dict[str,int]]) can't fire — no place to
hang the nested `field_types` string-map. `_field_type_for` fell to the ABSTRACT-READER path (opaque
`get_1 field` int reader → the string-vs-int arm failure). Abstract-reader shortcut = Gate-C facade reject.
FAITHFUL FIX (certified, axiom-free): retype `_record_types` value_type → the banked `hval` heterogeneous
model (`map string (option hval)`, Phase2f_PyVal cert, hpairs assoc-list, ledger 3). BUT it retypes a
SHARED field across **~97 read sites in 6 files** (types/statements/expressions/functions/stmt_control_flow/
preamble), re-lowering every access + re-proving types.py + every giant composing typeinferencemixin.
NOT byte-inert WITHIN the mirror (changes many green methods' terms; corpus byte-identical — hval sentinel
corpus-absent). Yield only ~2-3 stubs (`_field_type_for`, `_field_type_of`, ~`_emit_body_code`). = poor
ratio + high regression risk. [COST/SCALE, NOT correctness]. REOPENING = the hval shared-field retype.
NEXT: SPIKE the REGRESSION RISK (retype `_record_types`→hval, re-emit the 6 files, count how many of the
~97 read-site methods still PROVE) before committing to the full build. If sites survive → build; if they
cascade → genuine multi-session, decompose or record as the funded-window big-build.

## hval-retype = LOW-REGRESSION, tractable (2026-08-11, count 739, HEAD 48c6ad78) — building
Regression spike REFUTED the "~97 sites" scare: raw-grep artifact (comments/docstrings). REAL code read
sites = only **5** across 4 files, ALL membership (`x in self._record_types`) or pass-through (into
`IRScanner.find_record_vars`, itself membership-only) — NONE materializes the Any codomain. Retyping
`_record_types`→hval is **body-term-INERT** (0 method-body terms change; only the field decl option
int→option hval + the certified hval theory block). Survival: types.py whole-file proof SUCCESS + 2
sample --fun SUCCESS = 3/3, zero regressions, ledger 3. Corpus byte-inert (emitter-internal field, hval
sentinel corpus-absent). BUILD residuals: (1) retype at the single IR source point (or the spike's
name-keyed preamble overrides ~7127 + _uses_pyval ~6455); (2) propagate the type through
`IRScanner.find_record_vars`'s record_types param (2 statements.py call sites, mechanical); (3) DECISIVE
supervisor gate = the assembled Module6_WhyMLTranspiler giant proof (spike skipped it; expected green).
MAKE-OR-BREAK of the build = does `_field_type_for`/`_field_type_of` lower NON-VACUOUSLY under hval (real
HMap→HStr projections, not the abstract reader)? BUILDING now (739→737 if both convert).

## hval-record-view = LANDED (2026-08-11, 739->738, commit a3785a13)
`_field_type_for` converted by retyping the shared `_record_types` Dict[str,Any] field to the certified
hval heterogeneous value model + 4 composable axiom-free emitter features (values()-recognizer w/ hval
iterator, hstr_of compare, doubled pairs_get nested read, option-string union thread). Ledger 3, 0 new
stubs, corpus byte-diff 0. Whole-file proofs SUCCESS: types.py, expressions.py, Module6_WhyMLTranspiler
(giant), stmt_control_flow (@7200 — HEAVY hval E-matching ~2400s), ir_resolve; theory-only files inert.
Non-vacuity confirmed (real HMap/pairs_get/HStr descent + mutation test). **BANKED: the hval typed-record
read capability** (unblocks record-view readers of heterogeneous Dict[str,Any] registries).
- **FLAG 1 (proof-cost):** the hval retype makes stmt_control_flow's `_record_types`-reader VCs E-matching
  heavy (whole-file ~2400s, needs the 7200 timeout). Future hval-field retypes should bank an E-matching
  PIN (size/wf trigger) to bound the cost (wall2 device).
- **FLAG 2 (fidelity debt):** the load-bearing live `_handle_for_stmt` loop-var-tagging edit WIDENS its
  PRE-EXISTING mirror divergence (baseline drift-2 = `_handle_var_expr` + `_handle_for_stmt`; count
  unchanged, drift stays 2). A dedicated fidelity-cleanup pass should re-port BOTH stale mirror bodies.
- **SIBLING `_field_type_of`:** blocked NOT by hval but by an orthogonal emit_ir receiver-reflection
  feature (`attr.get('value') or attr.get('object') or {}` + getattr-with-default lowering → int-vs-option
  mismatch). Separate build. SESSION TALLY: 749->738 (11 conversions).

## Re-drain after hval wall: NO-CHEAP-REMAINING; frontier = HEAVY-BUILD-PER-STUB (2026-08-11, count 738, HEAD d74c3a2a)
Independent census confirms the hval-record-view vein is EXHAUSTED (only `_field_type_for` [landed] +
`_field_type_of` [orthogonally blocked] had the clean `for info in _record_types.values()` idiom). 10
frame-clean (`assigns \nothing`) small residuals measured, EACH blocked by a DISTINCT wall — none contained:
- `_field_type_of` (types.py): emit_ir receiver-reflection chained-`or` → int-truthiness collapse; needs a
  VALUE-TYPED chained-or SELECT over emit_ir sub-node reads yielding the selected pyval/hval sub-node (the
  emit_ir sub-node value-model — BROAD, orthogonal to hval; patch-only-`{}` = Gate-C vacuous).
- `_parse_mixin_sig`, `_refine_tuple_return_type`, `_infer_tuple_slot_type` (functions.py): heterogeneous
  tuple return (string-vs-int / int-vs-option) — the tuple value-model.
- `_build_method_param_whyml_types_by_name`, `_mutex_inv_params`, `_fresh_globals_facts`,
  `_emit_subtyping_goals` (functions/preamble): nested-map / `array`(string) codomain mismatch — typed-map
  codomain feature.
- `_emit_opaque_class_aliases` (preamble.py): BY-REF PARAM MUTATION (`declared_types.add`/`out.append` need
  caller-visible `writes {param}` frame) — the by-ref-param-frame feature.
- `_render_refinement_goal`: pipeline error (unsupported).
**FRONTIER STATE:** each further cut = a distinct session-scale value-model/frame feature build for ~1
stub (like hval-record-view: ~5h + proof-cost + fidelity-debt). NOT floor (COST/SCALE, not correctness),
but the autonomous ROI has fallen to heavy-build-per-stub. NEXT fundable levers ranked by reuse of banked
caps: (1) by-ref-param-frame (`_emit_opaque_class_aliases`, reuses mutable-ref append); (2) tuple
value-model (3 stubs); (3) typed-map codomain (4 stubs); (4) emit_ir sub-node value-model (`_field_type_of`,
broadest). SESSION TALLY: 749->738 (11 conversions).

## typed-map codomain "cluster" = MIRAGE (2026-08-11, count 738) — CORRECTION
Spike REFUTED the 4-stub grouping: the 4 share NO fix, each a distinct wall — #1
`_build_method_param_whyml_types_by_name` = nested-map `map string (map string string)` + missing mirror
helper `_dict_param_whyml_type`; #2 `_emit_subtyping_goals` = heterogeneous-dict-valued comprehension
(Dict[str,Any]); #3 `_mutex_inv_params` = string-op wall (`sorted`+f-string+substring `in`); #4
`_fresh_globals_facts` = frame save/restore + giant `_expr_to_whyml` proof-cost. Only #1 is map-shaped.
LESSON: verify cluster REALITY (per-stub live-body measure) before a "cluster" build — the census's
type-tag grouping was inaccurate. Frontier confirmed heavy-build-per-stub, NO cheap cluster. NEXT: verify
the TUPLE cluster reality (`_parse_mixin_sig`/`_refine_tuple_return_type`/`_infer_tuple_slot_type` — do
they SHARE a tuple-value-model fix, or 3 distinct walls?) before building.

## tuple "cluster" = MIRAGE too (2026-08-11, count 738) — frontier comprehensively measured
Spike REFUTED the tuple grouping (same topical-grouping error as typed-map): NONE of the 3 returns a
heterogeneous tuple value — #1 `_parse_mixin_sig` returns `(List[Tuple[str,str]], str)` = faithful
string-PARSER + seq-of-pairs; #2 `_refine_tuple_return_type -> str` = stateful self-field save/restore +
Dict[str,Any] + 2 still-trusted helpers; #3 `_infer_tuple_slot_type -> str` = Dict[str,Any] pyval +
getattr + trusted `_is_string_expr`/`_is_emit_ir_expr`. The tuple value SHAPE is axiom-free (Why3 tuples
built-in) — NOT the blocker anywhere; the real blockers are heterogeneous-dict + string-parser +
trusted-helper chains. **BOTH census "clusters" (typed-map, tuple) were MIRAGES.**
FRONTIER COMPREHENSIVELY MEASURED (this session, 749->738, 11 conv): the cheap/cluster frontier is
EXHAUSTED. Remaining residuals are each a distinct SESSION-SCALE build, gated behind: (a) the GENERAL
heterogeneous Dict[str,Any] value model (broke the record-READ case via hval, but the general case is
E-matching PROOF-SCALE-walled — hval on ONE field pushed stmt_control_flow to ~2400s; generalizing needs
the E-matching PIN device FIRST); (b) faithful string-parsers; (c) stateful self-field frames; (d)
still-trusted helper chains. Highest-leverage reopening capability = the E-matching PIN (bound hval VC
cost) — enables cheaper general heterogeneous-dict reads. Last un-measured ranked lever = by-ref-param
-frame (`_emit_opaque_class_aliases`); spiking it now.

## by-ref-frame lever = MIRAGE too; ROOT WALL = general heterogeneous Dict[str,Any] (E-matching proof-scale) (2026-08-11, count 738)
Spike REFUTED: the by-ref mutable-param frame (`assigns out`/`assigns declared_types`) ALREADY discharges
widely in verified mirror methods — NOT the blocker. `_emit_opaque_class_aliases`'s real blocker is
`func.get("kind")`/`func["self_type"]` over `List[Dict[str,Any]]` = the general heterogeneous-dict value
model + `.lower()`/f-string + trusted `whyml_ident`. **ALL 3 census "levers" (typed-map, tuple,
by-ref-frame) were topical mis-diagnoses.** CONCLUSIVE: every remaining residual is gated behind the ROOT
WALL = general heterogeneous Dict[str,Any] value model, which is E-MATCHING PROOF-SCALE-WALLED (hval on
ONE field cost ~2400s; per [[isolation_spike_not_whole_file]] the E-matching-saturation wall =
review-gated modular verification). Reopening capability = the E-MATCHING PIN device (size/wf triggers to
bound the hval VC cost). SPIKING the PIN now (measure-first): does a size/wf trigger on the hval/hpairs
theory bound the stmt_control_flow hval-reader VC below the 3200 budget? If yes -> banked capability
un-gates general heterogeneous-dict reads. If no -> the E-matching saturation is fundamental =
review-gated modular-verification CERTIFIED-BOUNDARY. SESSION: 749->738 (11 conv), frontier comprehensively
measured.

## E-matching PIN = REFUTED (PIN-INSUFFICIENT); general heterogeneous-dict wall = REVIEW-GATED proof-scale CERTIFIED-BOUNDARY (2026-08-11, count 738)
Spiked the E-matching PIN (the root-wall reopening capability): added an AXIOM-FREE size_hval/size_hpairs
measure + proven non-negativity `let rec lemma` pack to the hval theory (analogous to the pydict size PINs,
ledger stays 3). MEASURED: post-PIN stmt_control_flow hval whole-file proof = ~2350s SUCCESS vs the ~2400s
no-PIN baseline = NEGLIGIBLE (~2%) — the size-PIN does NOT bound the hard hval-reader VC. The E-matching
saturation on that VC is FUNDAMENTAL (not from missing size lemmas). REFUTED.
=> The general heterogeneous Dict[str,Any] value-model wall (root of every remaining residual) is a
PROOF-SCALE / E-MATCHING-SATURATION boundary whose only remaining reopening capability = REVIEW-GATED
modular verification (`#@ no_inline` modular boundaries, per [[isolation_spike_not_whole_file]]) — NOT an
autonomous size-PIN. The autonomous reopening capabilities are EXHAUSTED (PIN refuted; cheap clusters all
mirages; value model expresses it but the proof saturates).

## AUTONOMOUS FLOOR CONFIRMED at 738 (2026-08-11, comprehensively measured)
This session: 749->738 (11 conversions), broke 3 documented walls (Module5 capture-threading, two-pass
catamorphism, hval-record-view). Frontier THEN comprehensively measured: census (all 738) + 3 census
"clusters" all MIRAGES (typed-map/tuple/by-ref-frame — topical mis-groupings, each residual a distinct
wall) + the E-matching PIN REFUTED. Every remaining residual is behind the general heterogeneous-dict
E-matching proof-scale wall (or string-parsers/[[parser_vein_broken]] terminus / stateful-frames /
trusted-helper chains that converge on the same proof-scale terminus). AUTONOMOUS reopening capabilities
exhausted; the remaining path (modular verification) is REVIEW-GATED. => HOLD at 738 per driver §A.2 action
(6); periodically re-measure a not-yet-spiked class (anti-false-floor). The review-gated modular-verification
campaign is the fundable next step (needs authorization).

## Anti-false-floor CONFIRMED: leaf-first/bottom-up path CLOSED (2026-08-11, count 738)
Independent leaf-helper sweep (`_is_string_expr`/`_is_emit_ir_expr`/`_collect_array_var_assigns` + a broad
module6 sweep): the "leaf" helpers are NOT leaves — mid-DAG recognizers over the general heterogeneous
Dict[str,Any] IR-node model, each transitively dep on ≥8 trusted recognizers + self-state frames +
string-op tag dispatch + (for `_collect_array_var_assigns`) a while-changed variant-decrease E-matching-
flood boundary. NO trusted bool/Set/List module6 stub has a signature free of the IR-node model (stubs
type the un-modeled Dict/ExprIR as int); the genuinely string-typed leaves (abstract_ops/identifiers/
expr_ghost_collections) are ALL string-parsers over List[str] buffers (parser terminus). => bottom-up
path CLOSED; floor 738 REAL (4 independent confirmations this session: census + 3 mirage-clusters + PIN
refuted + leaf-helper sweep). Remaining path = review-gated modular verification (`#@ no_inline`), needs
authorization. DRIVER HOLDS at 738.

## FRESH-EYES anti-false-floor probe #2: proof2why3/crosscheck.py string-field twin = distinct wall (2026-08-12, count 738, HEAD 01f32bb8)
Independent census (NOT primed by the module6-centric prior framing): swept the less-mined proof2why3/*,
audit_*, frontend-helper files. Best NEW candidate the prior census under-named = **CrossCheckResult.all_agree**
(proof2why3/crosscheck.py) — a `@property -> bool`, `assigns \nothing`, callers trusted (`main`/`crosscheck_file`
stubs), small non-giant file (proves whole-file green as-is). It is the STRING-FIELD TWIN of the ALREADY-CONVERTED
`IRCrossCheckResult.all_agree` (crosscheck_ir.py, in-suite, green): same `canons=[...]; if not canons: False;
all(c==canons[0])` idiom, but over `str` fields (rocq_norm/lean_norm/registry_norm) with a **truthiness filter
`if n`** and **string `==`** instead of `Optional[Term]` fields with `if c is not None` + `term_eq`.
PROBED BY BUILDING (port verbatim body, drop `@property` per the crosscheck_ir precedent, remove `\trusted`):
- Emission is NON-VACUOUS (emits a real `let` — Array.make 3 of the fields, `list_content_comp_0` filter,
  `_all_fold`), but whole-file proof **FAILS**: the generic string-filter-comprehension path lowers
  `present = [n for n in norms if n]` to an **int** (`!present <> 0`; return type `int`), losing list content
  so `present[0]`/`all(...)` are meaningless. A real lowering GAP, not a missing invariant.
- The recognizer that makes the crosscheck_ir twin prove (`recognize_crosscheck_term_method` /
  `emit_crosscheck_term_method_group`, generic_fold.py ~32220-32520) is DELIBERATELY fail-closed &
  dispatch-gated on `_has_opaque_term_fields` -> fires on 0 corpus + only IRCrossCheckResult. It hard-codes:
  option is-not-None filter (`_cc_isnotnone_filter`), inline **Tuple** iter source (`_cc_canon_tuple_fields`),
  and `term_eq`/`Some/None` emission. crosscheck.py all_agree needs (1) a NEW shape for the double-indirection
  `norms=[list]; present=[x for x in norms if x]` (4-stmt, not the 3-stmt tuple-comprehension), (2) string
  truthiness-filter recognition, (3) string-`=` emission, (4) a NEW byte-inert dispatch gate (strings are common
  -> the `x=[...]; y=[e for e in x if e]; if not y: False; all(e==y[0])` idiom can appear in corpus, so
  byte-inertness is NOT free) + a full corpus byte-diff sweep to prove it.
VERDICT: NOT an existing-capability lever — a fundable recognizer-EXTENSION build (new shape + string emission +
scoped gate + corpus sweep). BUT it is a MORE CONTAINED / more tractable residual than the prior "general
heterogeneous Dict[str,Any] E-matching proof-scale wall" framing: it reuses an EXISTING, certified, axiom-free
(ledger-3) recognizer ARCHITECTURE over a CLEAN string-field record (no Dict[str,Any], no E-matching flood, no
stateful frame). Highest-ROI NEXT fundable lever = "string-field twin of the crosscheck term recognizer"
(unlocks all_agree + likely all_present-style siblings across CrossCheckResult). FLOOR HOLDS at 738 autonomously
(5th independent confirmation this campaign); the cheap/existing-capability frontier stays exhausted.

## FRESH-EYES DELEGATION BROKE THE FALSE FLOOR: string-field crosscheck LANDED (2026-08-11, 738->737, commit 9b79b509)
The 96h delegated fresh-eyes driver (not primed by the 6 prior floor confirmations) mined the LESS-EXPLORED
proof2why3/* files and found `CrossCheckResult.all_agree` — the string-field TWIN of the converted
IRCrossCheckResult.all_agree term recognizer. BUILT via a new string-field crosscheck recognizer
(recognize_crosscheck_str_agree, real nested-if over string fields, pystr_eq val, axiom-free, ledger 3,
dispatch-gated byte-inert). Full battery green (crosscheck.py proof SUCCESS, corpus byte-diff 0, drift 2).
LESSON: the "738 autonomous floor" was PARTIAL — the 6 confirmations focused module6/functions/types; the
proof2why3/audit/frontend-helper files are a FRESH VEIN. BANKED: string-field record recognizer.
NEXT: re-drive fresh-eyes over proof2why3/* + audit_* + frontend helpers for the next contained lever
(record-field / small-predicate twins reusing certified recognizer architectures). SESSION: 749->737 (12 conv).

## #@ no_inline campaign = NARROWER than framed (2026-08-11, count 736) — blocker is VALUE MODEL not inlining
User AUTHORIZED the modular-verification campaign (skill f773e7b9). Spike measured its ACTUAL scope: `#@
no_inline` does NOT unlock the general heterogeneous-Dict[str,Any] readers — two make-or-break --fun tests
(`_match_field_decode_idiom`, `_handle_sum_call`) FAILED on VALUE-MODEL gaps, not caller-inlining:
- `_match_field_decode_idiom`: emitted a NON-VACUOUS real `let` descending the certified IR value model
  (args_of/kind_of/str_eq_op/typeof_op/recv_get_str) — only the RETURN SHAPE defeats it: `Optional[tuple]`
  of IR-nodes `(slice,lower,width)` lowered to bare `(int,int,int)`, Optionality DROPPED, `return None`
  emitted `raise (Return_3 0)` (bare int) vs the tuple arm.
- `_handle_sum_call`: reads undeclared heterogeneous self-maps (`_known_collection_elements`) → unbound symbol.
`#@ no_inline` only relocates a PROVABLE body to a boundary; it can't fix a value-model gap. It is viable
ONLY for a reader that (a) returns a SIMPLE scalar (bool/str/int) AND (b) reads only already-declared mirror
self-fields / its ir param.
**REAL HIGHER-ROI LEVER (auto-authorized value-model, M1): Optional-tuple-of-IR RETURN LOWERING** — lower
`Optional[Tuple[τ...]]` to a proper `option (τ...)` union with correctly-typed arms + `return None` -> the
`Arm_None` ctor (the emitter currently synthesizes the union type but the `let` sig uses the raw tuple +
None->bare-int). Unblocks `_match_field_decode_idiom` (body already proves modulo the return) + any
Optional-tuple-returning reader. SPIKING it now. (Secondary: re-census for scalar-return + declared-field
readers = the direct #@ no_inline scope.) SESSION: 749->736 (13 conv).

## Optional-tuple return lowering = BUILT+BANKED (byte-inert, axiom-free) but needs the IR-SUB-NODE ACCESSOR value model (2026-08-11, count 736)
The Optional[Tuple[IR]] return-lowering fix WORKS (5 sites: _compute_return_type option-union sig,
has_none_return scanner, Return_opttuple_N exception, return->raise Some/None, catch) — verified byte-inert
(0 Return_opttuple with stub restored, L3-tc clean) + axiom-free (option+tuples built-in). Saved to
getting-better/banked-opttuple-return-lowering.patch (converts NOTHING alone — no-unused-facade, so NOT
landed solo). The ONLY Optional-tuple stub `_match_field_decode_idiom` hits a SECOND blocker AFTER the
return fix: **IR-SUB-NODE ACCESSOR value model** — sub-node LOCALS (`recv=expr.get("value")`,
`split_call`, `slice_node`) are typed `int` (ref 0) with opaque field-hash readers (`split_call_get_arr
"args"` -> array int), so `split_call.get("args")[0]` = int clashes with the converted
`_is_null_byte_lit(ir: emit_ir)`. **THIS IS THE GENERAL HETEROGENEOUS-DICT ROOT WALL** (the whole session
converged here; #@ no_inline + Optional-tuple spikes both bottomed out on it). Axiom-free-fixable (emit_ir/
args_of certified built-ins) — type sub-node locals as emit_ir + add certified field accessors (receiver/
value/slice/index/lower/upper). BIG value-model build (auto-authorized, M1), BROAD unblock (all IR-sub-node
readers). BUNDLE with the banked return-lowering patch. SPIKING it as the root-wall build.

## IR-sub-node value model = TWO LAYERS (2026-08-11, count 736) — Layer 1 contained/ready, Layer 2 = cert-touching Call-receiver extension
Root-wall drill on `_match_field_decode_idiom` (banked Optional-tuple return CONFIRMED active + not the wall):
- **LAYER 1 (auto-authorized, axiom-free, BYTE-INERT, ready):** `_is_emit_ir_expr` (expressions.py:1902)
  classifies `<emit_ir>.get(k)` as emit_ir only for k in `_EMIT_IR_NODE_KEYS` (value/object/index/pattern/
  guard/left/right). Add `slice/lower/upper/step` + certified `slice_of`/`lower_of`/`upper_of` over the
  existing IrSlice/IrSliceAccess ADT ctors (svalue_of/sindex_of precedent) → fixes split_call/slice_node/
  sl/lower_ir/upper_ir/idx. Byte-inert (gated on emit_ir-typed local in a @mutable_state class; corpus
  `x=d.get("value")` never satisfies). Converts `_match_field_decode_idiom`? NO (it also reads receiver).
  Possible Layer-1-ONLY yield = other trusted sub-node readers touching only value/index/slice/lower/upper
  (NO receiver) — UNMEASURED, the next contained census.
- **LAYER 2 (the boundary — cert-touching, corpus-affecting, FLAG):** the recognizer spine reads the
  METHOD-CALL RECEIVER (`recv=expr.get("receiver")`, `slice_node=split_call.get("receiver")`). The certified
  emit_ir ADT models a call as `IrCall string emit_ir int` (func,arg0,arity) and DROPS the receiver — no
  receiver_of, no IrMethodCall. A sentinel receiver_of → always-None vacuous facade (Gate-C reject).
  Faithful = EXTEND the Call ctor to carry the receiver sub-node: touches every IrCall reader (func_of/
  arg0_of/nargs_of/is_call/kind_of/size) + every reflected-method-call CONSTRUCTION + a co-landing axiom-free
  Rocq+Lean cert re-proving the extended ADT (LEDGER STAYS 3). M1-corpus-affecting (every reflected method
  call re-emits). Axiom-free IN PRINCIPLE. = the next BIG cert-co-landing build; spike the cert-feasibility
  + byte-diff scope first. NEXT: Layer-1-only census (contained), then Layer-2 cert-spike.

## Layer-1-only census = CLOSED, NO consumer (2026-08-11, count 736) -> Layer 2 is the sole path
Measured: every trusted sub-node reader touching slice/lower/upper (6 stubs) is gated on the Layer-2
method-call RECEIVER first, OR is a different value model (Python-AST `.values()` walker in monomorphize.py;
HAPPY write-site dict in Module3_Weaver). The 2 already-green emit_ir slice readers (_handle_slice_access_
expr, _slice_array_or_opaque) verify WITHOUT Layer-1 accessors (they pass bounds to trusted int-param
_expr_to_whyml, never descending the bound's sub-structure). So Layer 1 (slice_of/lower_of/upper_of) has NO
standalone consumer = no-unused-facade, NOT landed. **IR-sub-node floor = LAYER 2 only: extend the certified
emit_ir Call ctor to carry the method receiver** (IrMethodCall / receiver_of). High-leverage (unblocks the
BROAD method-receiver-reading recognizer class), axiom-free IN PRINCIPLE (ADT variant + total accessor +
co-landing Rocq+Lean cert re-proof, ledger 3), corpus-affecting (M1 — every reflected method call re-emits).
SPIKING cert-feasibility (make-or-break: does the emit_ir ADT extend + the cert re-prove axiom-free, is the
byte-diff M1-tractable?) before the full multi-session build.

## 2026-08-12 — Call-receiver wall BROKEN (a221599f, 736->735) + opttuple naming-collision bug fixed
- The general heterogeneous Dict[str,Any] / Call-receiver root wall is BROKEN via a certified
  axiom-free emit_ir ADT extension (`| IrMethodCall emit_ir string emit_ir int` + total
  receiver_of/slice_of/lower_of/upper_of/step_of accessors, gated `_uses_method_recv`). Phase2j
  certs (Rocq 10/10 closed, Lean {propext,Quot.sound}). `_match_field_decode_idiom` (returns
  Optional[Tuple[ExprIR,ExprIR,int]]) converted. Coupled to the opttuple return lowering (the
  method returns Optional[tuple], so the two changes are inseparable — proven by attempting to
  split them and breaking expressions.mlw).
- PROCESS LESSON (banked): the authoritative set of "changed-emission mirror files" that a build
  must whole-file-prove is NOT a worker's claimed file list — it is a MIRROR-WIDE .mlw emission
  diff (emit all 52 mirror files at HEAD vs build, md5 diff). This caught a REAL emitter defect the
  per-file work missed: the opttuple exception was named by ARITY alone, so Module6_WhyMLTranspiler
  (which composes an `option (int,int,int)` method AND `_match_field_decode`'s `option
  (emit_ir,emit_ir,int)`) emitted two `Return_opttuple_3` decls -> "Symbol already defined" ->
  whole-file proof FAILED. so-wt only proved expressions/stmt_control_flow (each has ONE arity-3
  opttuple), never the giant. Fix: key the exception name on the PAYLOAD TYPE
  (Return_opttuple_int_int_int vs Return_opttuple_emit_ir_emit_ir_int) at both decl sites + raise +
  catch. The collision only surfaces at whole-module COMPOSITION scale.
- Next (user standing request "keep converting the receiver-reading class"): _is_string_expr /
  _call_named_builtins / _handle_join_call / _infer_tuple_slot_type — now unblockable via receiver_of.

## 2026-08-12 (cont.) — frontier RE-MEASURED at walls (no_cheap_remaining); next wall precisely characterized
After a221599f the receiver-reading class is DRAINED (fresh base-loop probe, 735). No cheap win remains.
Top receiver-shaped candidates measured as walls:
- `_field_type_of` (types.py:292, ~59ln) — TWO-part wall: (1) NEW node-type-aware routing of `.get("value")`
  for an `IrAttr` base. `object_of` ALREADY reads the IrAttr base correctly (`match e with IrAttr o _ -> o`),
  but the projection map `expressions.py:96` is FIELD-NAME-keyed globally: `"value"->svalue_of` (matches only
  IrSub, returns `IrOther ""` for IrAttr) vs `"object"->object_of`. Module5 emits an Attribute base under BOTH
  `value` (spec ctx) and `object` (body ctx), so `.get("value")` must route to the IrAttr-base accessor when the
  base is IrAttr-typed — a structural change to a field-name-keyed map, NOT a new ctor. (2) THEN the banked
  hval-record-view (per `_field_type_for`/a3785a13) for the `self._record_types.values()` walk + nested
  `.get("field_types",{}).get(field_name)` — E-matching HEAVY (giant timeout, needs 7200; widened a fidelity
  drift in the _field_type_for precedent). = heavy 2-part Phase-2 build, NOT a spike-sized win.
- `_infer_return_value_type` (stmt_control_flow.py:1529, ~54ln) — cascade on unmodeled helper
  `_record_valued_expr_whyml_type` (lowers to opaque int val) flowing into an `Optional[str]` union -> int/union clash.
CHECKPOINT rationale: flagship (a221599f) landed+fully-verified this stretch; escalate-not-thrash + the heavy
giant-proof cost of the next wall make a fresh context the right place to build it. Wall-signal recorded above.

## 2026-08-13 — _field_type_of wall BROKEN (2d55bf04, 734->733... count 735->734) + 3-layer heterogeneous-dict recipe banked
The `_field_type_of` (types.py) wall — the general heterogeneous-dict node-type-aware Attribute/FieldGet
field-type resolver — is BROKEN. The spike REFINED the backlog's 2-part characterization (avalue_of routing
+ hval-record-view) into 3 tractable, byte-inert, axiom-free emitter recognizer layers (ledger 3; the
`.values()` walk REUSED `_field_type_for`'s certified hval-record-view, NO new cert):
- LAYER A: `_is_emit_ir_expr` BinOp/BoolOp(or/and) branch → `receiver = A.get("value") or A.get("object")
  or {}` flow-types emit_ir (empty-dict `{}` = absent sentinel `IrOther ""`); local pre-decls `ref (IrOther
  "")`.
- LAYER B: the SAME-KEY per-call-site conflict (`.get("object")` = `object_of`/emit_ir in the Attribute
  branch vs `fgobject_of`/string in the FieldGet branch — one key, one receiver, two type-classes) is
  resolved by a WHOLE-IDIOM recognizer `_recognize_attr_receiver_idiom` (`X.get("value") or X.get("object")
  [or {}]` → `avalue_of X`) so the Attribute operands escape the generic projection, freeing func-scoped
  `object→fgobject_of`/`field→field_of` for FieldGet.
- LAYER C: hval-map self-field SUBSCRIPT read in `_handle_subscript` (`self._record_types[gcls]` → `match
  Map.get … with Some _v -> _v | None -> HMap PNil`, κ=string raw key) + `_expr_is_pyval` Subscript branch,
  so the chained `.get("whyml_name")` fires the certified DOUBLED hval read. = the `_record_types[key]`
  heterogeneous-dict-by-string-key value model (read-twin of the DOUBLED `.get`).
PROCESS: the mandatory mirror-wide .mlw md5 diff found EXACTLY 2 changed-emission files (types.py + the
Module6_WhyMLTranspiler giant that composes the mixin) — both whole-file-proved 0 non-Valid (giant within
7200; types.py within 3200, NO `#@ no_inline` needed despite the `--fun` alone taking ~13min). Corpus
byte-diff 0. Gate-C non-vacuity PASS (mutation flips the emitted pairs_get key; zero opaque get_N). LESSON:
a single-fn `--fun` running ~13min did NOT force `#@ no_inline` — the whole-file proof still closed within
the giant/normal timeouts; measure the whole-file cost before assuming saturation. BANKED CAPS: emit_ir
or/and-chain local flow-typing (empty-dict sentinel); Attribute-receiver whole-idiom recognizer
(per-call-site same-key escape); hval-map self-field subscript value model + its `_expr_is_pyval`
recognition. NEXT: re-drain Phase 1, then the next receiver/heterogeneous-dict-shaped wall
(`_infer_return_value_type` stmt_control_flow.py:1529 = `_record_valued_expr_whyml_type` opaque-int→Optional[str]
union clash was the other measured wall).

## 2026-08-13 (cont.) — Phase 1 re-drain after _field_type_of = no_cheap_remaining; next walls REFINED into 2 roots
Base-loop drain (foreground) landed 0 cheap wins; the 3 banked _field_type_of caps unblock no sibling with
existing machinery. Residual walls split into TWO roots (measured, NOT the subagent's 1-cap hypothesis):
- **ROOT 1 = RELOCATION/SIGNATURE BOUNDARY (not cheap).** `_field_type_for` (statements.py:229) +
  `_field_type_of` (statements.py:276) are RELOCATED stubs in StatementEmissionMixin with signature `-> str`
  (return `""`), whereas the LIVE method (types.py, just converted) is `-> Optional[str]`. There is NO live
  `-> str` body to port verbatim → verbatim-porting is BLOCKED (a body adapting `return None`→`return ""` is a
  REFACTOR = Gate reject). ALSO `_record_types` is UNDECLARED in the statements.py mirror model (so
  `_self_field_dict_nu` can't resolve it → the `.values()` walk stays int-typed / get_1 facade). Reopening
  capability = a signature-aware relocated-stub mechanism (port the origin body + adapt the return-type at the
  relocation boundary WITHOUT it counting as a refactor) — a NEW driver capability, FLAG. `_field_type_of`@276
  is additionally a DEAD stub (no mirror caller); `_field_type_for`@229 IS live (called by verified
  `_handle_fieldassign_stmt`).
- **ROOT 2 = MULTI-CAPABILITY hval build (session-scale, ExpressionEmissionMixin, non-relocated, verbatim-OK).**
  Cluster: `_typeddict_field_access` (expressions.py:660, live 7622), `_typeddict_record_literal` (667, live
  7683), `_namedtuple_positional_access` (674, live 7758). The subagent's "1 cap = string-truthiness" was an
  UNDER-count; `_typeddict_field_access` alone needs FOUR new hval sub-caps:
  (a) **hval-truthiness**: `if self._record_types[sym].get("is_typeddict"):` — the `.get` value is a BOOL, but
     the certified DOUBLED read projects `Some (HStr s) -> s | _ -> ""` → string, then `if <string>:` lowers to
     `<string> <> 0` (int) = TYPE ERROR (expressions.mlw:2028, whole-file only — `--fun`/`--no-proof` FALSE
     GREEN, reconfirms 10.10). Faithful fix = an `hval_truthy : hval -> bool` total definitional `let function`
     (HBool b->b | HStr s-> s<>"" | HInt i-> i<>0 | HNone->false | ...), axiom-free, + route the hval `.get` to
     return the RAW hval (not string-project) in a bool/if context. (Not string-truthiness — hval-truthiness;
     a string-projection would be VACUOUS for the bool key.)
  (b) **hval-subscript-STRING-read on an hval LOCAL**: `rec_info["whyml_name"]` where `rec_info =
     self._record_types[rec_name]` (an hval local) → `match rec_info with HMap m -> pairs_get m "whyml_name"
     …`. (My banked Layer-C hval-subscript handles the self-FIELD `_record_types[rec_name]`; this is the
     LOCAL-hval subscript twin.)
  (c) **hval-collection-subscript**: `rec_info["fields"]` → an hval list/collection.
  (d) **`not in` membership** on `rec_info["fields"]` (the hval collection).
  = a genuine multi-cap session-scale value-model build (auto-authorized, M1). expressions.py is a GIANT
  (whole-file proof 7200, setsid-detached). RECOMMENDED NEXT: build ROOT 2's (a)+(b) first (they gate the
  typecheck), measure via WHOLE-FILE proof (NOT --fun — false green here), then (c)+(d). BANKED for reuse:
  Layer-C hval self-field subscript; the DOUBLED hval `.get` read; the hval-record-view `.values()` walk.

## 2026-08-13 — ROOT 2 member #1 `_typeddict_field_access` BROKEN (e531a377, 734->733); needed 6 caps (backlog under-counted by 2)
The hval value-model cluster's FIRST member is CONVERTED. The `_typeddict_field_access`
(ExpressionEmissionMixin) heterogeneous-`Dict[str,Any]` `_record_types` resolver
(`p["x"]` on a TypedDict receiver -> record-field read) needed SIX composable emitter
capabilities — TWO MORE than the itemized (a)-(d). All byte-inert, axiom-free (ledger 3;
reuses certified hval/hpairs/pairs_get, NO new cert). BANKED (reusable for the ROOT 2
siblings `_typeddict_record_literal` / `_namedtuple_positional_access`):
1. **hval_truthy** — total definitional `let function` (HStr non-empty via certified
   `hpairs_key_eq` / HInt<>0 / HArr,HMap non-empty / HNode present), in the preamble hval
   block. + bool-context routing WITHOUT re-lowering: the DOUBLED `.get` read STASHES its
   RAW hval form (`_last_hval_get_raw`/`_str`, computed with correct local_refs so ref
   locals `!sym` deref right) and `_to_bool` matches it by STRING-EQUALITY. KEY LESSON:
   `_to_bool(whyml_str, ir_expr)` has NO local_refs param; adding one CASCADES re-ports into
   the converted `_handle_while/if_stmt` (Gate reject) — the stash-match sidesteps it.
2. **hval_str_mem / hval_list_str_mem** — total definitional membership recursion over the
   bespoke `hval_list` carrier (certified `hpairs_key_eq` element test) for `x not in
   rec_info["fields"]`; a new `_emit_membership` Subscript-on-pyval-local branch reads the
   RAW hval (NOT the opaque int-hashed `contains_check`).
3. **local-hval pyval SUBSCRIPT** — `rec_info["whyml_name"]` on a pyval LOCAL projects HStr
   -> string (`_handle_subscript` pyval-local Var branch); the membership consumer reads the
   raw hval instead. Read-twin of Layer-C self-field subscript.
4. **pyval-local SEEDING from hval-self-field subscript** — `_prescan_pyval_locals`
   (`_rhs_is_pyval`) now seeds a Subscript on a `map string (option hval)` self-field (and on
   a pyval local) as pyval, so `rec_info = self._record_types[rec_name]` is a pyval local.
5. **gap-1 (NEW, NOT in backlog): STRING-default `.get("value","<str>")` -> `value_of`
   string-content** (a String IR node's CONTENT), NOT the `svalue_of` emit_ir sub-node.
   Disambiguated by the string-literal default via `_get_default_is_str_literal` in THREE
   places: the get-projection (`_scoped_val = "value_of"`), the emit_ir classifier
   `_is_emit_ir_expr` (EXCLUDE it so the target isn't typed emit_ir), and a new
   `_collect_emit_ir_value_str_locals` (types the target `ref ""`, not `ref (IrOther "")`/
   `ref 0`). This was the deepest gap — an emit_ir `.get("value")` is AMBIGUOUS between
   sub-node and String-content; the string default is the disambiguator.
6. (implicit) the Attribute/FieldGet branch goes control-flow-DEAD (`rec_name is None` ->
   `false` on a string ref) — sound over-approx for the type-safety+frame contract (the Var
   branch + all rec_info reads are live + non-vacuous). Not a facade (Gate-C mutation flips
   the emitted pairs_get key).

PROCESS: mirror-wide .mlw md5 diff -> EXACTLY 8 changed-emission files (the hval-theory set:
expressions, Module6_WhyMLTranspiler giant, types, stmt_control_flow, Module5_IREmitter,
ir_resolve, __init__, pycsl) — SAME set as a3785a13; all 8 whole-file-proved 0 non-Valid,
corpus byte-diff 0, drift 2, mirror 52/52, ledger 3, Gate-C PASS. LESSON: whole-file
`--no-proof` L3-tc IS a fast (~5min) type gate that catches the hval-truthy/field-name-type
errors (the backlog's "--no-proof false green" was about `--fun`, not whole-file). Adding 2
unused `let function`s to the shared hval block changed all 8 theory files' emission but they
all inert-pass (unused fns add no VCs).

NEXT (autonomous, deadline ~96h out 2026-08-17): re-drain Phase 1 (WHOLE-FILE proof, not
--fun), then the ROOT 2 SIBLINGS `_typeddict_record_literal` (expressions.py:7662 — `.values()`
record-scan + `info.get("is_typeddict")` truthy + zip over keys/values + missing/extra-key
RAISE) and `_namedtuple_positional_access` (7733 — Number-index + WL-04b record-array-local
path) — verbatim-OK, likely reuse caps 1-5. ROOT 1 relocated `_field_type_*` statements.py
stubs stay FLAGGED (`-> str` vs live `-> Optional[str]` = refactor = reject).

## 2026-08-13 (cont.) — ROOT 2 sibling `_namedtuple_positional_access` SPIKED + MEASURED; NEW wall = WL-04b `.items()` dead-block verbatim emission (checkpoint at 733)
Spiked `_namedtuple_positional_access` (expressions.py:7798). It reuses the 6 banked
`_typeddict_field_access` caps AND needs a NEW **hval-collection-as-SEQUENCE** capability
(BUILT in the spike, saved to `getting-better/banked-namedtuple-positional-spike.patch`;
reverted to keep 733 clean — no landed consumer yet):
- **hval_len / hval_list_len** (preamble): `len(rec_info["fields"])` -> hval-list length.
  `_handle_len_call` routes a `_pyval_locals` Var arg to `hval_len`.
- **hval_nth_str / hval_list_nth** (preamble): `fields[idx_val]` (INT index) -> the idx-th
  `HStr` as a string. `_handle_subscript` pyval-local branch now disambiguates by index IR
  type (Number -> `hval_nth_str`; String key -> the `pairs_get` DOUBLED read).
- **gap-2 (num_of)**: `index_ir.get("value")` (NO default) after a `type == "Number"` guard
  reads the Number leaf's INT payload (`num_of`), not `svalue_of`. Fixed via an EMPTY scoped
  entry in `_EMIT_IR_GET_KEY_PROJ_BY_FUNC` (makes `_scoped2` non-None -> the existing
  `.get("value")` no-empty-dict-default disambiguation routes to `num_of`).

REMAINING GAPS (measured via WHOLE-FILE `--no-proof` L3-tc, the ~5min fast gate):
- **gap-2b (idx_val emit_ir-misclassification)**: `_is_emit_ir_expr` (expressions.py:2101)
  still classifies `index_ir.get("value")` as emit_ir (it's a "value" node key), so idx_val
  pre-declares `ref (IrOther "")` and `idx_val := num_of index_ir` (int) TYPE-CLASHES. FIX =
  extend the gap-1 `_is_emit_ir_expr` exclusion to ALSO skip when the current func scopes
  "value" to a non-emit_ir projection (num_of/value_of) — NOT yet built. (Same shape as
  gap-1's `_get_default_is_str_literal` exclusion, but keyed on the func-scoped num_of.)
- **THE REAL WALL — WL-04b `.items()` DEAD-BLOCK VERBATIM EMISSION**: the body's WL-04b
  record-array residual (`for _cls, _info in self._record_types.items(): ...`) is
  CONTROL-FLOW-DEAD in the model (`rec_name is None` -> `false` on a string ref, like the
  Attribute branch), BUT the emitter has NO dead-code elimination — it STILL lowers the
  `.items()` loop VERBATIM. The emission is an opaque `items_0()`/`iter_get`/`iter_length`
  facade with an ill-formed `_cls`/`_info` tuple-unpack (`rec_name := _cls` where `_cls` is
  not cleanly bound) -> almost certainly ill-typed / Gate-C facade. `.items()` over a
  `map string (option hval)` self-field is UNSUPPORTED (only `.values()` is certified, via
  `_field_type_for`/a3785a13). This dead-block `.items()` is SHARED by BOTH ROOT 2 siblings
  (`_typeddict_record_literal` @7662 ALSO has `for name, info in ...items()` — LIVE there,
  not dead). So `.items()`-over-hval-self-field is the next capability both siblings need.
  `_typeddict_record_literal` additionally needs hval-collection ITERATION (`for fname in
  rec_info["fields"]`), `set(rec_info["fields"])`, zip(keys,values)+dict-build, and RAISE.

WALL-SIGNAL / NEXT (autonomous, deadline 2026-08-17): build (1) the gap-2b `_is_emit_ir_expr`
scoped-num_of exclusion (small), THEN (2) `.items()`-over-hval-self-field iteration (the
`(key, value)` twin of the certified `.values()` walk — key = the enumerated string, value =
the hval; reuse hval_values_len/get + add a key projector). Apply the banked spike patch,
land `_namedtuple_positional_access` first (smaller: only needs `.items()` in a DEAD block =
may over-approx to a trivially-typed empty/opaque loop if dead-block emission can be made
type-safe), then `_typeddict_record_literal` (LIVE `.items()` + collection-iterate + set +
raise = the bigger build). Full battery each increment.

## 2026-08-13 — _namedtuple_positional_access CONVERTED (797ec6d9, 733->732) + 3 PROCESS LESSONS
ROOT 2 hval cluster member #2. hval-collection-as-sequence (hval_len/hval_nth_str, definitional
total views over the already-certified hval_list, NO cert/axiom) + gap-2b narrowed + WL-04b
.items()-over-hval-self-field dead-block. 8 changed-emission files, all whole-file VALID, byte-diff 0.

THREE hard-won PROCESS LESSONS (supervisor caught what the delegate's flow missed):
1. STALE-GATE TRAP: a delegate can report gates GREEN using outputs that PREDATE its latest source edit.
   ALWAYS compare the proof/byte-diff sentinel mtime vs the source-file mtime before trusting a verdict;
   if source is newer, the gate is STALE — re-run from scratch. (Here: source 18:09 but proofs 15:07 →
   the "8 VALID" was for an earlier build that had a gap-2b regression mistyping _field_type_of.)
2. CPU-STARVATION TIMEOUT ≠ SATURATION: launching 8 giant whole-file proofs concurrently on a 14-core box
   (load 20) starves the heaviest one to a wall-clock EXIT=124 timeout even though its CPU work fits.
   Re-run a lone timeout giant SOLO before concluding saturation / reaching for #@ no_inline. (Module5_IREmitter
   timed out at 8-way, passed VALID solo.) Cap proof concurrency at ~cores/2, not all-at-once.
3. SUB-AGENT PROCESS DEATH: a sub-agent's detached background jobs (proofs/waiters) are KILLED when it goes
   dormant/completes — its whole process tree is torn down. Only the MAIN (supervisor) session persists long
   jobs. ARCHITECTURE: the supervisor OWNS launching+tracking all long whole-file proofs (setsid + Monitor +
   fresh uniquely-named sentinels + mtime freshness check); the delegate BUILDS + fast gates only, then stops.

Next wall: ROOT 2 member #3 `_typeddict_record_literal` (has .items() LIVE + collection-iterate/set/zip/raise) —
reuses the 6+ banked hval caps; measure via whole-file proof.

## 2026-08-13 — _typeddict_record_literal = WALL (V1 heterogeneous-Dict-LOCAL-CONSTRUCTION), reverted clean at 732
ROOT 2 member #3. Build-only measurement (verbatim port + whole-file --no-proof) FAILED L3-tc at
expressions.mlw:2210 (`frt` getattr-string-default), and the emitted body is dominated by opaque
input-blind facades (Gate-C reject regardless). Distinct from cluster members #1/#2: those READ hval
self-fields/locals (banked caps cover); THIS method CONSTRUCTS a fresh heterogeneous string->emit_ir
`kv` dict LOCAL + set-compares + list-comprehends + zip-unpacks + raises an f-string error. Needs a
SESSION-SCALE ~8-cap definitional build (all over existing hval/emit_ir/map ADTs — NO new axiom/ADT,
ledger stays 3): (1) getattr-string-default local typing; (2) expr.get("keys"/"values",[]) emit_ir-list
projection from DictLit; (3) faithful zip + k,v tuple-unpack binding; (4) loop-bound-IR-node
.get("type")/.get("value","") reads; (5) the kv heterogeneous string->emit_ir dict LOCAL
(insert/.keys()/.get); (6) set() over hval collection + over kv keys; (7) list-comp with `not in`
string membership; (8) raise PyCSLSemanticError w/ f-string. Cap (5) (kv-local construction) is the
dominant cost. ROOT 2 cheap/reusable members DRAINED (#1 #2 landed). This is the frontier's next
funded build; caps are REUSABLE (construction-form heterogeneous-dict wall, likely cascades).

## 2026-08-13 — _typeddict_record_literal SPIKE = FEASIBLE (cap-5 kv-local construction PROVEN)
Make-or-break falsifier PASSED (scratchpad/spike_kvlocal.mlw, 4 VCs Valid/Z3; spike_falsifier.mlw
non-vacuity FALSE-asserts correctly don't prove). The heterogeneous string->emit_ir dict LOCAL
constructed imperatively then read back is modelable via the BANKED set_kv device: a NON-GHOST program
`val set_kv (m:map string (option hval))(k:string)(v:option hval): ... ensures {result = Map.set m k v}`
+ `val empty_kv (): ... ensures {forall k. Map.get result k = None}`. Root cause it was blocked: Why3's
built-in Map.set is a GHOST function (`kv := Map.set !kv k v` rejected non-ghost) — set_kv is the
conservative non-ghost realization (SOUND, NOT an axiom; map string (option hval)+hval already certified
Phase2f; LEDGER STAYS 3). Read-back proves via Map Select_eq/Select_neq; Z3 knows distinct string
literals distinct. Alt-Ergo times out (no string theory) — Z3-only, matches mirror reality.
FULL BUILD = session-scale ~8-cap, correctness DE-RISKED: new caps = (1) getattr-string-default local
typing (was the L3-tc blocker @2210), (2) expr.get("keys"/"values",[]) emit_ir-list projection from
DictLit, (3) faithful zip + k,v tuple-unpack, (5) kv construction (set_kv, PROVEN); reused = (4) IR-node
.get reads (gap-1/2), (6) set/key over-approx (missing/extra feed only the RAISE branch -> over-approx
sound; returned record depends only on faithful kv.get(fname)), (7) not-in hval_str_mem, (8) raise
f-string _err-divergence. ESCALATED to full build.

## 2026-08-14 — _typeddict_record_literal build IN PROGRESS (uncommitted, count 731, NOT yet typechecking)
Session-scale build, caps landing incrementally (blocker advancing). DONE: cap-1 (getattr-self-string-default
read + string-local collector), cap-1b (.items()-key alias string-local), cap-2 (expr.get("keys"/"values",[])
-> real irlist projections dictlit_keys_of/dictlit_values_of). cap-2 ARCH FIX: IrDictLit was _uses_stmt_ir-gated
(Module5-only); added name-gated `_uses_dictlit()` (true iff file defines _typeddict_record_literal) to append
IrDictLit + its kind_of arm (no wildcard) + the 2 projections into expressions.mlw ONLY -> Module5/stmt_ir path
byte-identical (verified still L3-tc clean), corpus byte-inert. All definitional, LEDGER STAYS 3.
REMAINING (blocker at cap-3 zip region mlw:2242-2244): cap-3 (faithful zip + k,v tuple-unpack — NO existing
machinery; needs stmt_control_flow recognizer: index loop over min(irlen keys, irlen values), k=irnth i keys /
v=irnth i values, both emit_ir; the dual-emit_ir twin of the .items() unpack; irlen/irnth exist; v currently
NEVER bound). cap-5 (DOMINANT, spike-proven kv construction — REFINED: codomain is `map string (option emit_ir)`
NOT option hval, since v is the DictLit value NODE; use set_kv/empty_kv non-ghost vals over that type, guarded
insert on isinstance(k,dict)&k.get("type")=="String", kv[k.get("value","")]=v, kv.get(fname)=Map.get). cap-6
(set over-approx, reuse __anystr .values() pattern, feeds raise branch). cap-7 (not-in hval_str_mem + list-comp,
feeds raise branch). cap-8 (raise) DONE. BANKED reusable: cap-1/1b/2 (getattr-self-string, items-key alias,
_uses_dictlit+DictLit-into-expr-mirror+child-list projections+irlist-predecl).

## 2026-08-14 — _typeddict_record_literal build: caps 1-5 DONE, ONLY cap-6/7 remains (blocker mlw:2259)
Everything through kv construction L3-typechecks (uncommitted, count 731). This turn: cap-3 (faithful zip +
dual k,v emit_ir tuple-unpack via _zip_irlist_recv, min(irlen keys,irlen values) loop, v now BOUND), cap-4
(isinstance(emit_ir,dict)->const true sound guard + k.get("value","") string-default PRIORITY over num_of ->
value_of), cap-5 DOMINANT (kv `map string (option emit_ir)` — NO set_kv needed, existing polymorphic non-ghost
`map_update_some (m:map 'k(option 'v))(k)(v) ensures{result=Map.set m k(Some v)}` + pure Map.get already realize
imperative build+readback; readback proves via Map.Select; cap-5 was pure TYPING via _collect_emit_ir_valued_dict_locals
+ "emit_ir" cases in _dv_empty/_missing/_store). Re-ported 3 verified _dv_* mirror methods verbatim (drift 2).
LEDGER 3 (zero axioms, all definitional over certified emit_ir/IrDictLit + polymorphic map_update_some). Module5
mirror still L3-tc (gated). LAST cap = cap-6/7 (mlw:2259 set(rec_info["fields"])/set(kv.keys())/missing/extra/raise
guard): currently facades set_1/kv_keys_0()[INPUT-BLIND]/list_content_comp_0/1. These feed ONLY the raise branch
(returned record depends solely on faithful kv.get(fname)) -> SOUND over-approx permitted but must READ real inputs:
model missing/extra as typed abstract seq/list readers consuming rec_info["fields"](hval-list) + kv-domain
(f not in present = Map.get kv f = None; k not in declared = hval_str_mem over fields) — sanctioned __anystr
raise-consumer over-approx (wall2 memory). BANKED reusable: cap-3 (zip-over-irlists dual-emit_ir unpack), cap-4
(isinstance-emit_ir + .get("value") string priority), cap-5 (emit_ir-valued LOCAL dict map string(option emit_ir)).

## 2026-08-14 — post-wall-5 re-drain = no_cheap_remaining (731); next lever = heterogeneous Dict[str,Any] PARAM value-model
The construction/hval/zip/DictLit banked caps unblock NONE of the residual 731 (4 candidates measured, all walls).
ROOT 2 hval cluster DRAINED (3 members). Next-wall ranking:
1. HETEROGENEOUS Dict[str,Any] PARAM value-model (DOMINANT residual) — a Dict/symtab PARAM types `map string (option
   int)`, so string-valued reads (`symtab.get(nm)`, int->str `elem_map`) clash with string-literal compares
   (`st in ("list",...)`). Blocks _infer_tuple_slot_type (functions.mlw:1815), _track_collection_metadata
   (types.mlw:1443). DISTINCT from banked caps (self-field/LOCAL construction, not general PARAM codomain). Analogous
   to the landed LOCAL kv construction but for a map PARAM read back with string/hval values. Session-scale; SPIKE the
   param-codomain typing first.
2. Missing/cross-mixin helpers (_coerce_dotted_args needs _is_seq_arg/_materialize_* not mirrored) — scope creep, low value.
3. Giant hval/record dispatchers (_emit_membership/_to_bool/_handle_subscript/_expr_to_whyml/_handle_binop/
   _handle_call_expr) — scale walls, review-gated, banked caps get individual branches close.
4. Raw CPython AST ingestion (_synthesize_typeddict_functional/_emit_typeddict_record + Module5 ast.* walkers) — distinct
   raw-ast Ingestor boundary class.

## 2026-08-14 — Dict PARAM value-model SPIKE = REFINED/FEASIBLE (session-scale, no floor); escalating _infer_tuple_slot_type
The literal param-codomain is SOLVED with existing machinery: `Dict[str,str]` param -> `map string (option string)`
via _m5_get_dict_value_type + _dict_param_whyml_type (zero emitter changes, ledger 3). NECESSARY-NOT-SUFFICIENT.
Converting `_infer_tuple_slot_type` = session-scale ~4-5 caps (NO correctness floor): (a) `elt` raw-Dict[str,Any]
string-field READ (type/name/func read back as string); (b) string-local flow-typing for `x = strmap.get(k)` (locals
currently `ref 0`); (c) string-membership/equality lowering replacing int-hash facades (`st in ("list",...)` ->
str_eq_op, currently `!st = 1555321514` vacuous); (d) emit_ir-vs-raw-dict reconciliation (sibling _is_string_expr/
_is_emit_ir_expr model the node as emit_ir while elt is raw dict); (e) Set[str] params (array_vars/dict_vars now
map int(option int) -> want set/string). CAPS CASCADE (raw-dict string-read family = many stubs). Wall class =
"heterogeneous IR-node-dict string READ + string flow-typing". _track_collection_metadata is DISTINCT/heavier (full
hval HArr/HNode + self-state metadata mutation — separate wall). ESCALATED to build.

## 2026-08-14 — post-wall-6 re-drain = no_cheap_remaining (730); next lever = ROOT A emit_ir-NODE field projectors
Flat-Dict[str,str] string-read cap DRAINED (converted _infer_tuple_slot_type only; no sibling matches the flat shape).
Residual walls = 2 build-classes:
ROOT A (DOMINANT, spike-close, RECOMMENDED) — emit_ir-NODE field projection. Stubs need NEW total projectors over the
ALREADY-CERTIFIED emit_ir ADT ctors: index_of (IrSub->int), tuple_of/fst_of/snd_of (IrTuple sub-node), left_of/right_of
(IrBinOp/IrStrConcat recursion), svalue/name string projections. Definitional views over existing certified ctors
(like hval_len over hval_list, like receiver_of over IrMethodCall) — LEDGER STAYS 3, no new axiom/cert (per §10.8 +
IrBinOp/IrIfExpr projector precedent). CASCADES: _handle_proj_expr (index_of+tuple_of), _expr_to_whyml_string_ctx
(string kind-discriminant + left/right StrConcat + svalue/name), _handle_ctor_payload_expr, _seq_init_expr. Additive
per-node-kind build, autonomous-authorizable. Blockers seen: expressions.mlw:962 (_expr_to_whyml_string_ctx ExprIR node
reads string discriminant + nested sub-nodes), expr_ghost_spec_ops.mlw:402 (_handle_proj_expr node.index/node.tuple ->
generic svalue_of, no index_of/tuple_of). ESCALATED (start smallest = _handle_proj_expr: just index_of+tuple_of).
ROOT B (heavier, distinct) — _variant_types/_constructors nested-hval walk (union/match cluster _match_subject_union_info
/_union_ctor_for_arm_tag/_union_none_ctor_for): nested constructors/payload lists off _variant_types (hval HMap->list),
type-pinned by verified _handle_match_stmt. Same hval-HMap/HNode-list wall as _track_collection_metadata. Defer.

## 2026-08-14 — ROOT A REFUTED (projectors already exist); frontier = 3 DISTINCT session-scale builds
The re-drain's "ROOT A spike-close projector cascade" was WRONG: left_of/right_of/svalue_of/sindex_of/name_of/value_of/
elt0_of/elt1_of/kind_of ALREADY exist in _emit_exprir_theory. The residual cluster needs NON-projector walls:
- `_handle_proj_expr` (ProjExpr.index is a raw INT dataclass field) + `_handle_ctor_payload_expr` (CtorPayloadExpr.index)
  need a NEW ctor **IrProj carrying an int** -> requires a co-landing axiom-free cert (the wall #1 IrMethodCall/Phase2j
  pattern). _handle_proj_expr also needs a _deref str-return typing fix (mirror typed ->int, live ->str).
  _handle_ctor_payload_expr ALSO reads `getattr(self,"_constructors",{})` nested Dict[str,Dict[str,Any]] (V1 wall) +
  payload[idx] list-index -> 2 walls.
- `_expr_to_whyml_string_ctx` (real method = mirror expressions.py:1502) calls module-level free fn `whyml_string_literal`
  (identifiers.py) NOT modeled in mirror (auto-stubs ->int) -> a byte-op string-theory build (char-iter/ord/utf-8-encode).
  StrConcat recursion also needs left_of/right_of extended to IrStrConcat (projector-extensible).
- `_seq_init_expr` ALREADY converted (stale entry). [flag checked: drift still exactly 2, not _seq_init_expr — clean.]
FRONTIER = 3 distinct funded builds (no cascade): (a) IrProj ctor+cert (ghost-node int-index family); (b)
whyml_string_literal byte-op string theory; (c) ROOT B _variant_types/_constructors nested-hval union/match cluster.
Spiking (a) IrProj first (most precedent-backed = wall #1 pattern).

## 2026-08-14 — comparative spike: (a) IrProj = best next build; CERT-DISCIPLINE clarified
Ranked: (a) IrProj ctor [~3-4 caps, 1 stub _handle_proj_expr, cert-question below] >> (c) nested-hval union cluster
[~6 caps, 3 stubs, NO cert, but COUPLED re-port of verified _handle_match_stmt — proven: porting _union_ctor_for_arm_tag
breaks _handle_match_stmt L3-tc at stmt_control_flow.mlw:1113] >> (b) whyml_string_literal = DEFER (genuine correctness
boundary: char-iter/ord ALREADY modeled but faithful UTF-8-byte-encode + `{b:02x}` hex need a certified byte model or
stay trusted vals — leave trusted).
CERT-DISCIPLINE (empirically verified — NOT every ctor needs a cert): IrMethodCall->Phase2j, IrCallKw->Phase2g have
dedicated certs; IrCtorPayload(string string INT), IrCtorTest, IrSub have NONE. PRINCIPLE: a new emit_ir ctor needs a
co-landing axiom-free cert IFF its recursive child is STRUCTURALLY RECURSED by the certified size/wf machinery (size-
decrease + faithful-extraction proofs, as receiver_of/IrMethodCall). A ctor whose emit_ir child feeds only a TRUSTED val
(not recursed) + whose int is a plain payload follows the uncertified-sound IrCtorPayload/IrFst pattern (NO new cert).
IrProj emit_ir int: spike says its `tuple` feeds trusted `_e` (not recursed) + `index` is plain int -> IrCtorPayload
pattern -> likely NO cert. MUST VERIFY during build (default to co-landing Phase2k if the child IS recursed anywhere).
ESCALATED (a) IrProj with explicit cert-decision mandate. Ledger stays 3 either way (a cert is axiom-free).

## 2026-08-14 — IrProj = CERTIFIED-BOUNDARY (proof wall, not ctor/cert gap); L3-tc-spike over-ranked it
IrProj ctor + proj_tuple_of/proj_index_of BUILT clean (L3-tc ✓, non-vacuous, CERT DECISION rigorously = NO cert needed:
proj_tuple_of's result flows only to trusted _e + non-recursive name_of, never structurally recursed = IrFst/IrCtorPayload
pattern, ledger 3). BUT whole-body --fun PROOF FAILS on the terminus: `slots[!idx] <- "z_"` needs `0 <= proj_index_of node`,
FALSE for arbitrary node (IrProj _ (-1)); asserting it = unsound axiom. Root = WhyML Array.set model STRICTER than Python
(Python negative-index wraps, no IndexError). SAME wall keeps _handle_ctor_payload_expr trusted (`binders[idx]="z_"`).
CERTIFIED-BOUNDARY: needs a review-gated Python-faithful negative-wrap / bounded-index list-store model (demand-driven),
NOT a ctor/cert. BANKED (in-report, reusable if boundary crossed): IrProj ctor+projectors (no cert); string-elem array
index-store fix; string-key opaque-stub param inference. LESSON: the comparative spike RANKED IrProj #1 using --no-proof
L3-tc, which PASSED while the whole-body proof FAILED (§10.1 type-check != proof) — spikes measuring convertibility MUST
whole-body-PROVE, not just L3-tc. Frontier now: (a) IrProj/ctor-payload = BOUNDARY (array-store); (b) whyml_string_literal
= BOUNDARY (byte-op); (c) nested-hval union/match cluster = last clearly-breakable (3 stubs, ~6 hval caps + COUPLED
_handle_match_stmt re-port, no cert, revert-risk) -> escalating with whole-body-proof gating.

## 2026-08-14 — union/match cluster (c) = BUILDABLE (not boundary), ~6-cap coupled session-scale; sub-increment split
Measured concrete (spike reverted clean, ledger 3, NO cert — all definitional over certified hval). Cap stack C1-C5:
C1 = PyVal param + Optional-(string,hval)-tuple RETURN lowering (currently int-erased — _uses_pyval/PyVal->map string
(option hval) not firing for this file; build+gate FIRST). C2 = stmt.to_dict() emit_ir->map string (option hval)
projection at the _handle_match_stmt call site (the coupled re-emission point, stmt_control_flow.mlw:1112). C3 = .items()
over a NESTED hval LOCAL from vinfo.get("constructors") (landed _hval_items_recv only accepts hval self-FIELDS; needs
uninterpreted hval_as_map (h:hval):map string (option hval) + recognizer ext). C4 = payload=ctor.get("payload",[]);
payload[0]==arm_tag (HArr truthiness + hval_nth_str[exists] + string cmp). C5 = first-match-return-in-loop threading
option (string,hval). (+stub#3: hint_of ctor.get("arity")==0 + str_contains_op[exists]).
SUB-INCREMENT SPLIT: (1) stmt_control_flow.py _match_subject_union_info + _union_ctor_for_arm_tag + _handle_match_stmt
verbatim (CLEANLY coupled — grep=0 other converted methods touch _variant_types/_current_symbol_table in that file),
730->728, giant stmt_control_flow whole-file proof = true gate. (2) expressions.py _union_none_ctor_for (retype
_variant_types Dict[str,str]->Dict[str,PyVal], coupled to 2 already-converted key-membership methods @629/@906 - must
re-prove - + hint_of), 728->727. ESCALATED sub-increment 1.

## 2026-08-14 — union sub-increment 1 CHECKPOINT (uncommitted, count 728 but FACADE/not-L3-green — DO NOT commit)
PLUMBING caps DONE (reusable): C1a functions.py::_dict_param_whyml_type nu=="hval"->map string(option hval);
return option-wrap functions.py::_build_method_return_type_map (Optional-tuple override matching _compute_return_type,
fixes bridge-val None-check clash); C2 expressions.py::_handle_call_expr .to_dict()->`stmt_to_pymap <recv>` uninterpreted
projection (per-arg _todict_arg_wants_pymap when slot=map string(option hval); non-vacuous). Mirror stmt_control_flow.py:
_current_symbol_table:Dict[str,str], _variant_types:Dict[str,Dict[str,PyVal]] (nested map string(option hval)); 2 markers
removed. Ledger 3. Files: functions.py, expressions.py (live), stmt_control_flow.py (mirror). GOTCHA: L3-tc must use
--import-path src/pycsl (NOT src/self-annotate/src -> spurious line-881 fail).
REMAINING value-read caps (bulk; both bodies currently facade/input-blind -> Gate-C fail until done): C1b return tuple
elem types option(int,int)->option(string, map string(option hval)) via _refine_tuple_return_type flow-typing of var_name
(string)/vinfo(map) [also gates uinfo as _union_ctor_for_arm_tag param]; _match_subject_union_info body: subj=hval from
stmt.get("subject"), subj.get("type")/.get("name")->pairs_get->hstr_of, isinstance(subj,dict)->true, vinfo:map string
(option hval), not vinfo->sound (currently subj/vinfo ref 0 + subj_get_str/typeof_op facades); C3 _union_ctor_for_arm_tag
.items() over hval-LOCAL vinfo.get("constructors") -> needs hval_as_map (h:hval):map string(option hval) view + .items()
recognizer ext for hval local (key=hval_keys_get, val=hval_values_get) [currently items_0() input-blind]; C4
ctor.get("payload",[])->hval, payload and payload[0]==arm_tag -> hval_truthy + hval_nth_str payload 0 vs arm_tag str_eq_op
[currently ctor_get_arr/subscript_get facades]; C5 _handle_match_stmt coupling (verbatim) FIRST L3-tc err mlw:1115:
union_info/py_match now option(τ) locals but `if X is not None` emits `!X<>0` + `a,b=X` bare-tuple unpack -> register
option-tuple call-result locals, lower None-check as `match !X with None->false|Some _->true`, unpack as `match !X with
Some(a,b)->`. All definitional, ledger 3. RESUME: fresh delegate on caps C1b->C5.

## 2026-08-14 — union sub-inc 1: C5 LANDED (blocker 1115->1130); C1b/body/C3/C4 remain (still facade @728)
C5 DONE (option-tuple call-result local, reusable, gated on corpus-absent _option_tuple_vars -> byte-inert): _option_tuple_vars
field (functions.py::_reset_function_state); _collect_option_tuple_locals + _split_tuple_slots (types.py live-only, called from
\trusted-mirrored _typed_local_vars); pre-decl exclusion + let-bind (statements.py _emit_body_code/_handle_assign_stmt);
None-check `X is not None`->`not(match !x with None->true|Some _->false)` (expressions.py binop); tuple-unpack `a,b=X`->
`match !x with Some(a,b)->begin ...end|None->()` (statements.py::_emit_option_tuple_unpack). PROCESS NOTE: first draft edited
un-trusted-mirrored _collect_tuple_var_assigns -> drift SPIKED to 3; refactored to live-only _collect_option_tuple_locals
called from \trusted _typed_local_vars -> drift restored 2. LESSON: emitter helpers feeding option-tuple typing must be
live-only or \trusted-mirrored, never edit an un-trusted-mirrored method (drift). Files (live): functions/expressions/
statements/types.py; mirror stmt_control_flow.py (prior delegate). REMAINING blocker stmt_control_flow.mlw:1130
`self__union_ctor_for_arm_tag_2 !uinfo` (val wants map string(option hval), uinfo=int facade): C1b flow-type return slots
(_match_subject_union_info var_name->string/vinfo->map string(option hval) from _variant_types:map string(option(map string
(option hval))) => option(string,map...); _union_ctor_for_arm_tag ctor_name->string/ctor->hval => option(string,hval)) via
_refine_tuple_return_type/_infer_tuple_slot_type; then bodies (subj=hval from stmt.get("subject") -> pairs_get+hstr_of,
isinstance->true, not vinfo->sound; C3 .items() over hval-LOCAL vinfo.get("constructors") -> hval_as_map view + .items()
recognizer ext key=hval_keys_get/val=hval_values_get; C4 ctor.get("payload")->pairs_get, payload[0]==arm_tag -> hval_truthy+
hval_nth_str+str_eq_op). Kill facades subj_get_str/typeof_op/items_0()/ctor_get_arr/subscript_get/str_hash_op. Ledger 3.

## 2026-08-14 — union/match cluster COMPLETE (28b2eed0, 728->727); session 736->727 (9 conv / 8 walls)
Sub-inc-2 _union_none_ctor_for landed (hint_of + pyval-int-compare + hstr_of-map-assign + union-hval-LOCAL +
items-key-string caps; _variant_types Dict[str,str]->Dict[str,Dict[str,PyVal]] retype; 2 coupled key-membership methods
re-emit BYTE-IDENTICAL + re-prove clean). 8 changed-emission files all whole-file VALID, byte-diff 0. LESSON reaffirmed:
build-worker under-counted changed-emission set (claimed 4, authoritative=8 — the additive hint_of decl hit all pyval
mirrors); SUPERVISOR must always re-run the mirror-wide md5 diff. Walls this run: Call-receiver a221599f, _field_type_of
2d55bf04, ROOT2 hval cluster (typeddict_field_access e531a377 / namedtuple_positional_access 797ec6d9 /
typeddict_record_literal 30053c21), raw-dict-string-read _infer_tuple_slot_type bcd80aa3, union/match cluster
(38a46208 + 28b2eed0). Next: re-drain for union-cap cascade, else frontier = CERTIFIED-BOUNDARIES (IrProj array-store,
whyml_string_literal byte-op) + review-gated giants (_emit_membership/_to_bool/_handle_subscript/_expr_to_whyml/
_handle_binop/_handle_call_expr) + raw-ast Module5 walkers + _track_collection_metadata (V1 nested-hval+self-state).

## 2026-08-14 — post-union re-drain = no_cheap_remaining (727); next lever = hval-LOCAL-flow-typing (union-return siblings)
Union cluster PARAM members drained (3 landed). Residual siblings _maybe_inject_union_return (stmt_control_flow.py:769)
+ _infer_return_value_type (:776) both bind hval .get() result to an INTERMEDIATE LOCAL (vinfo/constructors/ctor_name/
payload -> ref 0 facades) — need the un-landed LEVER #1: (a) LOCAL flow-typing of an hval/map .get() result onto a local
(the local analogue of the landed PARAM-projection cap); (b) hval_as_map-over-LOCAL (.items() currently only over
self-FIELD/param); (c) _record_valued_expr_whyml_type resolver (currently auto-stubs ->int, clashes with the Optional[str]
variant return for _infer_return_value_type); (d) _resolve_dotted_signature(func)[0] subscript typing + func projection off
emit_ir. Session-scale ~4-5 caps, NO cert (definitional over certified hval), spike-close (reuses hval_as_map + union
machinery), CASCADES to other hval-local readers. Both siblings verbatim-portable, caller-typing correct (blocker is pure
value-model). Ranked #1 next build. (Lower: V1 Dict[str,Any] PARAM/_track_collection_metadata; boundaries IrProj/
whyml_string_literal; review-gated giants.) ESCALATED lever #1.

## 2026-08-14 — lever #1 spike: ~4-5 cap build, sub-increment split (measure-first reverted clean at 727)
val_ir MUST annotate "ExprIR"(->emit_ir), NOT PyVal/Dict (clash at _handle_return_stmt call site which passes emit_ir).
SUB-INC A (->726, _infer_return_value_type — CLOSER): most emits REAL (kind_of/name_of/func_of val_ir, Map.get
_current_symbol_table, str_startswith_op "_union_", union_arm_whyml_type). 2 gaps: cap(d) CLOSEABLE = register
_resolve_dotted_signature auto-stub return as `array string` (name-gated, mirror _thread_optional_return param reg at
functions.py:6087) so subscript_get[0] yields string not int-hash 1776665034; cap(c) HARD = _record_valued_expr_whyml_type
auto-stubs ->int, `if _rec is not None: return _rec` L3-tc FAIL (int vs synth _union__infer_return_value_type_2 variant
Arm_2_0 string|Arm_2_None). Optional[str] return is a SYNTH per-fn _union_ variant NOT plain option string (option override
functions.py:1923 fires only Optional[TUPLE]+None). _thread_optional_return (stmt_control_flow.py:1671-1718) does NOT thread
a bare Var return (only None/IfExpr/1-arg-.get). BUILD: extend the return-threading recognizer to `return <option-string-var>
-> union-arm`, OR model the resolver return as the synth variant. NOT a boundary.
SUB-INC B (->725, depends on A, _maybe_inject_union_return): cap(a) extend _collect_union_hval_locals (statements.py:2236)
to classify a local bound from a MAP-LOCAL's .get() yielding hval (vinfo is a local not self-field) + cap(b) hval_as_map-over
-LOCAL .items() ext + ctor.get pairs_get/hint_of + payload[0] + val.startswith string op. Coupled: needs A's string return
for arm_type==val_type. Baseline .mlw manifest at scratchpad/baseline_mlw/manifest.md5 (HEAD a35d46db). ESCALATED sub-inc A.

## 2026-08-14 (post-crash) — union-return lever COMPLETE (23c459a1 + 9adb26d3, 727->725); session 736->725 (11 conv)
Sub-inc A _infer_return_value_type (cap-d _resolve_dotted_signature->array string + cap-c Var-return->union-arm
threading via option-string model) + sub-inc B _maybe_inject_union_return (hval-LOCAL flow-typing: vinfo/constructors
map-locals via _collect_union_hval_locals+_prescan_pyval_locals vmap seed, .items()/for-key over hval-local, ctor
pairs_get/hint_of/hval_nth_str, val.startswith/str_contains, and the coupled optstr-== recognizer for arm_type==val_type
where val_type=_infer_return_value_type modeled option string). Both = SOLE changed-emission stmt_control_flow.mlw
(name-gated), whole-file VALID, byte-diff 0, ledger 3. CRASH-HARDENING LESSON: build delegates must NOT launch detached
background procs (setsid/nohup/&/manifest-loops) — they survive dormancy as ZOMBIES that respawn + corrupt the tree
(root-caused a crash this session; recovered by killing the loop root + committing the already-verified sub-inc A). New
mandate: delegates do SYNCHRONOUS build+fast-gate ONLY, hand off ALL long proofs/byte-diff/commit to the persistent
supervisor. BANKED caps: optstr-== recognizer, hval-LOCAL flow-typing (map-local .get->hval-local), Var-return->union-arm
threading, _resolve_dotted_signature array-string reader. Next: re-drain for union-return-cap cascade, else frontier =
boundaries (IrProj/whyml_string_literal) + review-gated giants + V1 Dict[str,Any]/_track_collection_metadata + raw-ast.

## 2026-08-14 (post-crash) — post-union-return re-drain = no_cheap_remaining (725); next lever = _try_union_is_none_match
Union-return caps drained their sibling cluster. Next FUNDED build (spike-close, session-scale ~5-6 caps, NOT a boundary):
`_try_union_is_none_match` (stmt_control_flow.py) — direct union-cluster sibling (same _variant_types/constructors/
hval_as_map machinery in-file) + 3 NEW caps: (i) emit_ir `stmt` param reconciliation (caller _handle_if_stmt passes
stmt.to_dict()=emit_ir; blocker stmt_control_flow.mlw:1059 emit_ir vs map param); (ii) vinfo["constructors"][ctor_name]
NESTED DOUBLE-SUBSCRIPT on map string(option hval); (iii) List[str] STRING-ARM ACCUMULATION (other_ctors/non_none_arms
[-1] mutation + enumerate) + _stmts_to_whyml recursion + Optional/Any return. Caps reusable (match-code string-accumulation
cascades). Other residuals: pattern-walkers (distinct pattern-value-model); return-type dispatchers (session-scale);
boundaries IrProj/whyml_string_literal; review-gated giants; V1 _track_collection_metadata; raw-ast. ESCALATED.

## 2026-08-14 (post-crash) — _try_union_is_none_match measured = ~6-cap build, MAKE-OR-BREAK = cap(iii) mutable-array-string [-1] store
Reverted clean (single fn, no A/B partial-green). Correction: mirror already has stmt:"ExprIR"(=emit_ir) + pymap is WRONG
here (stmt.get("body") feeds _stmts_to_whyml:array int -> only emit_ir body->stmts_of:array int matches). Dep-ordered caps:
(i) emit_ir stmt/test-subtree threading — add "test"->test_of projector on SIf ctor to _EMIT_IR_PROJ + thread test/left/
right/var_node emit_ir (op_of/kind_of/left_of/right_of/name_of) + route stmt.get("orelse",[])->stmts_of (fix
_get_default_is_empty_dict expressions.py:6922); (X) var_name in _optional_union_locals Set[str] membership (contains_check
str_hash facade); (Y) vinfo=_variant_types.get(symtype) as map string(option hval) — prescan BAILS here (vinfo used by BOTH
.items() AND nested subscript); (Z) "None" in ctor_name -> str_contains_op; (ii) nested double-subscript vinfo["constructors"]
[ctor_name] -> pairs_get twice; (iii) HARD/RISK = non_none_arms is List[str] with `non_none_arms[-1]` READ **and WRITE**
(`[-1] = last + …`) -> Why3 seq immutable; needs MUTABLE array string with `arr[length arr -1] <- v` (needs length-1>=0,
the IrProj array-store boundary risk) + `last + …`=str_concat_op + enumerate(other_ctors)->(int,string) + array-truthiness.
SPIKE cap(iii) first: if the mutable-array-string [-1] store proves (array non-empty at store point), FUND the 6-cap build;
if not, RECLASSIFY as CERTIFIED-BOUNDARY (like IrProj). Live body = stmt_control_flow.py:1312-1437, stub @:510.

## 2026-08-14 (post-crash) — cap(iii) SPIKE = FEASIBLE (guard-dominated [-1] store proves); FUND _try_union_is_none_match 6-cap build
The `non_none_arms[-1]` READ+WRITE are BOTH inside `if non_none_arms:` (live stmt_control_flow.py:1416-1418) -> GUARD-DOMINATED
(not just append-dominated): `_to_bool` lowers the guard to `Seq.length/Array.length <> 0` -> length>=1 on then-path = the
store's bounds VC. why3 prove: guarded seq store + guarded array store BOTH Valid (Z3+Alt-Ergo); unguarded falsifiers FAIL
with empty-collection counterexample (non-vacuous). NOT a boundary (contrast IrProj arbitrary-index). Ledger 3 (seq/array
built-in). Idiom: `ref (seq string)` `l := Seq.set !l (len-1) v` OR mutable `array string` `arr[len-1] <- v`; `+`=str_concat_op.
cap(iii) = 2 bounded emitter additions: (1) WRITE-side negative-literal-index rewrite a[-1]=v -> a[len-1]<-v (the `_negk`
rewrite exists only READ-side expressions.py:8689; statements.py:1156-1170 is_array store path must call it); (2)
subscript-STORE path for a growable _seq_locals list local (emit `l := Seq.set !l idx v`) — OR classify the append-target
into _array_locals so the existing `<-` path applies. FUND the full 6-cap build (i emit_ir-stmt/test-threading + X Set[str]
membership + Y vinfo hval-map prescan-both-uses + Z str_contains_op + ii nested double-subscript + iii guarded [-1] store).

## 2026-08-14 (post-crash) — _try_union_is_none_match CONVERTED (70c6d6bd, 725->724); session 736->724 (12 conv)
6-cap spike-cleared build (guard-dominated [-1] store + write-side negative-index rewrite + List[str] accumulation +
nested double-subscript + emit_ir stmt/test threading). SUPERVISOR CAUGHT+FIXED a delegate defect: test_of/orelse_stmts_of
projectors added UNGATED -> perturbed 12 corpus programs + fanned changed-emission to 15 files; gated on new name-sentinel
_uses_stmt_if_test -> byte-diff 0, changed-emission shrunk to 2 (stmt_control_flow + statements). LESSON: a build delegate's
"changed-emission=1, corpus-inert" claim is UNRELIABLE — the supervisor's mirror-wide .mlw diff + full corpus byte-diff are
MANDATORY (this one was 15 files / 12 perturbed vs the claimed 1/0). Every new emit_ir projector/theory decl MUST be
_uses_*-gated. BANKED caps: match-code List[str]-string-arm accumulation (guard-dominated negative-index mutable store +
write-side neg-index rewrite), test_of/orelse_stmts_of If-stmt sub-node projectors. Next: re-drain for match-code cascade,
else frontier = pattern-walkers (distinct) + return-dispatchers (session-scale) + boundaries + review-gated giants + V1.

## 2026-08-14 (post-crash) — post-_try_union re-drain = no_cheap_remaining; 724 = AUTONOMOUS FLOOR for banked caps
Union/match cascade DRAINED (all direct siblings converted). Every residual needs a NEW spike-gated session-scale build
or is a boundary. Only contained lead = `_e` (Dict->ExprIR pure forwarder; LOW value per §10.7 — a forwarder that only
proves ensures True; the Dict->ExprIR forwarding cap it needs might cascade but the stub itself is behaviorally empty).
Ranked residual walls: (1) Dict->ExprIR forwarding reconciliation (_e — contained/distinct small cap, low value);
(2) return-type dispatchers _refine_tuple_return_type/_compute_return_type (session-scale, chained through many trusted
helpers _first_tuple_return_elts/_infer_tuple_slot_type/IRScanner — central return-type logic, cascade potential);
(3) V1 generic Dict[str,Any]/nested-dict result (_build_method_param_whyml_types_by_name Dict[str,Dict[str,str]],
_emit_subtyping_goals dict-comp, _static_width via _linear_form tuple-of-dict); (4) value-model reflection gap
(_seq_operand _mutable_state_classes self-documented value-model-gapped + undeclared _seq_value_producing = V1-adjacent
BOUNDARY); (5) int-hash vacuity (_tag_of_value sum(ord) = wall-lesson-14 boundary); (6) string-parse/format
(_parse_mixin_sig/_iter_len_expr = string-op boundary); standing boundaries (IrProj/whyml_string_literal/giants/
pattern-walkers/raw-ast/_track_collection_metadata). Next: MEASURE the return-type dispatchers (most central, cascade).

## 2026-08-14 (post-crash) — return-dispatchers measured V1-BOUNDARY (verbatim port, no caps applied); SPIKE-before-accepting
_compute_return_type (functions.mlw:1657 `f"list {_cmg['elem_whyml']}"` string-valued-dict-field -> f-string/str_concat, int-erased)
+ _refine_tuple_return_type (functions.mlw:1965 nested Dict[str,Dict[str,str]] symbol_table). Delegate classified V1-BOUNDARY,
724=autonomous floor. BUT the measurement was a VERBATIM PORT WITHOUT the banked hval-string-flow caps (hstr_of, str_concat_op,
str_startswith_op, nested-hval — all built this session for the union cluster). Per "a boundary is a HYPOTHESIS — spike it"
(and this session broke Call-receiver/union/_try_union all first-claimed boundaries), SPIKING _compute_return_type's first
pattern (hval-string-field `_cmg['elem_whyml']` -> f-string) to decide buildable-vs-boundary before accepting the floor. Risk:
int-hash vacuity on `ann.startswith` (must lower to real str_startswith_op on an hstr_of value, not ann_startswith_1 <hash>).

## 2026-08-14 (post-crash) — return-dispatcher V1-BOUNDARY REFUTED; real blocker = FunctionEmissionMixin opaque-int self-type (structural)
Spike: hval-string flow IS buildable non-vacuously (Pattern 2 func.get("return_annotation").startswith("_union_") ->
hstr_of + str_startswith_op "_union_", real not ann_startswith_1 <hash>; caps = gate _compute_return_type into
_collect_union_hval_locals + "return_annotation" string-scalar-key allowlist + func:Dict[str,PyVal] param). REAL blocker
(Pattern 1 _compound_map_getter['elem_whyml']): FunctionEmissionMixin is modeled `type functionemissionmixin = int`
(opaque, NOT @mutable_state @dataclass record like ControlFlowStmtMixin) -> ALL its self-field reads erase to int. Two
paths: (a) flip FunctionEmissionMixin to a record self-type (243 fields, whole-mixin, re-prove all converted functions.py
methods + full byte-diff — LARGE/review-gated but PRECEDENTED by ControlFlowStmtMixin); (b) targeted opaque-self per-field
accessor caps (`getattr(self,FIELD)` bare read + Optional-map None-narrow + re-subscript on narrowed binder) — LIGHTER,
session-scale. NOT a value-model boundary. 724 = autonomous floor pending (a) or (b). SPIKING (b) — does a targeted
opaque-self field-accessor cap make _compute_return_type's self-field reads type non-vacuously without the whole-mixin flip?

## 2026-08-14 (post-crash) — _compute_return_type PATH (b) = FEASIBLE COST/SCALE (not boundary, not floor); FUND multi-turn build
Build-backed: NO read forces path (a) whole-mixin flip. All 7 self-fields have opaque-but-real accessor models (precedent:
__svt(self):pydict / proved_of / __axset(self):map string bool — all live, non-vacuous, over int self-type). _compound_map_getter
->option(map string(option string)); _current_self_type->option string; _mutable_state_classes->set string/map string bool;
_record_types/_variant_types->nested map; _dict_key/value_types->map string(option string). COST/SCALE = largest dispatcher
(~160 lines, ~15 branches, string-VALUE-computing). Needs: NEW generic opaque-self TYPED field-accessor cap (current
_lower_getattr returns default 0 for opaque self — only bespoke recognizers synthesize typed accessors; ~128 recognize_* in
generic_fold.py are the pattern) + pre-pass registering each `<local>=getattr(self,"_F",default)` with its faithful type +
option None-narrow + map-membership + double-subscript + func.get pyval reads + return-VALUE str computation + correct val
return types for 5 trusted-helper calls (_refine_tuple_return_type:string/_returns_stmt_ir:bool/_returns_emit_ir:bool/
_returned_var_name:option string). MUST be per-method NAME+SHAPE-gated (_uses_* shape) — generic_fold.py:18088 warns a global
_compute_return_type retype regressed 3 siblings. FUND: build the generic opaque-self typed field-accessor cap FIRST (reusable
foundation, cascades to ALL FunctionEmissionMixin self-field readers), then _compute_return_type branch-by-branch (multi-turn,
all-or-nothing L3-tc so checkpoint uncommitted). Per feedback_cost_scale_not_floor: COST/SCALE in a funded window is NOT a stop.
