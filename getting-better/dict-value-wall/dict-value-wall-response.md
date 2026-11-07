# Independent review of `dict-value-wall.md`

**Reviewer:** independent (Claude Fable 5.1), 2026-10-20. Inputs: the report
`getting-better/dict-value-wall/dict-value-wall.md` (main `d5ef5b08`, branch `ghost-assign-bc6`),
the main tree `/home/fabrice/git/pycsl`, the land27 worktree `/home/fabrice/git/pycsl-land27`
(`6227161c`), Why3 1.8.2 with Alt-Ergo 2.6.3 and Z3 4.13.3. No driver logs, backlog, transcripts
or other agents' notes were read. Every oracle run below went through
`scratchpad/heavy/heavy.sh`; spike files and raw prover outputs are in
`getting-better/dict-value-wall/review-spikes/` (`*.out` files are the verbatim `why3 prove`
output).

---

## 0. Verdict in one paragraph

The report's measurements are accurate where I could re-run them (census counts, marker counts,
the `_tag_of_value` lowering, the `Dict[str, Any]` int-erasure, the present-key hval read failure
and its fix by a key-equality spec, step counts to the digit). Its overall verdict — "a modelling
choice, not a fundamental limit; no measured combination converts more than ~2–4 markers" — is
**confirmed with two carve-outs**: (i) the hval model is weaker than the report says even after
R2a under Alt-Ergo, because Alt-Ergo cannot separate two distinct string literals (a two-key
read times out; only Z3 proves it), so every hval witness is Z3-dependent; (ii) "modelling choice"
is correct for the value layer, but the cost that actually binds is the **whole-file re-proof
bill** (38 min to hours per mover), which is a tooling limit of the L-plane, not of the model, and
the report under-weights it in its route costing. On the ledger question: **a spec on
`hpairs_key_eq` cannot be made definitional** in Why3 1.8.2 (five variants refused, measured);
the only forms available are a `val function … ensures { result <-> a = b }` (which Why3 itself
encodes as `axiom hpairs_key_eq'spec [@W:non_conservative_extension:N]` in the task — I printed
it) or the stdlib's own `String.(=)`, which carries the identical spec. It is realizable (Rocq
`string_dec`), satisfiable (Z3 returns `sat` on `false` under it), has an exact precedent
(`str_eq_op`), and leaves the 3-kernel-axiom ledger untouched; but the report's phrase "NOT an
axiom" is imprecise and should read "a realizable Why3 `val` spec, not a kernel axiom".

---

## 1. Oracle runs (all cited by file; raw outputs kept)

Common environment: `export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0`,
`H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh`, `L=/home/fabrice/git/pycsl-land27`,
`R=/home/fabrice/git/pycsl`. Spike dir `S=getting-better/dict-value-wall/review-spikes`.

