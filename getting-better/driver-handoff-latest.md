# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-31, RELAUNCH #19 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 491 · grep-substring 516 · offset 25 · unattached 0. UNCHANGED, and
  that is the honest result of this session.** From `bin/count-trusted-directives.py`,
  never a hand-rolled grep — 25 of the grep hits are one boilerplate module-docstring
  line repeated across 25 mirror files. **Every increment this session was SOUNDNESS,
  FAITHFULNESS or GATE work.** The cheap-win queue was re-drained twice from scratch and
  is EMPTY; see "the census" below before you spend a minute looking for a cheap win.
- **`bin/check-shadowed-selfcalls.py`: 13 CONVERTED methods / 33 bypassing call sites,
  ratchet 13** (was 14 / 125). **The 92 `_csl_to_ir` sites — the largest single item that
  metric ever held — are GONE.** Needs `TMPDIR=/home/fabrice/git/pycsl/scratchpad`;
  `--emit-dir <dir-of-emitted-mlw> --verbose` gives the breakdown in seconds.
- **`bin/check-trusted-frame-honesty.py` now reports TWO POPULATIONS.**
  **trusted 3 model-visible / 73 total** (from 3/73, via 6/76 when the analysis was made
  table-aware). **converted 2 / 69** — a NEW population this session, first measured at
  63/130. All THREE trusted survivors are CONSTRUCTORS; the converted survivors are
  `ControlFlowStmtMixin._handle_return_stmt` and one constructor.
- Ledger **3**, untouched. Emitted axioms **0**. Corpus is **814** files.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`);
  `bin/self-annotate-mirror-check.sh` **3 mirrors drifted, exit 1 — that IS the baseline**,
  and this session compared the DRIFT LIST byte-for-byte on every increment rather than
  just the count.
- **Corpus byte-diff was 0 of 814 on EVERY increment**, including the three that changed
  the LIVE emitter (`module6_whyml/preamble.py`, `functions.py`, `expressions.py`,
  `abstract_ops.py`). Baseline at `scratchpad/w3/corpus_base`.
- **FULL REFERENCE SUITE: `Results: 3010/3112 passed`, and the 23 failing pycsl-reference
  names are IDENTICAL to the recorded baseline** (0211-0220, 0226, 0484, 0540, 0700, 0701,
  0714, 0766, 0932, 0938, 0943, 0944, 0948, 0949). Run with
  `PYCSL_SKIP_CONFORMANCE_CHECK=1`; the leading IR-conformance gate still aborts with 40
  MISMATCH on stale goldens — nobody's work item.
- **PROOF COSTS measured this session (they MOVED):**
  `frontend/Module5_IREmitter` **1199 → 1481 → 1499**, ~35-50 min. The rises are REAL VCs
  from making 75 methods concrete and then making their comprehensions faithful; every one
  discharges. `frontend/ir_resolve` **793**. `frontend/__init__` **684**.
  `src/self-annotate/src/pycsl.py` **732**. Others unchanged from #18's table.
- Tree clean apart from the pre-existing user/build dirt. `getting-better/.driver-deadline`
  intact and UNTOUCHED.
- **PUSH: nothing was pushed by this worker.** Do not push.

## WHAT THIS SESSION LANDED

1. **LADDER ITEM 0 — the known-live unsoundness `val function csl_to_ir_op` — CLOSED,
   plus a SECOND offender of the same class found by finishing the census.**
   The fold `function synth_overload_clauses` is now PROGRAM code: a `let rec` with a
   STRUCTURAL `variant { ens }` over `list ens_node`. **Why3 accepts structural descent on
   an algebraic type, so no `diverges` is needed and NO effect propagates to the caller** —
   the bespoke `_synthesize_overload_guard` emitter is untouched. The second offender is
   `val function m5_current_class_present : bool`, the ONLY ARGUMENT-LESS pure
   `val function` on the whole surface: an argument-less pure symbol over per-visit mutable
   state is a CONSTANT. Both re-proved: ir_resolve 793, __init__ 684, pycsl.py 732,
   Module5_IREmitter 1199, all 0 non-Valid.
   **THE PREMISE WAS RE-DERIVED, NOT INHERITED.** A table-aware transitive self-write
   analysis over the LIVE `Module5_IREmitter.py` (resolving `_CSL_HANDLERS` 79 /
   `_PY_EXPR_HANDLERS` 23 / `_PY_STMT_HANDLERS` 16) gives `_csl_to_ir` → 77 methods reached,
   WRITES `_fresh_var_counter`; `_py_expr_to_ir` → 48 reached, WRITES NOTHING. So the
   demotions are necessary AND `boolop_dispatch` / `dict_dispatch` /
   `emit_ir_disp__py_expr_to_ir` — also pure, also applied inside LOGIC folds — are sound
   and were correctly left alone. **The `val function` census is now COMPLETE over all 123
   symbols and there are no further offenders.**
2. **THE FOURTH GATE PLANE HAD TWO BLIND SPOTS. Both closed.**
   (a) **The CONVERTED surface.** The plane was scoped to `\trusted` stubs on the reasoning
   that a converted method has a body so Why3 checks its frame. HALF TRUE: Module 6 emits an
   explicit `writes {  }` and Why3 DOES reject an under-declared frame (spike: an OMITTED
   `writes` is INFERRED and silently accepted; an EXPLICIT empty one fails) — but it checks
   the EMITTED body, an ERASURE of the live one, and in every OTHER file the method is a
   caller-side abstract `val` minted from the same `#@ assigns`, where the frame is ASSUMED
   exactly as a stub's is.
   (b) **Table-aware dispatch.** The call-graph walk resolved `self.<m>(...)` by attribute
   name only, so it could not see `getattr(self, self._TABLE.get(k))(x)` — it was blind to
   precisely the DISPATCHERS. Gated on the body also performing a `getattr(self, ...)` call;
   tightening it that way changed NO count, which is evidence every table edge is a real
   dispatcher.
