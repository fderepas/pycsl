# plan-review.md — adversarial review of the tier-3 TCB plan + phase-3 status

Independent, adversarial review of `triage-ranked-tcb-tier3-phase3.md` (status/postmortem) and
`triage-ranked-tcb-tier3.md` (execution plan), verified against repo ground truth on branch
`ghost-assign-bc6`, 2026-07-06. Every claim below was re-run, not trusted. Commands and their real
output are cited. Tools used: coqc 8.20.1, lake/Lean 4.31.0, why3 1.8.2, alt-ergo 2.6.2, z3 4.13.3.

**Headline verdict.** The *status doc is honest* and its *foundation claims reproduce cleanly* — the
certificate builds, the ledger holds, the spike discharges, the count is truthfully attributed. But
the *forward plan's central quantitative claim is NOT supported*: Step 1 (expr list-kinds + `size_list`)
does **not** unlock the ~34 `ir_scanner` cluster it is sold on. The "no remaining research risk, just
execution volume" framing is over-confident: the largest sub-cluster (generic `.values()` walkers) has
**no faithful typed-ADT path at all**, which is an unsolved *modeling* problem, not volume.
**Recommendation: proceed with changes (re-scope Step 1 and re-baseline the payoff projection).**

---

## Part (a) — Claim-by-claim verification

### 1. Commit chain — VERIFIED
`git log --oneline ee27b0cd~1..1a3479b4` returns exactly **9 commits**, matching the status table §2
(P0 `ee27b0cd`/`b830805f`, P1-prereq `d2479fe9`, P1-expr `8993a5b9`/`d989985f`, P3 `959f30c3`,
P4 `d4bcf2c1`, P2 `e73ec7c6`/`1a3479b4`). Descriptions match `git show`. **VERIFIED.**

Nit: the status doc §2 P1 row says "9 expr kinds (BinOp, Var, ...)" while commit `d989985f`'s subject
says "8 kinds: Var/Number/String/Subscript/Attribute/Call/MkTuple/FieldGet". The discrepancy is
BinOp (added in `8993a5b9`, the earlier commit) vs. the 8 completed in `d989985f` → 9 total. Internally
consistent, just two different counts in two places. Cosmetic.

### 2. Certificate builds + ledger holds (the make-or-break) — VERIFIED
- `src/formal-semantics/rocq`: `make clean && make -j4` → **exit 0**, `Phase2b_RecordVal.vo` produced.
- `Print Assumptions pycsl_soundness` **and** `Print Assumptions pycsl_soundness_verified` →
  exactly `{propositional_extensionality, functional_extensionality_dep}` — the two standard Coq
  axioms, no `path_get`/`RecordVal`/4th axiom. **Byte-identical to baseline claim: VERIFIED.**
- `Phase2b_RecordVal.v`: `grep Admitted|Axiom|Parameter|sorry` → none (only the word "Admitted" in a
  comment). All lemmas end `Qed.` **Axiom-free: VERIFIED.**
- `src/formal-semantics/lean`: `lake build` → **exit 0, 39/39 jobs**. `#print axioms
  pycslSoundnessVerified` → `[propext, Classical.choice, Quot.sound]` (the 3 standard kernel axioms =
  the "3-axiom ledger"), no `sorryAx`, no extension-specific axiom. `RecordVal.*` lemmas likewise only
  standard kernel axioms. **VERIFIED.**

**Caveat that qualifies the "certified" framing (see Part b, Finding 2).** Phase2b is a *conservative
side-car*, self-described at lines 24-29: it defines its **own** `val7`/`state7`/`lookup7`/`update7`
**alongside** the core `Phase2_State.val`, and *deliberately does NOT add a `VRec` constructor to the
core `val` inductive*. `pycsl_soundness` does not import Phase2b — that is *why* its assumption set is
unchanged. So "the ledger held" is true precisely *because the certificate is decoupled from the core
soundness induction*. It proves nested-record read-back/frame + a conservativity lemma (lifting base
state into `val7` agrees cell-for-cell), which is a legitimate *feasibility* proof — but it is **not**
an integration of record values into the mechanized WP soundness. The plan's own §0 coupling principle
("capability outrunning its certificate") is satisfied *in letter* (a Phase-3 file co-landed) but the
core `val` still ranges over `{VInt, VArray, VClosure}` only.

