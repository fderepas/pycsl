# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-31, RELAUNCH #18 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 491 · grep-substring 516 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep hits
  are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25.
  Stable across 3 samples. **Window #2 delta: markers 530 -> 491, grep 555 -> 516.**
  **This session (#18): 492 -> 491, ONE conversion across EIGHT gated increments** — the
  other seven are capability / faithfulness / gate work, and two of them moved metrics that
  matter more than the count (see below).
- **`bin/check-shadowed-selfcalls.py`: 14 CONVERTED methods / 125 bypassing call sites,
  ratchet 14** (was 14/153). Needs `TMPDIR=/home/fabrice/git/pycsl/scratchpad`; ~2 min.
  **92 of the 125 are the single remaining L2 dispatcher `_csl_to_ir`** — see its boundary.
- **NEW FOURTH GATE PLANE: `bin/check-trusted-frame-honesty.py` — 3 MODEL-VISIBLE / 73 total**
  (was 11 / 79 when first measured this session). All 3 survivors are CONSTRUCTORS.
- Ledger **3**, untouched. Emitted axioms: **0** in every file proved this session.
  Corpus is **814** files.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  `bin/self-annotate-mirror-check.sh`: **3 mirrors drifted, exit 1 — that IS the baseline.**
  check-untrusted-emitted **818 / 802 / 0 / 0** (was 817/801).
  emitted-vacuity `--emit`: no NEW erasure, **8 known**, 0 input-blind. doc-coherency GREEN.
- **Corpus byte-diff was 0 of 814 for EVERY ONE of this session's eight increments.**
  Nothing was spent. Verified after each with `bin/byte-diff-sweep.sh` against a HEAD-at-
  session-start baseline (`scratchpad/w2/corpus_base18`).
- **FULL REFERENCE SUITE on the final tree: `Results: 3010/3112 passed`, and the 102 failing
  names are IDENTICAL to the recorded baseline** — 23 in pycsl-reference (0211-0220, 0226,
  0484, 0540, 0700, 0701, 0714, 0766, 0932, 0938, 0943, 0944, 0948, 0949) and 79 in
  python-reference. **Zero regressions from eight increments, four of which changed the live
  emitter.** Run it with `PYCSL_SKIP_CONFORMANCE_CHECK=1` — the leading IR-conformance gate
  still aborts with **40 MISMATCH** (`only-derived=['param_ast_node_types','set_value_types']`,
  stale goldens, nobody's work item).
- **PROOF COSTS** (this session's measurements marked NEW; NOT proportional to source size):
  `frontend/pure_ast` **2857**, ~50 min. `frontend/Module5_IREmitter` **1198** (was 1134),
  ~50 min. `module6_whyml/stmt_control_flow` **1846**, ~45 min.
  **`module6_whyml/statements` 912, ~20 min (NEW — the campaign had never measured it)**.
  `module6_whyml/functions` **1191** (was 1187), ~30-45 min.
  `module6_whyml/expressions` **1069**, ~16 min. `frontend/Module2_Parser` **720**, ~10 min.
  `src/self-annotate/src/pycsl.py` **731**, ~20 min. `Module6_WhyMLTranspiler` **706**, ~20 min.
  `frontend/ir_resolve` **792**. `frontend/__init__` **683**. `proof2why3/parser` **438**.
  `frontend/Module3_Weaver` **266** (was 259), ~8 min — still the fastest real loop.
  `module6_whyml/preamble` **216**, ~5 min. `proof2why3/from_lean_json` **56**.
  `proof2why3/canonical` **48**. `frontend/exec_splice` **45**, `proof2why3/crosscheck_ir` **41**,
  `audit_proof` **40**, `audit_proof_reverify` **11**, `proof2why3/sertop` **11**,
  `module6_whyml/struct_format` **5**, `proof2why3/crosscheck` **2**. Corpus driver 1-11 s.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`, `style.css`). `getting-better/.driver-deadline`
  intact (Sep 1 08:24 UTC, untouched).
- **PUSH: nothing was pushed by this worker, and NOTHING NEW WAS PUSHED BY ANYONE.**
  `git reflog show origin/ghost-assign-bc6` still has its most recent `update by push` on
  **`4a4f0e66`**, exactly where relaunch #17 found it. 25 commits are ahead of that ref.
  Report only what you can verify; keep flagging the anomaly if it recurs.

## WHAT THIS SESSION LANDED (eight gated increments)

1. **THE CHEAP-WIN DRAIN, CENSUSED OVER THE COMPLETE SURFACE FOR THE FIRST TIME — 490 of 490
   stubs in ALL 44 mirror files, ZERO faithful wins.** Previous censuses covered ~230 in 22
   files. New repeatable tool `scratchpad/w2/probe_all2.py` ports each live body, re-emits
   `--no-proof --keep-mlw`, and **SCORES THE EMITTED BODY** for erasure (`str_hash_op`,
   `getattr_*`, `setattr_*`, argument-less oracles, `Array.make <n>`, `if true then`, `: int`
   params) instead of stopping at "L3-tc passes" (trap (hh)). ~10 minutes for the whole
   surface, 0.6 s per stub — the cheapest comprehensive oracle the campaign has. **38 pass
   L3-tc; all 38 decline on the emitted body.** Re-run it after EVERY capability lands.
2. **THE OBJECT-STATE WRITE MODEL — the FRAME PLANE made REAL for converted bodies.**
   An abstract `val setattr_* … : unit` has NO effect in Why3, so every mutating body
   satisfied `#@ assigns \nothing` VACUOUSLY. Now `_add_abstract_op` gives every `setattr_*`
   val `writes { _pyobj_state }` over one COARSE abstract cell and `_emit_function` emits the
   matching frame clause once the body is known to store an attribute — so `writes { }` under
   a mutating body is REJECTED. Nine mirror methods re-annotated honestly (the recorded gap
   said ELEVEN; two were false positives of a census that matched the emitter mirror's own
   STRING LITERALS `"val setattr_"`). Attribute READS stay effect-free `val`s, so the
   projector purity that got `_desugar_for` declined is NOT reintroduced.
   Module3_Weaver 259/259, functions 1191/1191, pure_ast 2857/2857.
3. **THE L2 DISPATCHER WALL BROKEN WITH `#@ \diverges` — `_py_expr_to_ir` IS CONCRETE,
   shadowed sites 153 -> 125, ZERO axioms.** The recorded floor said the 20-member mutual
   recursion needs a common variant, that the measure cannot be derived, and that the ledger
   would exceed 3. The first two are TRUE; the conclusion is not — a variant is only ONE of
   Why3's two ways to accept a recursive definition. Three parts: the SCC group-keyword
   post-process in `_emit_function` (nine bespoke group emitters hard-code `let`, breaking the
   `let rec … with` chain from the inside; byte-inert on its own), `\diverges` on the NINE
   members that ACTUALLY recurse (Why3 rejects it on the other eleven), and the caller cascade
   closed to a FIXPOINT computed statically over the emitted `.mlw` — exactly 12 more, then it
   stops, because every remaining self-call still goes through an abstract val.
   Module5_IREmitter 1198/1198, pycsl.py 731/731.
4. **`PyCSLWeaver._desugar_for` CONVERTED (492 -> 491) — and the soundness price that
   declined it is NOT PAID AT ALL.** The previous session built it, proved it 270/270 GREEN
   and reverted it because its chain needed PURE `val function get_<attr>` / `iter_length`
   projectors, solely so a `variant` term could mention them. The whole chain existed only to
   supply a variant; `\diverges` removes the need for one. Verified in the emitted `.mlw`:
   `get_lo`/`get_hi`/`get_var`/`get_clauses`/`iter_length`/`iter_get` are all PROGRAM vals,
   never `val function`. Module3_Weaver 266/266.
5. **A FOURTH GATE PLANE: `bin/check-trusted-frame-honesty.py`.** A `\trusted` stub's contract
   is ASSUMED, never checked, so a stub declaring `#@ assigns \nothing` for a live method that
   really mutates `self` is an unsoundness NO EXISTING PLANE CAN SEE — the proof is green, the
   byte-diff is 0, mirror-sync is happy and the vacuity probe finds nothing, because there is
   no body to check the claim against. Measured with a call-graph fixpoint over the live tree.
   First measurement: **390 stubs declare `assigns \nothing`; 79 stand for a live body that
   transitively writes self state; 27 write DIRECTLY; 11 MODEL-VISIBLE.**
6. **`ExpressionEmissionMixin._to_bool` corrected (11 -> 10)**, plus the emitter fix it
   needed: the CALLER-SIDE shadow val was emitted with all 17 declared fields while the
   callee's own val correctly carried 4 — `_emit_function` filters a method's own writes
   through `_emitted_record_field_labels`, the caller-side abstract op in
   `_resolve_dotted_signature` is a SECOND PRODUCER of the same clause and did not (lesson
   (am)). New `_writes_filtered_to_labels`. expressions 1069/1069, M6T 706/706.
7. **`ControlFlowStmtMixin._render_match_pattern` corrected, and the gate's model-visibility
   test sharpened to a PER-FILE question (10 -> 7).** stmt_control_flow 1846/1846.
8. **The four `module6_whyml/statements.py` false frames drained (7 -> 3).** statements
   **912/912 (NEW cost)**, M6T 706/706. All three survivors are constructors.

## CERTIFIED-BOUNDARIES RECORDED OR CORRECTED THIS SESSION

- **`_csl_to_ir` (92 shadowed sites — the largest single item left on that metric) — NEW AND
  PRECISE REASON.** The recorded cause ("members of a `let rec … with` group must agree on
  their EFFECT SUMMARY") is directionally right and incomplete. The whole chain was walked
  with `#@ sibling_concrete` applied: (1) `unlisted write effect` — a member really does reach
  `_csl_in`, which writes `self._fresh_var_counter`, so today's abstract `val` with
  `assigns \nothing` models the WHOLE handler subtree as pure and it is not; declaring
  `#@ assigns self._fresh_var_counter` on the members clears it. (2) `unlisted exception` —
  root cause is a REGISTRY-KEY MISMATCH: `_callee_raised_direct` looks callees up by the Call
  node's `self.<m>` spelling while `_module_func_raises` is keyed by the qualified
  `<class>__<m>`, so **a callee's `#@ raises` is invisible to its sibling callers**. Fixed and
  measured BYTE-INERT (0 of 52 mirrors, 0 of 814 corpus) — then REVERTED, because
  `_callee_raised_direct` is mirrored UN-TRUSTED and its own mirror body is already a facade
  (`registry := (if (0 <> 0) || ((const (None: option int)) <> 0) then 1 else 0)`), so the
  required port stops type-checking. (3) **THE WALL: Why3 requires a concrete `let`'s effect
  summary to be EXACT and rejects over-declaration BOTH ways** (`this write effect does not
  happen in the expression`, `this expression does not raise exception PyCSLIRError`). It
  cannot be made exact because the IR-level analysis and the emitted body disagree BY
  CONSTRUCTION: `_csl_mktuple`'s `[self._csl_to_ir(e) for e in node.elts]` lowers to
  `(IrMkTupleN (list_content_comp_3 node.mktupleexpr_elts))`, where
  `val list_content_comp_3 (src: array emit_ir) : irlist` is a PURE, EFFECT-FREE oracle and
  the per-element call is GONE. **REOPENING CAPABILITY: a FAITHFUL comprehension lowering for
  `[self.<m>(e) for e in xs]` that actually performs the call, or an effect analysis computed
  from the EMITTED BODY rather than the IR — the principle the `materialize` bridge already
  uses when it tests `any("(materialize_X " in l for l in lines)`.**
- **THE "ATTRIBUTE STORE IS STRUCTURALLY IMPOSSIBLE IN WHY3" REFUTATION WAS WRONG ABOUT ITS
  OWN HORNS — there is a THIRD, and it works.** The record called two horns exclusive and
  exhaustive (a ghost `ref (map …)`, or an `array int` store making `get_<attr>` non-pure).
  Spiked in minutes (`scratchpad/w2/heapspike.mlw`): keep the state as an opaque program
  token and PASS IT AS AN ARGUMENT to a pure logic projector —
  `val _pyobj_state : ref int`, `val function get_attr (st o f: int) : int` (pure, because the
  state is an ARGUMENT and not an external variable, hence legal in every contract clause),
  `val setattr_3 … writes { _pyobj_state } ensures { get_attr !_pyobj_state x f = v }`.
  Alt-Ergo: the mutate-then-read TRUE fact is **Valid**; the FALSE preservation claim across a
  store is **Unknown**. Zero axioms. **IT IS STILL A BOUNDARY FOR A NEW REASON:
  OBJECT-IDENTITY INJECTIVITY.** The read relation is sound only if distinct objects never
  lower to the same Why3 term, and the int-erased object model gives no such guarantee
  (`_coerce_to_int` collapses to the literal `0`; erased locals are `ref 0`). Measured against
  the emitted `.mlw`: today every `setattr_*`/`getattr_*` object term is a plain identifier
  (`node` 35 / `self` 12 writes; `self` 22 / typed `x` 8 reads), never a literal — so the
  hazard is UNEXERCISED but UNPREVENTED. **REOPENING CAPABILITY: injective object identity —
  the record AST model, or an allocator minting provably-distinct references. The heap
  encoding itself is DONE.**
- **`exception_model.bases_closure` — its recorded reason is only half the blockage.** Tried
  with `\diverges` and refuted in seconds: it fails L3-tc with `This expression has type
  string, but is expected to have type int`. The wall is the VALUE MODEL, not the
  while-fixpoint termination the record names.

## RECORDED BOUNDARIES CARRIED FORWARD — do not re-grind without the named capability

- The three above, plus everything below.
- **`crosscheck_ir.pairwise`** — the `Optional[Term]` PARAM route is SPIKED AND WORKING
  (`scratchpad/w2/opt_term_param.spike.patch`); two gaps remain: (a) a call to a LIFTED NESTED
  `def` does not resolve to the hoisted symbol; (b) `Dict[str, Optional[bool]]` is not
  expressible (the dict model already spends `option` on KEY PRESENCE). DEMAND IS NIL — the
  only reader of `.pairwise` is the `\trusted` `diagnostic()`. A whole-repo census this session
  found only **6** trusted stubs with a nested `def` at all, all in heavy I/O functions, so the
  generic lifted-nested-def capability has almost no yield.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]** on the 11 non-dispatcher
  shadowed methods.
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER]**; `node(self, name, start_tok, **kw)`
  — [MODEL]; `_slice` (needs `self._lines`); the **`_Unparser` family (~50 stubs)** — 13 of
  them pass L3-tc and every one is an int-erased facade; **`Module2_Parser`'s
  contract-expression cluster** (TERMINUS); `_decode_escapes` / `_decode_string`;
  `identifiers.whyml_ident` / `stable_hash`; `struct_format.parse_format` / `calcsize`;
  `proof2why3/normalize`'s whole file (regex).
- **`error` / `unsupported`** stay `\trusted` by design; count-neutral.
- Dropping the `_record_array_fields` PROXY disjunct changes 6 of 813 corpus files.
- The **Set[str]-returning surface is EXHAUSTED**: a fresh AST census found only FOUR trusted
  `Set[str]` stubs left — `audit_proof._parse_rocq_file` / `_parse_lean_file` /
  `_index_proofs_dir` (file I/O) and `statements._typed_local_vars` (recorded). Backlog 1b(A)
  has nothing left to convert; the per-callee `#@ sibling_concrete` gate it asked for exists.

## Pick up here — in this order

1. **`#@ \diverges` IS A NEW, CHEAP, AXIOM-FREE TOOL AND IT IS NOT YET FULLY MINED.** It broke
   two recorded floors this session. Its scope is bounded and known: a stub blocked ONLY on
   termination PASSES L3-tc today, so it is necessarily inside the 38-member KEEP set of the
   complete-surface census — and a re-run of that census WITH `\diverges` injected
   (`scratchpad/w2/probe_all3.py`) produced NO new candidates. So do not re-probe for more
   conversions; instead apply it wherever a build's soundness price is being paid ONLY to
   satisfy a termination obligation. **RULE, banked: `\diverges` asserts NOTHING, so it can
   never be the source of a false claim, whereas a purity upgrade can.**
2. **THE `_csl_to_ir` REOPENING CAPABILITY — a faithful comprehension lowering for
   `[self.<m>(e) for e in xs]`.** This is the highest-value item left: it is the named
   blocker for the 92 remaining shadowed sites, it removes a content-law ORACLE in favour of a
   real call, and the rest of that build (the honest `#@ assigns self._fresh_var_counter` on
   the 56 group members, `\diverges` for the group) is already walked and understood. Watch
   the `irlist` size-lemma explosion note in `preamble.py` before reaching for a polymorphic
   list.
3. **THE THREE REMAINING MODEL-VISIBLE FALSE TRUSTED FRAMES ARE ALL CONSTRUCTORS**
   (`PyCSLToJSONEmitter.__init__`, `pure_ast._Parser.__init__`, `_ContractParser.__init__`).
   A constructor writing the fields of the object it is CONSTRUCTING is a materially weaker
   case than a method mutating shared cursor state, and correcting one means declaring the
   whole record written at every construction site. Judge it on its merits; do not drain it
   for the number. The **73 total** (non-model-visible) offenders are honest-annotation debt,
   not unsoundness — correcting one of those is COSMETIC and was measured to change the
   emitted `.mlw` not at all.
4. **The `pyx_view` ADT redesign / the record AST model** remains the soundness floor under
   everything above: it is what makes object identity INJECTIVE (unblocking the heap encoding
   in §2 of the boundaries), what would let the L2 groups carry a real variant instead of
   `\diverges`, and what makes the AST-node `: int` erasure — measured at roughly twenty of
   the 38 L3-tc-passing stubs — go away. **BE PRECISE ABOUT WHAT EXISTS:** `py_with_node` /
   `py_match_node` / `py_ghost_node` are ABSTRACT types with pure `val` projectors, NOT
   records; the record model to route onto is the `@dataclass` one with MUTABLE FIELDS.
   **AND KNOW THE NEW OBSTACLE MEASURED THIS SESSION:** `pure_ast`'s node classes are
   SYNTHESIZED AT IMPORT by `type(name, (base,), body)` from the `_NODE_SPEC` dict literal,
   so Module5's static `@dataclass` recognizer cannot see them at all. Routing them onto the
   record model first requires either static class declarations in `pure_ast` (a real change
   to a core live file) or a bespoke recognizer that reads `_NODE_SPEC` itself.

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof; a `grep -c "Prover result"` on a running log flushes in
   batches. Do not conclude "stuck" from it.
7. **A FAILING `pycsl.py` run is much FASTER than a passing one.**
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** `nohup` the proof, then wait in
   the FOREGROUND with `timeout 580 bash -c 'until … ; do sleep 25; done'` AND pass the Bash
   tool's own `timeout`. **`scratchpad/w2/r18prove.sh <file> …`** proves a LIST sequentially
   (edit its `OUT=` per battery, as `r18prove2..7.sh` do).
8b. **`bin/byte-diff-sweep.sh` RUNS WITH `--no-typecheck`** — byte-diff 0 is NOT proof-safety.
9. **`scratchpad/w2/sweep.sh <root> <outdir>`** emits all 52 mirrors WITH L3-tc in ~35 s;
   **`keepsweep.sh`** keeps the `.mlw`. `bin/byte-diff-sweep.sh <out>` does 814 corpus files in
   ~32 s. RE-BASELINE both after every landed increment.
10. **`--fun` CANNOT probe `Module5_IREmitter` at all** — whole-file or nothing.
11. **`bin/check-shadowed-selfcalls.py --emit-dir <dir> --verbose`** gives the per-method
    breakdown in seconds from already-emitted `.mlw`.
12. The **Alt-Ergo pin at `pycsl.py:1318` is stale**. Pass
    `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.
13. **`grep` MISBEHAVES on `driver-progress.log`** (very long lines). Use
    `python3 -c "print(open(f).read().count(...))"`. The shell `grep` here is **ugrep**.
14. **A `#@`-block heredoc in a Bash `-m` commit message gets MANGLED by backtick command
    substitution.** Use `git commit -F -` with a QUOTED heredoc. Same for progress-log lines:
    write them with a `python3 - <<'PYEOF'` heredoc, never an inline `python3 -c "…"` (a
    backslash or apostrophe in the text kills it — happened once this session).
15. **Check `ps -eo cmd | grep -c '[p]ycsl.py'` BEFORE launching a battery.**
16. **NEVER put a `\trusted` marker LITERAL in a mirror comment** — it counts as a MARKER.
17. **NEW TOOLS this session** (all in `scratchpad/w2/`, foreground-only, always restoring):
    `probe_all2.py` (complete-surface census WITH an emitted-body erasure score),
    `probe_all3.py` (the same, injecting extra `#@` directives),
    `port_one.py` (port ONE stub's live body in place, plus extra directives — no restore),
    `fix_assigns_loop.py` / `fix_writes_loop.py` (iterate the emitter and repair a `#@ assigns`
    cascade to a fixpoint).

## Method notes this session paid for

- **WHEN A BUILD'S SOUNDNESS PRICE IS PAID ONLY TO SATISFY A TERMINATION OBLIGATION, CHECK
  WHETHER PARTIAL CORRECTNESS BUYS THE SAME RESULT FOR FREE.** `#@ \diverges` asserts nothing.
  It broke the L2 dispatcher floor AND converted `_desugar_for` without its declined price.
- **A RECORDED REFUTATION'S "EXHAUSTIVE HORNS" DESERVE THE SAME SUSPICION AS ITS GATE AND ITS
  MODEL.** The attribute-store refutation named two horns and called them exhaustive; the
  third (pass the state as an ARGUMENT) works and is axiom-free. This is the FOURTH
  consecutive session in which a recorded boundary was wrong about its own reason.
- **WHEN A LIVE-EMITTER CHANGE COSTS FIDELITY DRIFT, LOOK FOR A `\trusted`-MIRRORED CHOKE
  POINT THE SAME CHANGE CAN SIT BEHIND.** The object-state model first went into
  `statements.py` (mirrored un-trusted) and immediately cost 2 new `DIVERGED` entries, a
  ported helper and an unbound writes label; the identical three lines in `_add_abstract_op`
  (a `\trusted` stub) cost nothing. Same trick made the caller-side writes filter free.
- **A GATE MUST MEASURE THE MODEL'S CLAIM, NOT THE ANNOTATION'S WORDING.** The new
  frame-honesty metric was defined three times (79 -> 22 -> 11 -> 7) before it counted only
  the claims a prover can actually be misled by: `@mutable_state` class AND a field the
  stub's OWN MIRROR FILE assigns. A repo-wide field set still counted a class whose file
  emits `type <cls> = int`.
- **A FALSE `assigns \nothing` ON A TRUSTED EMITTER STUB HIDES A ONE-METHOD CASCADE, NOT A
  WAVE** — measured three times in a row (`_to_bool`, `_render_match_pattern`, the four
  statements.py stubs) — because every other path to the mutated state already declares it.
  But seed the cascade loop with the stub's FULL declared write set: seeded short it spins
  forever re-adding the same insufficient clause (60 no-progress iterations, measured).
- **AN EFFECT SUMMARY MUST BE EXACT IN WHY3, NOT AN OVER-APPROXIMATION.** Why3 rejects both
  `this write effect does not happen` and `this expression does not raise exception X`. Any
  scheme that DERIVES a frame from the IR must therefore agree with what the body EMITS.
- Still live: **(am)** ASSUME TWO PRODUCERS — it bit three more times this session (the SCC
  group keyword, the bespoke dispatcher dropping `#@ \diverges`, the caller-side `writes`
  clause); **(ai)** prove sequentially; **(bq)** a returnless mutator is modelled as a NO-OP;
  **(bu)** the concrete-route allowlist is a serial silent floor; **(hh)** L3-tc passing is NOT
  a conversion criterion — now measured at 38 of 38 over the COMPLETE surface.