3. **THE `_csl_to_ir` CERTIFIED-BOUNDARY IS BROKEN — 75 methods concrete in ONE
   `let rec … with` group, 92 shadowed sites gone, 1481/1481 Valid.**
   The record said the family's effect summary "cannot be made exact BY CONSTRUCTION".
   **That is true of exactly TWO of the 75.** `scratchpad/w3/fix_assigns.py` drives the
   emitter and reacts to its OWN error text, editing only `#@` directives — the recorded
   reopening capability ("an effect analysis computed from the EMITTED BODY rather than the
   IR") built as a LOOP rather than as an analysis. 57 iterations to L3-tc.
   56 of 75 took the honest `#@ assigns self._fresh_var_counter`; 17 of the other 19 make NO
   self-call at all; the last 2 were the erasure. Blocker (2) did NOT need the reverted
   `_callee_raised_direct` registry fix — an explicit `#@ raises E when True` is a second,
   working route. **The dispatcher is BESPOKE-emitted and had never carried `#@ \diverges`
   (lesson (am)); the first proof run was 1481/1595 Valid with ALL 114 failures being its
   termination sub-goal.**
4. **THE FAITHFUL COMPREHENSION LOWERING — built, and it is SMALL.**
   `[self.<disp>(t) for t in xs]` now emits a LOCAL `let rec` that PERFORMS the call.
   **The architectural finding: it does NOT need to be a new member of the `let rec … with`
   group — a group member's body has its siblings IN SCOPE**, so a local `let rec` can call
   the concrete dispatcher directly. Both length-only oracles are gone; the exactness
   fixpoint then converged in SIX iterations and gave `_csl_mktuple` / `_csl_call_expr` the
   honest frame. Module5_IREmitter 1499/1499.
5. **THE `_py_stmts_to_ir` SHADOW TAKES ITS RECEIVER AND CARRIES ITS FRAME.**
   `val self__py_stmts_to_ir_1 (x0: array int)` was RECEIVER-LESS and EFFECT-FREE for a
   state-writing method. It has **FOUR PRODUCERS** — the generic `_handle_dotted_call`
   route, the hard-coded fallback table in `abstract_ops._SELF_DISPATCH_VAL_DECLS`, and
   three bespoke stmt handlers — and the decision now lives in ONE place
   (`functions._stmts_disp_writes`). Fails closed on the IMPORTED-emitter path, where the
   class is `type pycsltojsonemitter = int` and an unfilterable label produced `unbound
   function or predicate symbol '_fresh_var_counter'`.
6. **The census scorer had a FALSE-NEGATIVE CLASS.** Its `nilop` mark required an
   argument-less oracle's name to END IN `_<digits>`, so `errors.PyCSLError.message` —
   whose WHOLE emitted body is `(str_dunder_op ())` — scored 0 and read as a cheap win.
   Fixed in `scratchpad/w3/probe_all4.py`.

## CERTIFIED-BOUNDARIES RECORDED OR CORRECTED THIS SESSION

- **`pure_ast._Parser.error` / `.unsupported` — conclusion SURVIVES, reason REPLACED.**
  The mirror said they stay trusted because of "raise + f-string + the `_tokenize.tok_name`
  dict read" and that the conversion is "count-neutral". Both wrong. They DO convert
  (L3-tc GREEN, `let … ensures { false } raises { PyCSLSyntaxError }` over a real receiver
  read `t := (_parser__cur self)`) and the count goes 491 → 489. What declines it is
  `bin/check-emitted-vacuity.py --emit`: 2 NEW erasures, each function erasing its ONLY
  input. **REOPENING CAPABILITY: a modelled message payload on the raise** — the same
  decision `_fin` needs for its location stamps. The mirror comments now say this.
- **`_py_stmts_to_ir`'s bespoke second producers** — recorded then BUILT in the same
  session; see landing 5.

## RECORDED BOUNDARIES CARRIED FORWARD — do not re-grind without the named capability

- The `_csl_to_ir` boundary is **BROKEN and should be struck from any ladder that still
  lists it.**
- **The attribute-store third horn** (pass the state as an ARGUMENT to a pure projector)
  works and is axiom-free; it is still blocked on **OBJECT-IDENTITY INJECTIVITY**.
- **`crosscheck_ir.pairwise`** — spiked and working, demand NIL.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]** on the remaining
  non-dispatcher shadowed methods (now only 33 sites over 13 methods).
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER]**; `node(self, name, start_tok, **kw)`
  — [MODEL]; `_slice`; the **`_Unparser` family (~50 stubs)**; **`Module2_Parser`'s
  contract-expression cluster** (TERMINUS); `_decode_escapes` / `_decode_string`;
  `identifiers.whyml_ident` / `stable_hash`; `struct_format.parse_format` / `calcsize`;
  `proof2why3/normalize`'s whole file (regex).