### 3. Phase-0 WhyML spike — VERIFIED
`why3 prove -P alt-ergo` and `-P z3` on `tier3_ir_node_adt_spike.mlw`:
- **All positive goals + all `'vc` termination goals Valid** on at least one prover (union of
  Alt-Ergo+Z3, project-standard best-of-N). Alt-Ergo times out on `g1_disjoint` but Z3 proves it
  (0.24s); all `size/size_list/pat_size/stmt_size` `'vc` goals Valid on both.
- **All 4 false twins stay UNPROVEN on both provers**: `g2_false_twin`, `g3_false_twin`,
  `g5_false_twin`, `g6_false_twin` → Timeout (Alt-Ergo) / Timeout-or-Unknown (Z3). Correct behavior.
- No `axiom` keyword in the file. **0 axioms: VERIFIED.**

Minor honesty gap: the spike header comment says positive goals are "Valid on Alt-Ergo+Z3"; strictly
`g1_disjoint` is Z3-only (Alt-Ergo times out). This is standard best-of-N and harmless, but the phrase
overstates Alt-Ergo coverage for one non-string goal.

### 4. expr ADT + gates (conformance 38/38, byte-diff 0, locks) — VERIFIED
- `bin/run-conformance.sh` → **"front-end conformance: 38 OK / 0 MISMATCH"**, front-end-only + IR
  conformance both pass. **VERIFIED.**
- `bin/self-annotate-mirror-check.sh` → **"all 51 mirrors are in sync"** (matches "mirror-check 51/51").
- Locks `0878.py`–`0881.py` exist under `test-suite/corpus/pycsl-reference/`. **VERIFIED.**
- `\trusted` count = **1249** (`grep -rF '\trusted' src/self-annotate/src --include='*.py' | wc -l`).
  Byte-diff 0 not independently re-run (conversions were mirror-only by construction, a sound argument).

### 5. Phase-2 "0 ADT-enabled conversions" + honest attribution — VERIFIED
`git show e73ec7c6`: the 3 de-trusted functions are `_array_coerce_arg` (pure string coercion),
`_emit_new_ghost_ref` (f-string builder), `_wrap_body_with_return_catch` (string dispatch) — all
string/f-string leaves reading no IR node, each given `requires True / ensures True / assigns
\nothing`. Count 1252→1249 exact. The status doc's characterization ("incidental non-ADT leaves, net
ADT-enabled = 0") is **truthful and correctly attributed. VERIFIED.**

Observation (not a discrepancy): these are *trivial-contract* conversions (`ensures True`) — they lower
the trusted *count* while adding near-zero verified *behavioral* content (they certify only body
type-safety + frame-cleanliness). The status doc is candid about this. Worth remembering when reading
the running count as a soundness metric.

---

## Part (b) — Forward-plan stress-test

### Finding 1 (MOST SEVERE) — Step 1 does NOT unlock the ir_scanner cluster it is sold on
The plan (status §4 Step 1; line 84) asserts Step 1 "**Unblocks the `ir_scanner` family (~34 stubs, the
largest cluster)**" and projects "**~+30 from `ir_scanner` alone**" (line 92). Reading the real bodies
(`src/pycsl/module6_whyml/ir_scanner.py`, live) and the mirror stub signatures
(`src/self-annotate/src/module6_whyml/ir_scanner.py`, 34 `\trusted`) refutes this. The 34 split into:

