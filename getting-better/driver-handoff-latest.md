# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-29, RELAUNCH #11 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 516 · grep-substring 541 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep
  hits are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25. Stable across
  three samples.
  **Window #2 delta so far: markers 530 -> 516, grep 555 -> 541.**
  **This session (#11): 521 -> 516 — FIVE conversions, a shadowed-selfcall repair wave,
  a live-tool faithfulness repair, and FOUR certified boundaries of which TWO WERE THEN
  BROKEN in the same session, in seven gated increments.**
- **`bin/check-shadowed-selfcalls.py`: 27 CONVERTED methods / 176 bypassing call sites,
  RATCHET LOWERED to 27** (was 32 / 192 at session start; 50 / 259 at window start). Needs
  `TMPDIR` on the repo filesystem (`TMPDIR=/home/fabrice/git/pycsl/scratchpad`).
- Ledger **3**, untouched. Emitted axioms in pure_ast: **0**, unchanged.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **794 / 777 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known**. Corpus byte-diff **0 over 813/813**.
  `frontend/pure_ast` proves **2202 / 2202**.
  `bin/self-annotate-mirror-check.sh` byte-identical to the HEAD baseline.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`, `style.css` — a why3doc artifact from Aug 26).
  Leave it alone. `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC).
  **~74 h remained on the window at handoff time.** Commits are unpushed by design.

## WHAT THIS SESSION LANDED (seven gated increments)

1. **`_binop` CONVERTED (521 -> 520) — CERTIFIED-BOUNDARY [GROUP VARIANT RE-PHASING]
   BROKEN.** The `str -> (str, int)` PAIR-dict emitter capability plus the SIXTEEN-member
   expression-group variant re-phasing. TCB net STRICTLY negative: the emitted file's
   abstract-`val` set differs from HEAD's by exactly one line (`val _parser___binop`
   REMOVED, zero added).
2. **Shadowed-selfcall repair wave 4 (32 -> 27 methods, 192 -> 176 sites; ratchet lowered
   to 27).** `#@ sibling_concrete` makes a self-call REAL recursion (the dotted `self.<m>`
   form `IRScanner.is_recursive` missed), plus a NARROW kind-local discriminant carve-out.
   Seven mirrors re-proved, all SUCCESS.
3. **`_fstring` + `_fstring_format_spec` CONVERTED (520 -> 518).** The LITERAL-VALUE carrier
   `irconst = ICStr string | ICNone`, an `irlist` slot filled from an `array
   emit_ir`-returning CALL, and **a live-tool faithfulness repair: a module-level call's
   KEYWORD ARGUMENTS were silently dropped and the callee's DEFAULT emitted in their
   place** — fixed generally, corpus byte-diff 0.
4. **`_subscript_item` REFUTED**, with the recorded diagnosis REPLACED (the old one was
   wrong) and the reopening capability named precisely.
5. **`_subscript_item` CONVERTED (518 -> 517)** — the boundary from increment 4, broken
   four hours later by exactly the capability it named. THE OPTIONAL-NODE CARRIER LOCAL
   (`iropt_ir`) + the `IrPySlice` arm + a SECOND group re-phasing (NINETEEN members,
   multiplier 13 -> 16).
6. **`_fstring_replacement` CONVERTED (517 -> 516)** — the boundary from increment 3,
   broken by the three capabilities it named. The OPTIONAL-STRING carrier (`iropt_str`)
   completes the pair, and it is a SOUNDNESS-shaped fix: both guards had been lowering to
   LITERALS (`format_spec is None` -> `false`, `debug_text is not None` -> `true`), so the
   model took the wrong branches. **The f-string cluster's three convertible members are
   all in.**
7. **`lambda_parameters` REFUTED — [LIST-ALIAS ELEMENT TYPE]**, five of six pieces built
   and measured, the sixth named. Spike fully reverted; emission byte-identical to
   increment 6, so no re-proof was needed.

New emit_ir arms added this session: `IrPyConstant irconst iropt_str`,
`IrPyJoinedStr irlist`, `IrPySlice iropt_ir iropt_ir iropt_ir`,
`IrPyFormattedValue emit_ir int iropt_ir`, plus the `irconst` carrier and the two DEFINED
projectors `iropt_val` / `iropt_str_val` (no axiom; ledger unchanged).