- **`exception_model.bases_closure`** — the wall is the VALUE MODEL, not termination.
- Dropping the `_record_array_fields` PROXY disjunct changes 6 of 813 corpus files.

## Pick up here — in this order

1. **`ControlFlowStmtMixin._handle_return_stmt`** — the ONE non-constructor model-visible
   false frame left on either population (18 fields via-callee, including the MODELLED
   `_current_self_type`). Expect the same shape as landing 5: find which shadow/oracle
   erases the write, make it carry its receiver and its frame, then let
   `scratchpad/w3/fix_assigns.py` converge. `module6_whyml/stmt_control_flow` is 1846 goals,
   ~45 min.
2. **THE CONSTRUCTORS.** After item 1, EVERY remaining model-visible false frame on BOTH
   populations is a constructor (`PyCSLToJSONEmitter.__init__`, `pure_ast._Parser.__init__`,
   `Module2_Parser._ContractParser.__init__`, `proof2why3/parser.py::_Parser.__init__`). A
   constructor writing the fields of the object it is CONSTRUCTING is a materially weaker
   case, and correcting one means declaring the whole record written at every construction
   site. Judge it on its merits; do not drain it for the number.
3. **`scratchpad/w3/fix_assigns.py` IS THE REUSABLE TOOL OF THIS SESSION.** It converges
   `#@ assigns` / `#@ raises` / `#@ \diverges` against Why3's own error text. Point its
   `MIR` constant at another mirror and it generalises. Every wall whose recorded reason is
   "the effect summary cannot be made exact" should be re-tested with it FIRST.
4. **The `pyx_view` ADT redesign / record AST model** remains the soundness floor under the
   object-identity question. **KNOW THE OBSTACLE:** `pure_ast`'s node classes are
   SYNTHESIZED AT IMPORT by `type(name, (base,), body)` from `_NODE_SPEC`, so Module5's
   static `@dataclass` recognizer cannot see them.

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof; `grep -c "Prover result"` flushes in batches. **A run can sit
   at ZERO prover results for 50 minutes and then flush 1500 — do NOT conclude "stuck".**
   Check for live `alt-ergo`/`z3` children instead.
7. **A FAILING `pycsl.py` run is much FASTER than a passing one.**
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** `nohup` the proof, then wait in
   the FOREGROUND with `timeout 580 bash -c 'until … ; do sleep 25; done'` AND the Bash
   tool's own `timeout`. **`scratchpad/w3/prove.sh <files…>`** proves a list sequentially in
   the main tree; **`scratchpad/w3/prove_wt.sh`** does the same in the worktree.