- **10 generic heterogeneous walkers** typed `obj: Any` in the mirror
  (`find_named_expr_targets`, `collection_binder_kinds`, `uses_inline_set_or_dict_ops`, `uses_subscript`,
  `uses_array_lit`, `uses_minmax`, `uses_string`, `uses_sum`, `uses_set_card`, `uses_ord_chr` — plus
  `uses_true_division`, `uses_divmod`). Their recursion is `for v in obj.values(): recurse(v)` /
  `for x in obj: recurse(x)` over the **untyped `Dict[str, Any]`** tree, descending into *every* field
  regardless of type and mixing expr/stmt/contract nodes and scalar leaves in one walk. A typed WhyML
  **variant has no `.values()` operation** — you cannot iterate "all fields of a `BinOp`" as a
  homogeneous list because `op:string`, `left:ir_node`, `right:ir_node` have different types. These
  have **no faithful typed-ADT lowering path**; converting them would require *rewriting the live
  emitter source* to structured recursion (a risky refactor of working code), which violates the SL
  "verbatim live body" discipline. **Step 1 does nothing for these; arguably no ADT step converts them.**

- **22 structured scanners** typed `stmts: List[int]` in the mirror (`uses_arrayset`,
  `find_assigned_vars`, `find_ghost_vars`, `has_continue`, `uses_for`, `collect_user_exceptions`, …).
  These dispatch on `stmt["stmt"]`/`stmt["type"]` and recurse into known keys (`body`, `orelse`,
  `handlers`, `cases`) — i.e. recursion over **stmt-node lists**. To type these you need the **stmt-node
  ADT with typed body lists**, which the plan itself schedules as **Step 4** (line 94), *not* Step 1.
  Step 1 adds only the *expr* list-kinds (`ArrayLit`/`SetLit`/`Tuple`/`DictLit`).

**Net: Step 1's expr list-kinds unblock neither subset.** The genuinely expr-arg-list recursions
(e.g. `Call.args` iteration) are exactly the generic `.values()` walkers above, which the ADT can't
model. This is the **same "feasibility-check-in-isolation over-optimism" the status doc claims to have
learned from in §3.3 — repeated in the forward plan.** The spike proves `size_list` on a *clean typed
`list ir_node`*; the real scanners walk `dict.values()`. The projected "~+30 from `ir_scanner`" is
unsupported by the code.

### Finding 2 (SEVERE) — the coupling claim for Step 1 is imprecise-to-wrong
Status §4 gating (lines 99-104) claims Step 1's "list projections return `list emit_ir`, covered by the
conservative `path_get` certificate — likely no new Phase-3 lemma." Phase2b_RecordVal.v models **none
of this**: `path_get : val7 -> path -> option val7` is *nested single-field record projection*
(`o.b.c`), returning one sub-value. It has **no list-of-subnode type, no `size_list`, no termination
measure over lists**. The soundness of `size_list` recursion is a **Why3-intrinsic termination VC**
(the `'vc` goals in the spike), *not* something `path_get` certifies. So the certificate does not cover
what Step 1 emits; the plan's stated justification is wrong, even though the *conclusion* ("no new
Phase-3 lemma needed") may accidentally hold because a pure ghost `size_list` measure is self-certified
by Why3, not by the semantics certificate. This should be argued correctly, not hand-waved through
`path_get`. It also re-exposes that the deferred **deep integration** (VRec in the core `val`, re-proving
the 22-constructor soundness induction) is the thing that would actually discharge the §0 coupling
principle — and the plan keeps deferring it while advancing Phase 1.

### Finding 3 (MODERATE) — "no remaining research risk, just execution volume" is overstated
The 10 generic `.values()` walkers are an *unsolved modeling problem*: faithful verification of untyped
heterogeneous tree reflection has no typed-variant representation. That is **research/design risk**, not
execution volume. The plan's risk register (`triage-ranked-tcb-tier3.md` §Risk) does not list it; the
closest ("surface not closed — `Any`/dynamic nodes") was resolved for *node kinds* but not for
*generic-field-iteration idioms*. Additionally, B4 (dict/map builders, str-tag inference) is
acknowledged as a "separate value-model gap" — also not merely volume.

