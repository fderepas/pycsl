# Seven Authorize-First Levers — Plan to Reduce the Self-TCB Below 754

**Context.** Run #3 of the self-tcb-reduction driver drove the self-annotation mirror's
`#@ \trusted` count `783 → 754` (29 conversions) and then bottomed out. Every *reachable*
vein was drained with the existing (ledger-3, no-new-axiom) device set; the residual ~754
stubs are all blocked behind **capability gaps in the emitter** (`src/pycsl/`). Each lever
below is one such gap. Building it reopens a cluster of currently-blocked stubs.

**Hard invariants for every lever (non-negotiable):**
- **LEDGER STAYS 3.** Any new WhyML value shape needs an *axiom-free* co-landing certificate
  (Rocq + Lean, a conservative side-car in `src/formal-semantics/`), verified with
  `Print Assumptions` / `#print axioms` == 3 after. `proof_axiom_allowlist.py` never touched.
- **Verbatim mirror bodies**; a refactor is a REJECT.
- **Corpus byte-diff.** A mirror-only recognizer must be byte-inert (0 across the 627-corpus).
  An emitter change that alters corpus output is a *semantics* change and needs the M1
  discipline (the diff is exactly the change AND every affected program re-proves).
- **Three L-planes each increment:** fidelity (mirror-check) ∧ whole-file Why3 proof (0
  non-Valid, no sibling regression) ∧ corpus byte-diff-0 (or sanctioned M1 reset).
- **Method:** spike-first (make-or-break falsifier before any build) → build → three-plane gate.

**Suggested order:** #7a (byte-inert, ready, also a soundness fix) → #1 and #2 (highest
cross-file leverage) → #3 → #4/#5/#6 as follow-ons. #1 and #2 are independent and could run
in parallel.

---

## Lever 1 — Pydict copy-and-set-field / dict-param-mutation construction primitive
**Gap.** The emitter models heterogeneous `Dict[str, Any]` as *readable* (pget_dyn / pget_list /
size_dict / K_dyn) but has **no sound write/construct op**: `dict(func)` + `func["x"]=v`,
`{**a, **b}` merge, `d.insert/append`, and in-place `m[k]=v` on a **by-value dict/set param**
all hit "in-place mutation of dict/set parameter out of scope" or "no construction primitive".

**Reopens (largest cross-file cluster):** `ir_resolve` (`_strip_dir_scan_proofs`,
`apply_inheritance`, `apply_composition`, `_inject_functions`, `_rewrite_ir_calls`); all of
`ir_inline` (`_substitute`, `_Inliner.*`, `_inline_calls`, `apply_inline_globals`); Module5
record-builders (`_csl_in`, `_build_function_ir`, `_build_function_symbol_table`);
`functions._build_method_*_map` (nested-map); `_extract_happy_properties`; `Module3_Weaver`
`_subst_var`/`_subst_csl_param` (dataclass-reflection variant); `pycsl.py` record mergers
(`_merge_records_best_of_n`, `_record_key`, `_finalize`).

**Build.** A certified pydict-construction op: `pput : pydict → K → pyval → pydict`
(`ensures result = <the updated dict>`), a list-insert/append analogue, and a by-reference
frame for `#@ assigns d` where `d` is a dict/set param. Co-landing §10.5 cert that the new
construction value is sound (conservative side-car; ledger 3). The read-side `pget_*` already
exists — this is the missing *write* half.

**Spike (make-or-break).** Isolation `.mlw`: a `dict(func)` copy + one `pput` field-replace +
`#@ ensures True / assigns result`, prove the VCs discharge axiom-free; confirm the pput
`ensures` composes with the existing pget readers without E-matching blowup. REFUTE if the
construction can't be certified axiom-free → real boundary.