| # | command | file | result (one line) |
|---|---|---|---|
| O1 | `$H why3 prove -P alt-ergo -t 5 keq_a_nospec.mlw` | `S/keq_a_nospec.mlw` (land27 hval carrier + `pairs_get` + `hval_truthy` verbatim, `val function hpairs_key_eq` with NO spec) | `empty_read` Valid (6 steps); `hit_read`, `hit_twin`, `miss_read`, `miss_twin`, `truthy_hit`, `truthy_twin` all **Timeout** |
| O2 | same, `-P z3` | same | `empty_read` Valid; `hit_read`/`miss_read` Timeout; `truthy_hit` **Unknown (sat)**, `truthy_twin` Unknown (sat) |
| O3 | `$H why3 prove -P alt-ergo -t 5 keq_b_spec.mlw` | `S/keq_b_spec.mlw` (= O1 + `ensures { result <-> a = b }`) | `hit_read` **Valid (26 steps)**; `hit_twin` Timeout; **`miss_read` Timeout**; `truthy_hit` Timeout; `truthy_twin` Timeout |
| O4 | same, `-P z3` | same | `hit_read` Valid; `hit_twin` Timeout; **`miss_read` Valid (0.59 s)**; `miss_twin` Timeout; `truthy_hit` Valid; `truthy_twin` **Unknown (sat)** |
| O5 | `$H why3 prove -D why3 keq_b_spec.mlw` | same | printed task contains `function hpairs_key_eq string string : bool` and `axiom hpairs_key_eq'spec [@W:non_conservative_extension:N] : forall a b. hpairs_key_eq a b = True <-> a = b` |
| O6 | `$H why3 prove --type-only` on `keq_c_def.mlw`, `keq_d_pred.mlw`, `keq_e_stdlib.mlw`, `keq_f_pure.mlw`, `keq_g_predfirst.mlw`, `keq_h_stringeq.mlw`, `keq_i_funfirst.mlw`, `keq_j_ifeq.mlw`, `keq_k_ghost.mlw`, `keq_l_iffml.mlw` | definitional variants of `hpairs_key_eq` | **all refused** (see §3 for each message) |
| O7 | `$H why3 prove -P alt-ergo -t 5 keq_m_spec_string.mlw` | `S/keq_m_spec_string.mlw` (= O3 + `use string.String`) | `hit_read` Valid; `miss_read`, `truthy_hit` still Timeout (stdlib in scope does not give Alt-Ergo literal distinctness) |
| O8 | `$H why3 prove -P z3 -t 5 keq_n_absurd.mlw` | `S/keq_n_absurd.mlw` (= O3 + `goal contradiction_probe: false`, `keyeq_refl`, `keyeq_sym`) | `contradiction_probe` **Unknown (sat)** (the spec'd theory has a model); `keyeq_refl` Valid; `keyeq_sym` Valid |
| O9 | `$H $L/.venv/bin/python $L/src/pycsl/pycsl.py hit_probe.py --import-path $L/src/pycsl --no-proof --keep-mlw` | `S/emit_land27/hit_probe.py` (Appendix A + `second_key_hit` {"answer","time"} + `top_twin`) | L3-tc ✓; emitted `.mlw` line 5 `use string.String`, line 23 `val function hpairs_key_eq (a b: string) : bool` (no spec); `top_hit` body exactly as the report's Appendix A |
| O10 | `$H why3 prove -P alt-ergo -t 5 hit_probe.mlw` / `-P z3` | `S/emit_land27/hit_probe.mlw` (as emitted) | `answer_hit`, `second_key_hit`, `top_hit`, `top_twin` all **Timeout** in both provers |
| O11 | same on `hit_probe_spec.mlw` (one `sed` line: the `ensures`) | `S/emit_land27/hit_probe_spec.mlw` | alt-ergo: `answer_hit` **Valid (975 steps)**, `top_hit` **Valid (116 steps)**, `second_key_hit` **Timeout**, `top_twin` Timeout. z3: `top_hit` Valid, `second_key_hit` **Valid**, `answer_hit` Timeout, `top_twin` Timeout |
| O12 | `$H $R/.venv/bin/python $R/src/pycsl/pycsl.py anydict_truthy.py … --no-proof --keep-mlw` | `S/emit_main/anydict_truthy.py` (`rec: Dict[str, Any]`) | emitted `let function any_truthy (py_rec: map string (option int)) : int` — int-erased |
| O13 | same on `exprir_probe.py` | `S/emit_main/exprir_probe.py` (`node: "ExprIR"`) | emitted `let function ir_kind (node: emit_ir)`, `.get("type") == "Var"` → `is_var node`, `node["name"]` → `name_of node` |
| O14 | same through land27 on `harr_for_probe.py`, `hval_in_probe.py`, `hval_keys_probe.py` | `S/emit_land27/` | `for r in (rec.get("records") or [])`: **L3-tc ✗** (`has type hval, expected int`); `"loc" in inner`: **L3-tc ✗**; `rec.keys()` on the top-level dict: **L3-tc ✓**, lowered to an abstract `iter_length (rec_keys_0 ())` loop |
| O15 | `git archive b9dc767e … \| tar -x; python3 -I census.py; python3 -I cluster.py` (scratchpad) | report's own scripts | `423 399 423`; `N 19 13 4 2 / P 30 7 3 1 / G 14 5 2 2 / J 4 4 3 3 / M 12 3 1 0 / X 18 9 6 3` — matches §2.2 exactly |
| O16 | `grep -rF '#@ \trusted' … \| wc -l` and `grep -rhE '^\s*#@ \\trusted'` on main and land27 | mirrors | 451 / 423 (main), 449 / 421 (land27) — confirmed |
| O17 | `ast` census over the land27 mirror (inline script, O16's command block) | mirror | verified-with-`Dict[str, Any]`/`dict` = **183** (per-file 84 / 24 / 19, exact match); IR-tag and PyVal counts depend on the matching rule (mine: 217 / 11 verified, 38 / 0 trusted vs the report's 184 / 10, 71 / 1) — not a disagreement, an unstated rule |

A note on O10/O11 versus the report's Appendix A: the step counts 975 and 116 reproduce to the digit,
and the z3 Timeout on `answer_hit` reproduces. The report is accurate here.

---

## 2. Claim-by-claim check of the facts

| claim (report §) | status | evidence |
|---|---|---|
| §1 counts 451/449 and 423/421 | CONFIRMED | O16 |
| §1 axiom ledger = 3 kernel-axiom allowlist | CONFIRMED (the allowlist is Rocq propext/funext(+dep) and Lean `propext`/`Classical.choice`/`Quot.sound`, `src/pycsl/proof_axiom_allowlist.py:19-40`) | read |
| §2.1 census numbers and §2.2 cluster table | CONFIRMED | O15 |
| §3.1 bare `ExprIR` param lowers `.get("type")`→discriminant, `["name"]`→`name_of` (the 20260719 Claim-A refutation) | CONFIRMED | O13; `git show 3bd6e1b9` shows the retype was the only modelling change |
| §3.2 main has `val hpairs_key_eq` (`preamble.py:8046`), land27 `val function` (`:8051`) | CONFIRMED | grep |
| §3.2 "present-key reads unprovable on land27" | CONFIRMED | O1, O2, O10 |
| §3.2 the spec fixes `answer_hit`/`top_hit` (alt-ergo 975/116 steps), twin stays unproved | CONFIRMED | O11 |
| §3.2 "`Phase2f` uses `string_dec`"; Lean `pairsGet` uses `if k = k'` | CONFIRMED (`Phase2f_PyVal.v:214-217`; `PyVal.lean:160-163`) | read |
| §3.2 "Why3 has no native program string `=`" (preamble comment, quoted) | **REFUTED** for Why3 1.8.2: `stdlib/string.mlw:487-488` declares `val (=) (x y: string) : bool ensures { result <-> x = y }`, and every emitted file already does `use string.String` (O9 line 5). It is not usable inside a `let function` body (O6, `keq_h`), so the practical conclusion stands, but the stated reason is wrong |
| §3.2 the spec "is NOT an axiom" (via `generic_fold.py:16379`) | **IMPRECISE**: Why3 encodes it as `axiom hpairs_key_eq'spec` in the task (O5). It is not a *kernel* axiom and the ledger's definition does not count it; see §3 |
| §3.2 "`.keys()` not covered" | CARVE-OUT: `.keys()` on the top-level `Dict[str, PyVal]` (a `map string (option hval)`) type-checks and lowers to an abstract over-approximated iterator (O14); it is `.keys()` on a nested `HMap` that is uncovered |
| §3.2 "for-loop over `HArr`" and "`"k" in <hval local>`" not covered | CONFIRMED (both L3-tc ✗, O14) |
| §3.5 `Dict[str, Any]` → `map string (option int)` | CONFIRMED | O12 |
| §3.5 "`Any` returns None" in `_m5_get_dict_value_type`; `PyVal` returns `"hval"` | CONFIRMED (`Module5_IREmitter.py:5752-5753`) | read |
| §3.5 183 verified `Dict`-signature functions, 84/24/19 per file | CONFIRMED exactly | O17 |
| §3.3 147 recognizers | CONFIRMED (`grep -c '^def recognize'` = 147) | grep |
| §4.4 original pyval oracle | the cert's oracle `getting-better/pyval-oracle.mlw` used `PMap (map string (option pyval))` with logic `=` through `Map.get` and had **no key-equality primitive at all**; the opaque `hpairs_key_eq` arrived with the R3 assoc-list carrier. So "the WhyML model is strictly weaker than the certificate" is a consequence of R3, not of the original design. Worth recording | read |
| §5 R5 counts 22 / 22 / 1 / 1 `assigns` clauses | CONFIRMED | grep |
| §5 R4 `check-shadowed-selfcalls` ratchet 14 | CONFIRMED (`bin/check-shadowed-selfcalls.py:42 BASELINE = 14`) | read |
| §6.6 `_string_set_locals` not in land27 `src/` | CONFIRMED (0 hits) | grep |
| §1 "61 planes" | NOT CHECKED (the script's `PLANES=(` array is not trivially countable; irrelevant to the verdict) | — |

**One new fact the report does not have** (O3/O4/O11): even with the spec, **Alt-Ergo times out on
any read that must pass over a non-matching binding** (`miss_read`: `pairs_get (PCons "b" _ (PCons
"a" v PNil)) "a"`, and the emitted `second_key_hit` with keys `"answer"` and `"time"`), while Z3
proves them in well under a second. Alt-Ergo has no string theory and Why3's driver gives it no
literal-distinctness facts (`use string.String` in scope does not help, O7). Since PyCSL runs
`_DEFAULT_PROVERS = ["Alt-Ergo,2.6.3,", "Z3,4.13.3,"]` best-of-N (`pycsl.py:7195`), the tool
will still prove these, but every multi-key hval witness is Z3-only, and Alt-Ergo-only
twin-failures tell you nothing about the model. R2a's make-or-break must be stated as "Z3 Valid,
twin non-Valid in BOTH provers", not "alt-ergo Valid".

---

## 3. Gate R question 1: can `hpairs_key_eq` get a spec without a new axiom?

**Short answer.** Not as a definition. Why3 1.8.2 refuses every non-ghost definitional form
(O6, messages verbatim):

| variant | body | Why3 answer |
|---|---|---|
| `keq_c_def` | `let function … : bool = a = b` (with `use int.Int` before) | `This expression has type string, but is expected to have type int` (program `=` resolves to `Int.(=)`) |
| `keq_i_funfirst` | same, declared before `use int.Int` | `Logical symbol (=) is used in a non-ghost context` |
| `keq_d_pred` / `keq_g_predfirst` | `let predicate … = a = b` | same two messages respectively |
| `keq_l_iffml` | `let function … = if a = b then true else false` | `Logical symbol (=) is used in a non-ghost context` |
| `keq_j_ifeq` | same, after `use string.String` | `expected to have type int` |
| `keq_e_stdlib` / `keq_h_stringeq` | `let function … = String.(=) a b` | `Logical symbol (=) is used in a non-ghost context` (a `let function` body may not call a program `val`) |
| `keq_f_pure` | `let function … = pure { a = b }` | `Function hpairs_key_eq must be explicitly marked ghost` |
| `keq_k_ghost` | `let ghost function … = pure { a = b }` | accepted for itself, but then `Function pairs_get must be explicitly marked ghost` — the whole reader chain becomes ghost and the emitter's program-position reads (`match pairs_get m "answer" with …` inside `let v_or = …`, O9 line 79) would no longer type-check |

The root cause is Why3's design: polymorphic `=` is a logic symbol, string equality in program
code must come from a `val`, and a `let function` must be both pure logic and executable program.
So the two legal shapes are exactly the two the report names, and both are specs on a `val`:

1. `val function hpairs_key_eq (a b: string) : bool ensures { result <-> a = b }` (the report's
   R2a); Why3 prints it as `axiom hpairs_key_eq'spec` (O5).
2. The stdlib `String.(=)` — same spec, same encoding, but a plain `val` (not `val function`), so
   it cannot be called from `let rec function pairs_get` at all; it does not help.

**Is (1) acceptable under the ledger?** Yes, on three grounds, each measured or cited:
* The ledger is `proof_axiom_allowlist.py`'s kernel-axiom allowlist for Rocq/Lean certificates
  (the reverify path). A Why3 `val` spec does not enter that path. Ledger stays 3.
* It is realizable: the certificate's `pairs_get` uses `string_dec` (`Phase2f_PyVal.v:217`) and
  Lean's `if k = k'` (`PyVal.lean:163`), i.e. the certified object IS decidable equality. The spec
  makes the WhyML *equal* to the certificate, not stronger. It is satisfiable: `false` is
  `Unknown (sat)` under it (O8), and reflexivity/symmetry follow (O8).
* Precedents of the identical form already exist in the emitter: `str_eq_op`
  (`functions.py:5444-5445`), `str_contains_op` (`expressions.py:1876-1877`), the generic-fold
  `…__streq`, and the stdlib's own `String.(=)`.

**But the vocabulary must be fixed.** `generic_fold.py:16379`'s "NOT an axiom" and the report's
echo are false at the Why3 level — Why3 literally tags it `axiom … [@W:non_conservative_extension:N]`.
The honest sentence is: "a realizable spec on an uninterpreted `val function`, encoded by Why3 as
a task axiom, not a kernel axiom; its realizer is `string_dec` in the cited certificate". I
recommend the project keep a second, separate count of such Why3 `val`-spec assumptions (today at
least `str_eq_op`, `str_contains_op`, the stdlib `String.(=)`, `any_map`'s absence of spec, and
R2a) so that "ledger 3" is not read as "zero assumed facts in the SMT context". The stdlib
`string.String` module also brings `axiom extensionality` into every emitted task
(`stdlib/string.mlw:439-440`) — that is Why3's, not the project's, but it is in the TCB.

---

## 4. Route-by-route

### R1 — retype `Dict[str, Any]` / `int` → `ExprIR` / `StmtIR` / `PyVal`

**Agree, with the cost re-weighted.** The mechanism is confirmed (O12 vs O13: the same `.get` on
the same key lowers to `Map.get py_rec … : int` or to `is_var`/`name_of` purely on the annotation).
What the report under-weights: the only landed instance (`3bd6e1b9`) moved two mirror files and
its own commit message says "WHOLE-FILE PROOF OWED … If either has a non-Valid goal, REVERT". So
R1's true unit cost is not "cheap per signature" (§0) but "one whole-file proof per mover, 38 min
to hours each, and the 183-function ripple surface makes multi-file movers the norm". That is
what makes the measured yield 1. The soundness caveat (3 of 19 N markers are not IR) is correct
and important: a wrong retype is not caught by fidelity (annotations are ignored at runtime) or
by L3-tc; only a twin would catch it. **Carve-out:** the report should say explicitly that the
retype of a NON-IR value to `ExprIR` is a *false model* that proves things (the value becomes a
projector-readable ADT it never was), i.e. R1 has a soundness failure mode, not just a cost.

### R2a — pin key equality

**Agree; it is the cheapest, most necessary step, and it is prerequisite to every hval claim.**
Measured: O3/O4/O11. Three corrections:
1. Make-or-break must be run on Z3 as well as Alt-Ergo (the Alt-Ergo literal-distinctness gap,
   §2). A two-key witness (e.g. `second_key_hit`) must be added to the gate; today's witnesses
   3140/3160 read single-binding records and would not detect a regression to Alt-Ergo-only.
2. The twin outcome to require is "non-Valid in both provers"; prefer twins that give
   `Unknown (sat)` (`truthy_twin`, O4) over Timeouts, because a sat answer is a real counter-model
   and a Timeout is not.
3. Wording (§3 above).
Cost: one preamble line, the ~30 corpus + 21 mirror movers the report lists are line-only diffs;
re-proof of the FAIL twins is the real bill. Unlocks 0 markers alone, as stated — but every hval
conversion already landed (`_record_answer`, `_collect_typevar_registry`, …) currently proves its
`ensures True` contract over reads that cannot be reduced; R2a is what makes those bodies' future
*non-trivial* contracts possible, so its value is not zero, it is "every later hval marker".

### R2b — for-loop over `HArr`, `in`, `.keys()`

**Agree on the gap (O14 confirms two of three), carve out `.keys()`** (already accepted at the
top level, abstractly). The proposed lowering (index loop over `hval_list_len`/`hval_list_nth`) is
definitional and axiom-free; note that `Phase2f_PyVal.v` contains **no** `hval_list_len`/`nth`
statements (grep empty), so the "small lemma" in the route table is currently absent, not small.
Under the ch28 projector rule that is acceptable (definitional functions over certified
constructors). Soundness risk the report misses: an index loop over `hval_list_nth` whose `HNil`
arm returns `HInt 0` (preamble `hval_list_nth`) is total by a *sentinel*; a loop that over-runs
reads `HInt 0` rather than failing, so the loop bound must be exactly `hval_list_len`, and a
witness must check the element at the last index. Unlocks alone: 0, agreed.

### R2c — stores into a nested hval

**Agree that it is the one memory-model question, and refine the carve-out.** Two shapes are
conflated:
* **Local tree** (`_collect_generic_decls`: `generics[self_type]["methods"].append(func)` on a
  dict built in the same function, `monomorphize.py:138`): no alias can exist outside the
  function, so a functional write-back is faithful without any precondition. This sub-case is a
  value-model question after all and is cheaper than the report's R2c.
* **Caller's tree** (`_rewrite_annotations`: `func["symbol_table"] = new_st` on elements of
  `ir_data["functions"]`, `monomorphize.py:667-675`): the report is right that this needs a
  no-alias statement the fixed `requires True` shape cannot express. Note the function returns
  `None` and its whole effect is the mutation; under `ensures True` + functional write-back the
  conversion would be *vacuous* unless the frame names the root. Treat as boundary until the
  contract shape allows an assigns-through-path clause.

### R2d — hashable hval keys

Agree: one beneficiary (`_merge_records_best_of_n`, `pycsl.py:6252-6274`), which also needs
tuple keys `(k, nseen)` and `_record_key` — low value.

### R3 — per-node-kind payload for `value`

**Agree with the design constraint and sharpen the soundness risk.** Projector-only routing
needs no cert change — true, and O13 shows the current table in action. But the report's own
measured failure mode (a constant `IrOther ""` read under a wrong kind lets "branch never taken"
prove) means dominator-keyed routing must be **fail-closed**: when no `is_K`/`kind_of = "K"`
test dominates the read, refuse (L3 error), do not fall back to `svalue_of`. Answer to Gate R Q4:
dominator routing is sound only if (a) the dominance is computed on the emitted WhyML control
flow, not on Python syntax (an `and`-chain like `_emit_bitwise_or_power`'s
`left_ir.get("type") == "Number" and … isinstance(left_ir.get("value"), int)` is short-circuit,
so the second read *is* dominated — fine — but an `or` is not), and (b) the routed projector's
default arm is never reachable under the dominating test (`num_of` returns `0` on non-`IrNum`;
under `is_number` the node IS `IrNum`/`IrNumF`/`IrBoolC` — the `IrNumF` case would read `0`
for a float Number, a *false* constant; so `is_number` must be split, or `num_of` must be
defined over all three). A typed refinement of `emit_ir` is not needed; a per-kind twin per
routed read is. Unlocks alone: 0, agreed; `_emit_bitwise_or_power` additionally reads
`self._BITWISE_FOLD_OPS[op_char](…)` — a dict of *callables* — which is not on any route list and
makes that marker further than the report says.

### R4 — cross-mixin self-method typing

**Agree, 0 unlocks; the soundness risk is real and correctly identified.** Importing a sibling's
declared signature imports its `assigns`; the underdeclaration plane must be green for that
sibling first. Cheap (a 6-line partial exists per the report), but it only advances markers that
each have ≥3 more blockers. Low priority.

### R5 — declare missing self-map fields

**Agree it is expensive, and add: it is a frame-model change, not a value-model change.** The
22/22/1/1 `assigns` counts are confirmed. The HOLE-T delta is unmeasured, and f5/g5 say the only
move that satisfies both ratchets switches on the ceiling-0 arm for every clause that omits the
field. Until the delta is measured, R5 is unpriced. Lowest expected yield per cost of the six.

### R6 — leave cluster G trusted (CERTIFIED-BOUNDARY)

**Agree, with one condition.** The ground is sound (a `pyval -> pyval` rebuild has no template
and would need a new certified fold plus a cross-model bridge). The condition: the report's ch26
suspicion (a) — three trusted bodies with `assigns \nothing` that append to a list parameter —
must be closed before G is declared a boundary, because "leaving them trusted is an assumption,
not a hole, provided their declared frames are honest" is exactly the proviso those three
violate. Declare the boundary after `check-trusted-reasons`/underdeclaration planes confirm the
G frames.

---

## 5. The overall verdict

**"A modelling choice, not a fundamental limit" — AGREE**, with the precise statement: the value
layer is a choice (O12 vs O13 vs O9 are the same Python under three annotations), the
certificates for all three models are axiom-free, and the one genuinely non-value question is the
caller-tree in-place store (R2c, caller's-tree shape only).

**"No measured combination converts more than ~2–4 markers" — AGREE, and I could not beat it.**
Gate R Q3 asks for a marker that converts with at most two of {R1, R2a, R2b, R3, R4, R5}. I read
the live bodies of the cheapest-looking candidates on land27:
* `_collect_generic_decls` (P, "DICT-only complete"): needs R1 + R2b (two `for` over
  `ir_data.get(...)`) + nested dict literal with an hval payload + hval structural `in`
  (`func not in generics[...]["methods"]`, an hval-equality on whole records, not on any route) +
  a local nested store (R2c-local). ≥4.
* `_rewrite_annotations`: R1 + R2b (`.items()` over an hval `HMap`) + R2c (caller tree) + a
  callee (`_rewrite_annotation_str`, `re`). ≥3 and one is the boundary.
* `_residual_selectors_from_records` (J): R1 + R2b + an f-string over two hvals (`f"{fn}:{ln}"`,
  lossy under `hstr_of`) + `Set[str]` membership. ≥3.
* `_emit_bitwise_or_power` (N): R1 + R3 + a dict of callables + `str()` of a folded int + `try`.
  ≥4.
So the answer to Q3 is **no marker found**; the bound stands. The reason is structural: the
value-model gaps are the FIRST blocker because the type checker finds them first, and the chains
behind them are mixed (loops, sets, f-strings, callables, in-place stores). The honest framing is
that the dict wall is a *gate*, not the *wall*: every route here buys entry to a chain, not a
conversion.

---

## 6. Ranking by expected markers per unit cost

| rank | route | expected markers | cost | why |
|---|---|---|---|---|
| 1 | **R2a** key-equality spec | 0 direct; unblocks every future hval contract (P 30, J 4 in-chain) | one line + twin re-proofs (line-only movers) | measured O3/O4/O11; prerequisite for any non-vacuous hval witness; no cert change; ledger 3 |
| 2 | **R2b** `HArr` index loop + `in` on hval | 0 direct; advances P/J | definitional emitter work, a few witnesses, no cert | O14 shows the exact type errors; projector rule covers it |
| 3 | **R2c-local** (nested store into a *locally built* dict) | opens `_collect_generic_decls`-shaped P readers | emitter + witnesses | my carve-out of R2c; no alias question |
| 4 | **R1** retype, applied one *leaf* at a time | ≤1 per attempt (measured 1 in 19) | one whole-file proof per mover (38 min–hours) | the binding constraint is the L-plane proof bill, not the model |
| 5 | **R3** fail-closed per-kind `value` routing | 0 direct, 3 advanced | small emitter change + one twin per kind | sound only fail-closed and with `IrNumF` handled |
| 6 | **R4** cross-mixin typing | 0 direct, 3 advanced | small, but imports frames | gate on underdeclaration plane |
| 7 | **R6** declare G boundary | — | zero | do it after closing suspicion (a) |
| 8 | **R2c-caller** (caller-tree store) | `_rewrite_annotations` and the P writers | needs a contract-shape change | boundary until assigns-through-path exists |
| 9 | **R5** field declarations | 0 direct, 4 advanced | unmeasured HOLE-T delta; `types.py` re-proof | unpriced; measure before spending |
| — | R2d | 1 | — | skip |

---

## 7. Soundness risks, listed

1. **R1 unfaithful retype** proves false claims (a Lean JSON node retyped `ExprIR` becomes
   projector-readable). Not caught by fidelity or L3-tc. Require a twin per retype that reads a
   key the real value does not have.
2. **R2a vocabulary**: a `val function` spec is a Why3 task axiom (O5). Keep the kernel ledger at
   3 and add a visible count of Why3 `val`-spec assumptions; never describe them as "no axiom".
3. **R2a Alt-Ergo-only evidence** is weak: Alt-Ergo cannot separate literals, so an Alt-Ergo
   Timeout on a twin may be a prover gap rather than model strength. Twins must be checked in Z3
   (prefer `Unknown (sat)` outcomes).
4. **R3 wrong-kind constant reads** (report's own ch28 note a) — fail-closed routing and a per-kind
   twin; `num_of` on `IrNumF` reads `0`.
5. **R2b sentinel totality**: `hval_list_nth` returns `HInt 0` past the end; loops must be bounded
   by `hval_list_len` exactly.
6. **R4 frame import**: a sibling's under-declared `assigns` becomes the caller's false assumption.
7. **R2c caller-tree write-back** under `requires True` is faithful only with a no-alias
   precondition the contract shape cannot state; and under `ensures True` + `-> None` it is
   vacuous unless the root is in the frame.
8. **R6**: three trusted `assigns \nothing` bodies that append to a parameter (report ch26 (a)) are
   a live hole until re-declared; do not call G a boundary before that.

No route in the report adds a kernel axiom or strengthens a model beyond its certificate; R2a
*weakens the gap* between WhyML and certificate to zero. The one proposal that would exceed the
certificate is any *abstract law* version of R2b (a length-only or "some element" law over
`HArr`), which the 20260718 lesson already names as a vacuity trap — the report avoids it.

---

## 8. Factual errors, over-scoping, missed cheaper moves

* **Error (quoted comment):** "Why3 has no native program string `=`" — false for Why3 1.8.2
  (`string.mlw:487`), and the emitted preamble already `use string.String`. Harmless to the
  conclusion, wrong as a reason.
* **Error (vocabulary):** "NOT an axiom" for a `val function … ensures` — Why3 emits
  `axiom …'spec`. Realizable, not kernel, precedent-backed; still, say so.
* **Over-scoping:** §0 calls R1 "legal and cheap per signature" — the measured unit is a
  whole-file proof per mover, and the only instance landed is still OWED. R1 is the most expensive
  route per attempt, not the cheapest.
* **Over-scoping:** `.keys()` listed as uncovered — covered (abstractly) at the top-level map
  (O14).
* **Under-scoping:** R2c conflates local-tree and caller-tree stores; the local case is a value
  question and cheaper.
* **Missing measurement the report should add:** the Alt-Ergo literal-distinctness gap (O3/O11
  `miss_read`/`second_key_hit`). It changes what a valid hval witness looks like.
* **Missed cheaper framing:** since the certificate's own oracle used a `map string (option pyval)`
  carrier (no key primitive), the project could document that R3's assoc list is where the
  opacity entered, and that R2a restores parity rather than adding strength. That makes R2a a
  *repair*, which is the strongest justification available for it.
* **Mirror census:** the `Dict` count (183) reproduces exactly; the IR-tag (184) and PyVal (10)
  counts depend on an unstated matching rule (my `ast` rule gives 217 and 11). State the rule.

---

## 9. Answers to Gate R, compact

1. §3.2: **CONFIRMED** on both halves (present-key reads unprovable; the spec fixes them and the
   twins do not prove). Acceptable under the 3-axiom ledger on a par with `str_eq_op`, provided it
   is described as a realizable Why3 `val` spec (task axiom) and its make-or-break is run in Z3
   with a two-key witness.
2. §5: **CONFIRMED** modelling choice. R2c is the only memory-model part, and only its
   caller-tree half; the local-tree half is a value question.
3. Ranking in §6. **No** marker found that converts with ≤2 of the listed routes; four candidates
   were read and each needs ≥3 (one of them a boundary).
4. R3: dominator-keyed routing is sound in the current architecture **if** fail-closed, computed on
   emitted control flow, and with `IrNumF`/`IrBoolC` handled; no typed refinement of `emit_ir` is
   required.
5. G: declare CERTIFIED-BOUNDARY **after** the three `assigns \nothing`-but-appends frames are
   corrected; not before.

---

## Appendix — spike inventory (`getting-better/dict-value-wall/review-spikes/`)

* `keq_a_nospec.mlw`, `keq_b_spec.mlw`, `keq_m_spec_string.mlw`, `keq_n_absurd.mlw` + `*.out`
  (O1–O4, O7, O8).
* `keq_{c,d,e,f,g,h,i,j,k,l}_*.mlw` — the refused definitional variants (O6).
* `emit_land27/hit_probe.py`, `hit_probe.mlw` (as emitted by land27), `hit_probe_spec.mlw`
  (+ one `ensures` line), `*.out` (O9–O11); `harr_for_probe.py`, `hval_in_probe.py`,
  `hval_keys_probe.py` and their `.mlw` where emitted (O14).
* `emit_main/anydict_truthy.py`, `exprir_probe.py` and their `.mlw` (O12, O13).