## Pick up here — in this order

0. **The shadowed residue is 27 methods / 176 sites, and 142 of those sites are the two
   Module5 dispatchers** (`_csl_to_ir` 92, `_py_expr_to_ir` 44, `_py_op_to_str` 6) — the
   recorded L2 TYPE-UNIFICATION wall, and now the single biggest named item on the board.
   The `comprehension`-joins-the-family move is the shape that answers it: give every
   handler's input class an `_PYAST_IRNODE_CTORS`-style ADT arm so the handlers unify on
   `emit_ir`. A large, well-defined, funded-window build. The long tail's per-method
   blockers are named in the relaunch-#10 increment-5 commit PLUS one from this session:
   **a `-> bool` callee emits as a `bool`-returning logic symbol while the concrete call
   site coerces `<> 0` for an int** (`_is_final_annotation`).
1. **`lambda_parameters` / `parse_parameters` — ONE missing capability, and it is named.**
   PROBED AND REFUTED this session as [LIST-ALIAS ELEMENT TYPE], but FIVE of the six pieces
   were BUILT AND MEASURED WORKING and are spelled out in the refutation commit and on the
   stub: the `IrPyArg string iropt_ir iropt_str` family arm (+ `_lambda_arg -> "ExprIR"`),
   `arguments.kw_defaults` retyped `irlist -> iroptlist`, a SECOND admission route for the
   optional-node carrier (`None`-assigned AND presence-tested), a SLOT-based
   `iropt_ir`-element seq classification, and the two carrier-append rules.
   **THE ONE MISSING PIECE: propagate a seq local's ELEMENT TYPE across an
   `x = <other seq local>` REBINDING** (`posonly = args; args = []`) — a fixpoint over the
   assignment graph. Without it the `posonlyargs` `irlist` slot declines and the whole
   `arguments` construction falls back to the `arguments_0 ()` facade. Two markers for one
   capability plus a re-build of five measured pieces: the best ratio on the board.
2. **`small_stmt`** — still [HETEROGENEOUS CONVERTED RETURNS]. Its five siblings are
   CONVERTED onto harvested RECORD returns; migrating them onto `_PYAST_IRNODE_CTORS` arms
   (plus `alias`) is a well-trodden move now. The count does not move until the LAST one
   lands.
3. **`strings`** — the last f-string-cluster member and the hardest: `b"".join(...)` over a
   BYTES value, a `kinds` SET, and tuple-in-list parts. Not probed.
4. **The `Constant` NUMBER arm.** `irconst` is the frame; adding an `ICNum`-shaped arm plus
   a faithful `_parse_number` interface reopens `atom`, `_pattern_number` and
   `closed_pattern` in one move (three markers).

## RECORDED BOUNDARIES — do not re-grind without new capability

- **`_fin` — [ERASURE-LEDGER], a JUDGEMENT not a wall (lesson (bd)).** Proved 1612/1612 and
  reverted anyway: it trades a COUNTED marker for an UNCOUNTED erasure-ledger entry and
  buys nothing. Do not re-spike; read (bd) and (bf) §3 first.
- **`_set_ctx(node, _N("Store")())` — [CORRECTNESS].** `emit_ir` is IMMUTABLE and `ctx` IS
  modelled. Blocks `namedexpr_test`, `_comp_target`, `_for_target`, `expr_stmt`, `del_stmt`,
  `_with_item`. Reopening: a functional `set_ctx` in the LIVE SOURCE. The POSITION plane is
  NOT part of this (lesson (az)) — only `ctx`.
- **`small_stmt` — [HETEROGENEOUS CONVERTED RETURNS]** (lessons (av)-(ax)). Ladder 2.
- **`lambda_parameters` / `parse_parameters` — [LIST-ALIAS ELEMENT TYPE].** Ladder 1; five
  of six pieces measured working, the sixth named.