8b. `bin/byte-diff-sweep.sh` RUNS WITH `--no-typecheck` — byte-diff 0 is NOT proof-safety.
9. **`scratchpad/w2/sweep.sh <root> <outdir>`** emits all 52 mirrors WITH L3-tc in ~35 s and
   writes an md5 manifest; **`keepsweep.sh`** keeps the `.mlw`. **PASS ABSOLUTE PATHS** — it
   `cd`s to `<root>` and a relative outdir lands inside the worktree.
10. **`--fun` CANNOT probe `Module5_IREmitter` at all** — whole-file or nothing.
11. **A GIT WORKTREE IS THE RIGHT PLACE FOR A SPIKE.** `git worktree add --detach
    scratchpad/w3/wt HEAD` + symlink `.venv`. It lets a long main-tree proof and a
    spike proof run at the same time, and it keeps a census's port→revert churn off the
    real tree. **Sync it with `git checkout --detach $(git -C <main> rev-parse HEAD)` —
    `git rev-parse HEAD` INSIDE the worktree returns the worktree's own HEAD.**
12. **A PROOF TRANSFERS BETWEEN TREES WHEN THE EMISSION MANIFEST IS IDENTICAL.** `diff` the
    two `sweep.sh` md5 manifests; if they match, the worktree's proof IS evidence for the
    main tree. This session used it once and re-ran the battery anyway.
13. The **Alt-Ergo pin at `pycsl.py:1318` is stale**. Pass
    `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.
14. **`grep` here is ugrep and MISBEHAVES on `driver-progress.log`** (very long lines). Use
    python. Write progress lines with a `python3 - <<'PYEOF'` heredoc, never inline `-c`.
15. **`cd` PERSISTS ACROSS A COMPOUND BASH COMMAND** in this harness even though the cwd is
    reset between calls. A `cd <worktree> && …` followed by a relative path silently
    operates on the wrong tree. Use absolute paths after any `cd`.
16. **NEVER put a `\trusted` marker LITERAL in a mirror comment** — it counts as a MARKER.
17. **NEW TOOLS this session** (`scratchpad/w3/`, foreground-only):
    `fix_assigns.py` (the Why3-EXACTNESS FIXPOINT over `#@ assigns`/`raises`/`\diverges` —
    the session's most valuable artifact), `probe_all4.py` (the census with the repaired
    argument-less-oracle mark), `conv_frame.py` (the converted-surface frame probe, now
    folded into the gate), `census.sh`, `prove.sh` / `prove_wt.sh`,
    `spike_local.mlw` / `spike_cc.mlw` / `spike_cc_neg2.mlw` / `spike_fold.mlw`.

## Method notes this session paid for

- **WHEN A RECORDED REASON SAYS "BY CONSTRUCTION", MAKE THE MACHINE SAY IT.** The
  `_csl_to_ir` boundary's claim that the family's effect summary can never be exact was true
  of 2 members out of 75. A loop that reads Why3's error text found that in 57 iterations;
  three sessions of reasoning had not.
- **`#@ \diverges` ASSERTS NOTHING, so it can never be the source of a false claim** — but
  a BESPOKE emitter is a SECOND PRODUCER of the contract block and will silently drop it.
  Lesson (am) fired FOUR times this session (the dispatcher's `diverges`, the
  `_py_stmts_to_ir` shadow's receiver, its declaration table, its three bespoke call sites).
- **A LOCAL `let rec` INSIDE A GROUP MEMBER'S BODY SEES ITS `let rec … with` SIBLINGS.**
  This is what made the faithful comprehension lowering a small change instead of a
  group-restructuring one.
- **AN ARGUMENT-LESS PURE `val function` IS A CONSTANT.** If it stands for mutable state,
  the model asserts that state never changes. Grep for `val function <name> : <type>` (no
  parameters) — there was exactly one, and it was wrong.
- **A GATE'S SCOPE IS A CLAIM, AND IT DESERVES THE SAME SUSPICION AS ITS THRESHOLD.** The
  frame-honesty plane's two blind spots were both in its SCOPE, not its measurement: it
  looked at the wrong population and it could not see dispatch.
- **A RATCHET MAY RISE WHEN THE ANALYSIS GETS SHARPER** — and the docstring must then say
  what it newly sees. The table-aware change took trusted 3/73 → 6/76 before the session's
  work took it back to 3/73.
- Still live from earlier sessions: **(ai)** prove sequentially; **(bq)** a returnless
  mutator is modelled as a NO-OP; **(bu)** the concrete-route allowlist is a serial silent
  floor; **(hh)** L3-tc passing is NOT a conversion criterion.