**Risk.** Medium. Emitter-touching → full corpus byte-diff (should be inert: name-gated
recognizers, corpus programs don't use these self-annotation shapes). The cert is the load-bearing part.

---

## Lever 2 — Typed record-field accessors / CSLNode-as-variant
**Gap.** The CSL-node and IR record ADTs (Var/Number/BinOp/… ~213 CSLNode subclasses; the Term
ADT) are modeled as opaque `int` with **int-only** auto-generated field accessors
(`get_name`/`get_op`/`get_value` all `: int`) and an opaque `isinstance_op` (constant args).
So only **int-returning** readers convert faithfully (that is exactly why `_const_int` landed
but `_csl_to_str` type-failed: `get_name` is needed as `string`).

**Reopens:** the isinstance-string-readers (`_csl_to_str` in Module2_Parser) AND the `canonical.py`
**Term→Term rewriter family (9 stubs:** `substitute`, `_ac_normalize`, `_alpha_rename`,
`_flatten_foralls`, `_normalize_names`, `_dedup_arrow_chain`, `_sort_arrow_hypotheses`,
`_iff_app_to_binop`, `_expand_nat_to_int`) — those also need Lever 1's construction op for their
rebuilt-Term returns, so 1+2 together unlock the whole rewriter vein.

**Build.** Two options (spike both, pick the cheaper):
(a) type each field accessor *per field* off the isinstance narrowing (`get_name`/`get_op` →
`string`, `get_value` → `int`); or
(b) model CSLNode/Term as a genuine Why3 **variant** ADT and route through the existing
`recognize_term_string_pp` catamorphism (`generic_fold.py:28069`) — but that recognizer is
2-param `(term, prec:int)` over a variant `spec["ctors"]`, and the CSL readers are 1-param with
no variant model, so (b) is the larger build. Co-landing cert for the variant value if (b).

**Spike.** Convert `_csl_to_str` with option (a): give `get_name`/`get_op` string type off the
narrowing, prove the recursive str-catamorphism (size-measure variant) discharges. PASS → build
(a) across the readers; then attempt one `canonical.py` rewriter (needs Lever 1).

**Risk.** Medium-high (touches the record ADT model / accessor typing). Corpus byte-diff required.

---

## Lever 3 — Faithful `List[str]` string-membership + f-string-literal preservation
**Gap.** Two emitter-core string limits: (1) `x not in field_targets` over a `List[str]` lowers
to `contains_check (str_hash_op x) field_targets` — int vs `seq string` clash; (2) f-string
literal segments lower to hashed ints (`str_concat` type error). The str-build lowering itself
(`str_of_int`, `str_concat`) is fine — only these two reads/literals are wrong.

**Reopens:** ~30 WhyML string-emitters that are otherwise reachable — `statements.py`
(`_emit_frame_condition`, `_seq_init_expr`, several `_handle_*`), `preamble.py`
(`_emit_*` families), `Module6_WhyMLTranspiler.py`, `pycsl.py` (`_synthesize_*`, `_record_answer`),
`proof2why3` (`_strip_rocq_comments` and the regex/str residue that isn't pure `str_to_int`).

**Build.** (a) Lower `List[str]` membership to a real `Seq`/`StrSet` `contains` without int-hashing;
(b) preserve f-string literal segments as real WhyML `string` literals (not int hashes) in the
`str_concat` chain. Both are lowering fixes, not new value shapes → likely no new cert.

**Spike.** `_emit_frame_condition` (the cleanest str-emitter): fix the `List[str]` membership
lowering, prove it. Confirm byte-inert on corpus (f-string/list-membership are common in corpus
programs → this fix's byte-diff is the make-or-break; if non-inert it's semantics-changing = M1
discipline, review-gated).

**Risk.** High byte-diff risk (touches common lowering paths). Must byte-diff before landing.

---

## Lever 4 — getattr-self-mutable-field emitter capability
**Gap.** `st = getattr(self, "_current_symbol_table", None); st[v] = "str"` — the alias `st` is not
modeled as the mutable self field, so the write can't be framed (`assigns self._current_symbol_table`),
and declaring `assigns \nothing` would be an unsound trusted-frame-drop. A positive-control `.mlw`
proves Why3 *can* frame a self-map write — so this is purely an emitter modeling gap, not proof power.

**Reopens:** the self-collection-mutation-frame class — `_collect_string_elem_read_locals`,
`_collect_field_decode_str_locals` (statements.py), and similar self-registry writers.

**Build.** Model `getattr(self, "<field>", default)` as the mutable self field, and local-alias
mutation `st[v]=x` as a self-map-set through a program `val` set-device (the `__setk`/Map.set
family, sound conservative realization — NOT an axiom). Needs Lever 1's dict-set op underneath.
Faithful lowering of the `Any` map-value type.

**Spike.** Positive control already exists (Why3 frames a self-record map write). Spike: model
`_collect_string_elem_read_locals`'s getattr-alias as the mutable self field + `__setk` write,
prove whole-file. REFUTE if the heterogeneous `Any` map-value can't be faithfully typed.

**Risk.** Medium. Depends on Lever 1. Corpus byte-diff (self-annotation-only shape → likely inert).

---

## Lever 5 — Cross-mixin declared-interface (`#@ requires_method`)
**Gap.** `bin/check-self-annotate-mirror-sync.py` requires an un-`\trusted` mirror function to be
byte-identical to a live function at the **same relative path**. But ~20 `statements.py` stubs are
*re-declarations* whose real bodies live in `expressions.py`/`types.py`/`preamble.py`
(`_expr_to_whyml`, `_e`, `_coerce_to_int`, `_field_type_for`, …). Giving them bodies in the mirror
`statements.py` yields functions with no live anchor → unsound / skipped by the fidelity oracle.

**Reopens:** ~20 cross-mixin `statements.py` re-declarations + `functions.py`
`_build_method_field_param_frame_ensures_map` (calls `self._frame_trigger_term`, absent from the
mirror `functions.py`).

**Build.** A declared-interface mechanism — a `#@ requires_method`/`#@ interface` annotation that
lets a mirror method reference a sibling-mixin method as a *contracted opaque val* (not inlined),
with the fidelity oracle checking the interface not a same-path body. (Some `#@ interface`/`#@ reveal`
machinery already landed for Track B — extend it to the cross-mixin case.)

**Spike.** Pick one clean cross-mixin stub (e.g. `functions._build_method_field_param_frame_ensures_map`),
declare `_frame_trigger_term` as an opaque contracted val, prove whole-file. REFUTE if the fidelity
oracle can't be taught the interface check.

**Risk.** Medium (touches the fidelity/mirror-sync tooling). Mirror-only → byte-diff 0 by construction.

---

## Lever 6 — Value-preserving `or`/`and` over structured types
**Gap.** Python `A or B` in body context lowers to an **int truthiness collapse**
(`if (A<>0)||(B<>0) then 1 else 0`), regardless of operand type. So converting a callee to require
a structured param (e.g. `emit_ir`) type-fails its *verified caller* that passes `A or B`
(int ≠ emit_ir) — the `_try_local_decl_kind` wall.

**Reopens:** `_try_local_decl_kind` (Module6) and any callee fed by an `and`/`or` of structured
values from a verified caller.

**Build.** A value-preserving short-circuit `or`/`and` lowering over structured types (return the
selected operand, not an int), plus a structured-emptiness/truthiness predicate (the live falsy
sentinel is `{}`). Touches the and/or lowering **every corpus file depends on** → highest byte-diff risk.

**Spike.** Make-or-break: can `emit_ir or emit_ir` lower value-preservingly WITHOUT changing the
int-truthiness output for int operands (so corpus stays byte-identical)? If the fix can be gated to
structured operands only → inert; if it changes int `or` → semantics-change, M1 discipline / review-gated.

**Risk.** Highest byte-diff risk. Lowest single-stub payoff (+1). Do last.

---

## Lever 7 — Module6_WhyMLTranspiler.py triple-masked package  *(also a SOUNDNESS item)*
This file is **RED at HEAD** — a `_union__hdr_name_5` type error aborts its whole-file *type-check*,
so **no solver goal has ever run on it**, yet **~3 of its methods are marked converted
(illusory-verified — not backed by any passing whole-file proof).** Three sub-tasks:

### 7a — Byte-inert union-arm fix  [READY, characterized, do first]
`_sig_val_from_let`'s nested `def _hdr_name` returns a string ternary lifted to
`Optional[str]` = union `Arm_5_0 string | Arm_5_None`, but `_handle_ifexpr_expr`
(`expressions.py`) only str-types ternary arms under `_str_ctx` (@mutable_state OR
return=="string"); a `_union_*` return hits neither, so `else ""` hashes to int `313406155` and
the arms aren't wrapped in `Arm_5_0`. **Fix:** add predicate `_func_ret_union_some_str()` and
OR it into (i) the ternary `_str_ctx` gate and (ii) the `IfExpr` branch of `_is_string_expr`
(both in `expressions.py`) → wrap the whole ternary in `Arm_5_0`, emit real `""`. **Verified
byte-inert** on all 4 Optional[str] corpus files (0946/0947/0942/0892 byte-identical) +
`pure_ast.py` no-regression. Risky-class (conditional-lowering) so flagged, but ready.

### 7b — `_collect_variant_var_assigns'vc` proof-scale timeout  [review-gated]
Once 7a clears the type error, exactly one goal times out (~23.5s / 5.59M steps) — recursive
pydict/pyval fold variant-decrease E-matching saturation (the isolation_spike_not_whole_file
terminus). Needs **modular verification** (`#@ verify_module` worsens it per prior measurement),
not a timelimit bump. This is the wall that keeps the file RED even after 7a.

### 7c — Audit the 3 illusory-verified methods
Once the file can whole-file-prove (7a + 7b), re-verify the ~3 contracted-and-NOT-trusted methods
actually discharge; if any don't, they were a latent gate hole — record + fix.

**Payoff of 7 (all parts):** unblocks CIE (`_callee_implicit_exceptions`, sound-in-isolation) +
the whole ~17-stub Module6_WhyMLTranspiler.py file, AND closes the soundness gap.

**Order within 7:** 7a (ready, byte-inert) → 7b (review-gated modular verification) → 7c (audit).

---

## Dependencies & sequencing summary
- **7a** — standalone, byte-inert, ready; also the soundness prerequisite. Do first.
- **1** — foundational; **2, 4** depend on it (construction/write op). Highest leverage.
- **2** — depends on 1 for the rewriter half; the reader half (typed accessors) is independent.
- **3** — independent; high byte-diff risk (gate carefully).
- **4** — depends on 1.
- **5** — independent; mirror-sync tooling.
- **6** — independent; highest byte-diff risk, lowest payoff; do last.
- **7b/7c** — after 7a; review-gated (modular verification + audit).

Each lever ends BROKEN (its cluster converts, count strictly down, ledger 3, byte-diff-0/M1) or
CERTIFIED-BOUNDARY (spike refutes → recorded). Nothing lands without the three-L-plane gate.