### Finding 4 (MINOR) — the certificate is a side-car, so "de-risked" is half-earned
Findings verified in Part (a).2: the certificate proves *feasibility of a conservative extension*, which
genuinely de-risks the "can a record value be added axiom-free?" question. It does **not** de-risk "does
the mechanized soundness proof cover programs that manipulate record/variant values?" — because the core
`val` still lacks `VRec`. For *pure immutable* ir_node reads (the plan's model; inner mutation is
rejected per the nested-list memory) this may be acceptable, since variant projection is definitional in
Why3 and needs no soundness lemma. But then the honest statement is "the ir_node reads are pure values,
self-certified by Why3's variant semantics; the Rocq/Lean Phase2b is a *stronger-than-needed* feasibility
artifact" — not "the emitter ADT is certified by the Phase-7 model." The current framing implies a
tighter coupling than exists.

### Finding 5 (CONTEXT) — opportunity cost is real
Tier-1 yield was 8 (not the projected 39), tier-2a marker-yield was 0 (built then reverted `768f5392`→
`5c4b87e0`), and tier-3 has 0 ADT-enabled conversions after the P0–P3 build. Given Findings 1–3, the
"~150–200 Module-6-core stubs" payoff (plan §Phase 2) is not yet substantiated by any converted stub,
and the largest named cluster (ir_scanner) is now shown to be substantially harder than "list-kinds"
implies. The "prioritize by value, leave the mass trusted" stance (already applied to `pure_ast` ~262
and `proof2why3` — the two single largest trusted files, per `grep -c`) is likely the better call for
*more* of the frontier than the plan currently concedes.

---

## Part (c) — Findings ranked (most severe first)
1. **Step 1 does not unlock the ir_scanner cluster** (10 generic `.values()` walkers = no typed-ADT
   path; 22 structured scanners need the Step-4 stmt ADT, not Step-1 expr list-kinds). The "~+30 from
   ir_scanner" projection is unsupported. Repeats the §3.3 over-optimism it claims to have fixed.
2. **Coupling claim for Step 1 is wrong**: `path_get` (nested scalar record projection) does not cover
   `list emit_ir` / `size_list`; that soundness is Why3-intrinsic termination, not the certificate.
3. **"No research risk, just volume" is overstated**: generic heterogeneous reflection is an unsolved
   modeling problem, plus B4 value-model gaps.
4. **Certificate is a conservative side-car**, not a core-`val` integration; "certified/de-risked" is
   half-earned (honest in the doc's fine print, oversold in the headline).
5. **Trivial-contract conversions** (`ensures True`) reduce count without behavioral content — the
   running count is a weak soundness proxy. (Honestly disclosed.)

Everything I could not re-run is flagged; nothing material was un-reproducible. All five VERIFY items
reproduced.

## Part (d) — Bottom-line recommendation: PROCEED WITH CHANGES

The certified foundation is real and durable — bank it. But before the "payoff grind":

1. **Re-baseline the ir_scanner projection.** Triage the 34 into (a) ~22 structured stmt-list scanners
   → gated behind the **stmt-node ADT (Step 4)**, not Step 1; (b) ~10 generic `.values()` walkers →
   mark **leave-trusted or requires-live-source-rewrite**, with an explicit decision like the Phase-4
   `pure_ast`/`proof2why3` call. Do not carry them as "Step 1 unlocks ~34."
2. **Reorder:** if the goal is first real ADT payoff, the stmt-node ADT (current Step 4) reaches more
   convertible stubs than Step 1's expr list-kinds. Consider promoting it.
3. **Fix the coupling justification** for `size_list`: state it is a Why3-intrinsic termination witness,
   and decide honestly whether the deferred VRec-in-core-`val` integration is ever required (for pure
   reads, argue it is not; then stop calling Phase2b the "coupling certificate" for lists).
4. **Redo the §3.3 lesson properly:** the "whole-body port that full-proves" feasibility gate must be
   run on a *generic `.values()` walker* before any ir_scanner increment is scheduled — that single
   probe would have caught Finding 1.
5. **Weigh the opportunity cost explicitly** (Finding 5): with tier-1=8, tier-2=0, tier-3=0 realized,
   the value-first "leave-trusted" doctrine deserves to be applied to more of the Module-6 frontier,
   not just the peripherals. The marker count is not the soundness metric; the certificate is.