- **`_pattern_number`, `atom`, `closed_pattern` — [MODEL].** `Constant(value=…)` needs the
  parser's own number/constant classification. **The `irconst` carrier built this session is
  the frame for it**: add an `ICNum`-shaped arm and a faithful `_parse_number` interface and
  these reopen. Until then a non-string, non-None literal DECLINES fail-closed, which is
  what keeps them honest. See ladder 4.
- **`_max_end` / `_fin_block` — [ERASURE-LEDGER], the `_fin` judgement (lesson (bd)).**
  Both are PURE POSITION work and every call site already elides them, so converting them
  would trade a COUNTED marker for an UNCOUNTED erasure-ledger entry and buy a caller
  nothing. Same reopening condition as `_fin`: an `emit_ir` that CARRIES the four ASDL
  location attributes.
- **`node(self, name, start_tok, **kw)` — [MODEL].** A `**kw` SPLAT into `_N(name)(…)`
  with a run-time class name; neither the by-name payload binding nor the variable-class
  recognizers can see the field set.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION].** Ladder 0.
- **`for`-over-array termination** — the SOURCE cannot supply a variant.
- The **`_Unparser` family (~51 stubs in pure_ast)** is blocked by
  `self.interleave(lambda: …, self.traverse, node.names)` — LAMBDA + higher-order function —
  and `with self.delimit(…)` context managers. A fundamental modelling boundary.
- **`error` / `unsupported`** stay `\trusted` by design (raise + f-string); count-neutral.

## FLAGGED FOR THE USER (outside the campaign's mandate — NOT taken)

Still standing from earlier windows: **the Alt-Ergo pin at `pycsl.py:1318` is stale**
(2.6.2 vs installed 2.6.3), so a nominally dual-prover run is silently Z3-only. Keep passing
`--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.

Also still standing: **dropping the `_record_array_fields` PROXY disjunct from
`_handle_dotted_call`'s concrete-sibling gate changes only 6 of 813 corpus files, and every
one replaces an opaque abstract `val` with the real concrete application** — including 0721
and 0722, where the abstract route had SILENTLY DROPPED the callee's
`requires self.session_authenticated = 1`. Measured, reverted, recorded in lesson (bc).

**NEW THIS SESSION, and it was TAKEN because it costs users nothing:** a module-level
call's KEYWORD ARGUMENTS were silently dropped and the callee's DEFAULT emitted in their
place. `_merge_str_constants(values, drop_empty=False)` emitted `… 1`, i.e. `True`. Fixed
generally; corpus byte-diff 0 over 813. **Look for the same defect wherever an argument list
is rebuilt from positions** — this one was found only because a conversion happened to pass
a keyword.

**NEW THIS SESSION, FOUND AND NOT TAKEN:** Module5's `_py_stmt_assign` reads
`stmt.targets[0]` ONLY, so the SECOND AND LATER targets of a CHAINED assignment
(`a = b = c = V`) are SILENTLY DROPPED — a fail-open, the same shape as the `p.x = v` no-op
its own comment warns about. The three-line repair was built and measured corpus-byte-inert
(0 over 813) and reverted anyway, because the mirror's own emitted model of
`_py_stmt_assign` goes through the typed AST reader `assign_target0_ast`, which exposes only
`targets[0]`: the repaired body's new branch is silently dropped from the emission (measured
BYTE-IDENTICAL with and without the fix). **A live change whose mirror counterpart cannot be
EMITTED does not get verified** — it just widens the gap between the body and the model
(lesson (bb), sharpened; lesson (bk) §2). Reopening capability named: `assign_targets_len` /
`assign_targetk_ast` in the reader model.

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof, or the log stays empty until the run ends.
7. The Bash tool caps a foreground command at 10 minutes. Run the proof with `nohup … &` and
   poll. **`scratchpad/w2/proveseq.sh <logdir> <files…>`** proves a LIST sequentially and
   appends START/DONE/valid/total per file to `<logdir>/seq.status`; it obeys lesson (ai) by
   construction. **`scratchpad/w2/sweep.sh <repo-root> <outdir>`** emits all 52 mirrors WITH
   L3-tc and writes an md5+TC_OK/TC_FAIL manifest in ~35 SECONDS — diff two manifests to get
   the exact changed-mirror set (that is how this session's 7-mirror second-order radius was
   found rather than guessed). Corpus byte-diff sweep: ~32 s.
8. **`--fun` CANNOT probe a mutual-recursion group.** Slicing one re-emits as
   `unbound function or predicate symbol` / `unexpected 'variant' clause`. A group is proved
   whole or not at all.
9. **`bin/check-shadowed-selfcalls.py` has its BASELINE as a constant in the file** — lower
   it in the same commit as the wave that earns it.

## The §10.4 RE-PORT PRICE LIST (re-measured this session)

| mirror | goals | wall clock |
|---|---|---|
| any `\trusted` mirror body | — | **0** |
| `module6_whyml/types` | 669 | ~9 min |
| `Module6_WhyMLTranspiler` | 706 | ~12 min |
| `pycsl` | 730 | ~17 min |
| `module6_whyml/statements` | 904 | ~23 min |
| `module6_whyml/expressions` | 1049 | ~15 min |
| `frontend/Module5_IREmitter` | 1115 | ~50 min |
| `frontend/pure_ast` | **2202** | ~40 min |

Mirror emission sweep WITH L3-tc (52 files): **~35 s**. Corpus byte-diff (813, 6 jobs): ~32 s.

## THE FASTEST THING THIS CAMPAIGN KNOWS — use it

**An emit-only run is a 1-SECOND oracle for pure_ast.**
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --no-proof
--keep-mlw` type-checks (L3-tc is ON) and leaves the `.mlw` for inspection. EVERY capability
this session was designed by porting a body, emitting, READING the emitted WhyML for facades,
and iterating — before spending a minute of proof time. It also PRICES A VARIANT SHAPE: "all
functions in a recursive definition must use the same well-founded order" is a TYPE-CHECK
error, so the whole sixteen-member re-phasing was converged in seconds and only the DECREASE
cost a proof. And it is how `_subscript_item`'s recorded diagnosis was found to be wrong.

