# M1 `size`-rename — structural project to unblock the `@mutable_state`+pyval reader cluster

*Self-contained project plan, 2026-07-10. This is NOT a squeeze-loop increment — it is a deliberate,
one-time **global rename with a sanctioned corpus baseline reset**, because the fix is not byte-diff-0
(measured). Scoped per the reader-census findings (`getting-better/reader-census-2026-07-10.md`): the
flat-`Dict[str,str]` reader cluster is blocked on the `@mutable_state`+pyval `size` two-theory collision;
M1 is the unblocker. The 09-2223 M1 spike proved the rename type-checks + discharges (Z3) + is
cert-invariant; this plan is the emitter build + the corpus re-baseline.*

## 1. The collision (measured)
When a mirror module is `@mutable_state` (pulls the emit_ir ADT) AND also pulls the pyval theory (via a
generic-fold recognizer, or an emit_ir-reflection reader that also does string-map work), TWO WhyML
symbols named `size` land in one scope:
- `preamble.py:2719` — `function size (v: pyval) : int` (pyval measure; lemmas `size_pos`,
  `size_list_nonneg`, `size_dict_nonneg`, `size_dict_mem`).
- `preamble.py:3327` — `let rec function size (e: emit_ir) : int` (emit_ir structural measure; used in
  `variant { size <emit_ir-param> }`, `functions.py:1330`).
→ Why3: *"Symbol size is already defined in the current scope"*. This blocks converting any reader that
needs BOTH `@mutable_state` (getattr-self-field-`.get`, emit_ir reflection) AND non-emit_ir string-map
typing — e.g. `_call_return_whyml_type` branch 3 (`getattr(self,"_field",{}).get(obj) or …`).

## 2. Why it is NOT byte-diff-0 (the reason this is a project, not an increment)
Both `size` symbols are **corpus-present**: pyval `size` in **2** corpus programs (0882, 0883), emit_ir
`size` in **15** (0746–0751, 0774, 0776, 0878, 0881, …). Renaming either changes those programs' emitted
WhyML → byte-diff ≠ 0. There is no byte-inert rename. Hence the sanctioned baseline reset (§4).

## 3. The rename (choose the smaller blast radius: pyval → `pv_size`)
Rename the **pyval** `size` → `pv_size` (2 corpus programs touched, vs 15 for emit_ir). Sites, all in
`src/pycsl/`:
- `preamble.py:2719` decl `function size (v: pyval)` → `pv_size`; its lemmas (`size_pos` →
  `pv_size_pos`, etc.) and every in-theory reference (`pydict`/`sdict` theories that call the pyval
  measure).
- The `variant { size <param> }` emission (`functions.py:1330` and any peer): emit `pv_size` when the
  variant param is **pyval**-typed, keep `size` when **emit_ir**-typed. (Today both emit bare `size`; the
  choice must become type-directed.)
- Any hand-written `.mlw` fixtures / self-annotate mirrors that reference the pyval `size` by name.
- grep the whole tree for `\bsize\b` in pyval context; a partial rename fails Why3 closed (not silent).

## 4. Sanctioned baseline reset + full re-proof (the protocol)
The rename is **semantics-preserving** (pure symbol rename), so the new byte output is the new truth:
1. Apply the rename; emit the whole 756-corpus.
2. `diff` old vs new baseline: the ONLY changes must be `size`→`pv_size` on pyval lines in the pyval-using
   programs (0882/0883 + any pyval-variant program). ANY other diff = a bug in the rename (over/under-reach)
   → fix before proceeding. This diff-review IS the correctness gate (a rename cannot change anything else).
3. **RE-PROVE every corpus program** (not just re-emit) — each must stay `Valid`. A rename that broke a
   proof would mean an incomplete/incorrect rename. This is the load-bearing verification (the byte-diff-0
   gate is replaced by "byte-diff = exactly-the-rename ∧ all-still-prove").
4. Re-prove the self-annotation suite (`bin/run-self-annotation-suite.sh`).
5. Adopt the new corpus `.mlw` as the baseline (the reference fixtures that are committed); document the
   reset in a commit that touches ONLY the rename + the regenerated baselines.

## 5. Cert invariance — ledger STAYS 3 (the coupling rule, §10.5)
The Rocq/Lean certificates define their OWN `size` (`def size : PyVal → Nat` in `Phase2c_PyValDict.v` /
`PyValDict.lean`), independent of the emitted WhyML measure NAME. Renaming the WhyML `size`→`pv_size`
changes **no** `.v`/`.lean` proposition → `Print Assumptions` / `#print axioms` unchanged **by
construction**, no recompile, ledger = 3. VERIFY this explicitly after the rename (audit the 3-axiom
ledger) — it is the non-negotiable invariant. (09-2223 M1 spike already confirmed this on a hand `.mlw`.)

## 6. Payoff scope (HONEST — not all 85 Dict-readers)
M1 unblocks the subset of readers that need `@mutable_state` + non-emit_ir string-map typing SIMULTANEOUSLY
— the flat-`Dict[str,str]` cluster (`_call_return_whyml_type`, `_field_type_for`, `_callable_tag_to_whyml`,
…) once their OTHER recognizers (A3 rpartition, A4 option-return, U union-return, getattr-field,
string-`or`-chain, nested-dict) also land (the M2 plan, `m2-reader-emitter-build.md`). It does NOT convert
the generic-`Any`-tree-walker readers (§10.3 hard class — by-ref-set mutation, unbounded heap walks); those
stay leave-trusted regardless. Estimate the reachable subset by a fresh whole-body census AFTER M1, before
committing to the M2 recognizers. Value: the ~4-marker flat cluster + a reusable path, NOT 85.

## 7. Order & risks
`rename pyval size→pv_size (emitter) → emit-diff-review (exactly-the-rename) → full-corpus re-proof →
self-annotate re-proof → ledger-3 audit → adopt baseline (one commit) → THEN resume the M2 recognizer
build on the now-unblocked cluster`.
- **Risk 1 (incomplete rename):** a missed pyval-`size` reference → Why3 type error (fails closed, not
  silent) → caught at re-proof. Mitigate: grep-exhaustive, type-directed variant emission.
- **Risk 2 (baseline-reset scope creep):** the emit-diff MUST be exactly the rename; any other change means
  the rename touched semantics → STOP. The diff-review is the guard replacing byte-diff-0.
- **Risk 3 (payoff shortfall):** if the post-M1 census shows the reachable cluster is <3 markers, M1 is not
  worth it — run that census as the go/no-go BEFORE the M2 recognizer build (measure-before-build).
- **Non-goal:** M1 does not touch the cert `size`, the ledger, or the emit_ir measure. pyval-only rename.