**Run `bin/check-self-annotate-sync.sh` immediately after ANY live-emitter edit.** Seconds,
and it catches a mis-placed edit before it costs proof time (lesson (bb)).

## Method notes this session paid for (full text in wall-lessons.md, (bh)-(bl))

- **(bh)** the group re-phasing, executed: cost the CYCLE, not the function — find the one
  provably advancing edge and count offsets backwards from it; L3-tc prices the variant SHAPE
  for free; spike a termination question with a PLACEHOLDER body; and a lever that BYPASSES
  an opaque abstract op must also stop REGISTERING it (measure by diffing the emitted `val`
  SET against the baseline).
- **(bi)** `#@ sibling_concrete` makes a self-call REAL recursion; and a `kind_of` string
  guard is not merely slower than `is_K` but INSUFFICIENT for a structural recursion — the
  `IrOther "K"` catch-all makes the size-decrease genuinely FALSE. When one arm of a two-arm
  structural recursion proves and its twin times out, look for the accidental
  constructor-pinning conjunct.
- **(bj)** carry the literal's SHAPE, not one of the shapes; and a keyword argument that was
  silently replaced by the callee's default — caught by writing the same call positionally
  behind a probe constant and diffing the emitted term.
- **(bk)** a refutation that names its capability PRECISELY can be reopened the same day —
  two of this session's three boundaries were broken hours after being recorded, by exactly
  the capability the refutation named. And: a fix you cannot EMIT is not a fix.
- **(bl)** the optional CARRIER pair (`iropt_ir` / `iropt_str`), their DIFFERENT gates, and
  the diagnostic that matters most: **a guard that lowers to a LITERAL (`&& false`,
  `if true then`) is the signature of a modelled-away optional — grep the emitted body for
  it before believing a conversion.**
- Still live: **(am)** ASSUME TWO PRODUCERS — it bit twice more this session (the tuple
  return-type map on a MODULE-level function, and the concrete-sibling allowlist);
  **(ai)** never stack whole-file proofs; **(ay)** run BOTH untrusted-emitted and
  shadowed-selfcalls every increment; **(bf)/(bj)** decline a conversion that buys a marker
  with a new hole.
