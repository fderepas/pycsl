# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-29, RELAUNCH #11 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 518 · grep-substring 543 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep
  hits are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25. Stable across
  three samples.
  **Window #2 delta so far: markers 530 -> 518, grep 555 -> 543.**
  **This session (#11): 521 -> 518 — THREE conversions, TWO certified boundaries, a
  shadowed-selfcall repair wave, and a live-tool faithfulness repair, in four increments.**
- **`bin/check-shadowed-selfcalls.py`: 27 CONVERTED methods / 176 bypassing call sites,
  RATCHET LOWERED to 27** (was 32 / 192 at session start; 50 / 259 at window start). Needs
  `TMPDIR` on the repo filesystem (`TMPDIR=/home/fabrice/git/pycsl/scratchpad`).
- Ledger **3**, untouched. Emitted axioms in pure_ast: **0**, unchanged.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **792 / 775 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known**. Corpus byte-diff **0 over 813/813**.
  `bin/self-annotate-mirror-check.sh` byte-identical to the HEAD baseline.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`, `style.css` — a why3doc artifact from Aug 26).
  Leave it alone. `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC).
  **~75 h remained on the window at handoff time.** Commits are unpushed by design.

## WHAT THIS SESSION LANDED (four increments)

1. **`_binop` CONVERTED (521 -> 520) — the recorded CERTIFIED-BOUNDARY
   [GROUP VARIANT RE-PHASING] is BROKEN.** Both halves built: the `str -> (str, int)`
   PAIR-dict emitter capability (collector + membership disjunction + per-slot unpack ITEs
   + string-local class name), and the SIXTEEN-member expression-group variant re-phasing
   at `13 * (\length(self.toks) - self.i) + <depth>`. TCB net STRICTLY negative: the
   emitted file's abstract-`val` set differs from HEAD's by exactly one line
   (`val _parser___binop` REMOVED, zero added). pure_ast 1931/1931.
2. **Shadowed-selfcall repair wave 4 (32 -> 27 methods, 192 -> 176 sites; ratchet lowered).**
   Two emitter fixes: `#@ sibling_concrete` makes a self-call REAL recursion (the dotted
   `self.<m>` form that `IRScanner.is_recursive` missed), and a NARROW kind-local
   discriminant carve-out so `_rhs_yields_map`'s structural recursion can discharge its
   variant. Seven mirrors re-proved, all SUCCESS.
3. **`_fstring` + `_fstring_format_spec` CONVERTED (520 -> 518).** NEW capability: the
   LITERAL-VALUE carrier `irconst = ICStr string | ICNone` for `Constant.value`. Plus an
   `irlist` slot filled from an `array emit_ir`-returning CALL, and **a live-tool
   faithfulness repair: a module-level call's KEYWORD ARGUMENTS were silently dropped and
   the callee's DEFAULT emitted in their place** — fixed generally, corpus byte-diff 0.
   pure_ast 1985/1985.
4. **`_subscript_item` REFUTED — CERTIFIED-BOUNDARY [UNANNOTATED OPTIONAL-NODE LOCAL]**,
   and the diagnosis REPLACES the recorded one, which was wrong (see below).

New emit_ir arms this window: **fifty-five total**. Added this session: `IrPyBinOp` (via
`_binop`'s conversion — the arm already existed), `IrPyConstant irconst iropt_str`,
`IrPyJoinedStr irlist`, and the `irconst` carrier.

## Pick up here — in this order

0. **THE `iropt_ir` LOCAL — one capability, and it is the named reopening for TWO recorded
   boundaries.** Classify a local as an `iropt_ir` LOCAL when it is assigned a bare `None`
   AND is bound into an `iropt_ir` PAYLOAD SLOT of a `_N(<Class>)(...)` construction in the
   same body: `ref IrONone` pre-decl, `IrONone` / `(IrOSome e)` assignments, the slot
   binding `!x` directly, and a DEFINED total projector
   `let function iropt_val (o: iropt_ir) : emit_ir = match o with IrOSome v -> v
   | IrONone -> IrOther "" end` for an emit_ir-position read. No axiom, ledger unchanged.
   With it plus an `IrPySlice iropt_ir iropt_ir iropt_ir` arm, **`_subscript_item` converts**
   (everything else about it already emits — measured). It is also ONE of the three
   capabilities `_fstring_replacement` needs.
1. **`_fstring_replacement`** — the third f-string member. Needs ladder 0 PLUS: the
   `Optional[str]` local twin (`debug_text = None`, read back under an `is not None` guard
   into the new `irconst` slot), and a TUPLE-TYPED PARAMETER interface for
   `_slice(self, start, end)`, whose `(line, col)` actuals are `pytuple_int_int` against an
   `int`-declared `val`. Its `IrPyFormattedValue` arm is spelled out in the refutation
   commit and was reverted WITH the spike.
2. **The shadowed residue is 27 methods / 176 sites, and 142 of those sites are the two
   Module5 dispatchers** (`_csl_to_ir` 92, `_py_expr_to_ir` 44, `_py_op_to_str` 6) — the
   recorded L2 TYPE-UNIFICATION wall. The `comprehension`-joins-the-family move is the
   shape that answers it: give every handler's input class an `_PYAST_IRNODE_CTORS`-style
   ADT arm so the handlers unify on `emit_ir`. A large, well-defined, funded-window build.
   The long tail's per-method blockers are named in the relaunch-#10 increment-5 commit,
   PLUS one new one from this session: **a `-> bool` callee emits as a `bool`-returning
   logic symbol while the concrete call site coerces `<> 0` for an int**
   (`_is_final_annotation`) — a return-type coercion gap at the concrete route.
3. **`small_stmt`** — still [HETEROGENEOUS CONVERTED RETURNS]. Its five siblings are
   CONVERTED onto harvested RECORD returns; migrating them onto `_PYAST_IRNODE_CTORS` arms
   (plus `alias`) is a well-trodden move now. The count does not move until the LAST one
   lands.
4. **`strings`** — the last f-string-cluster member and the hardest: `b"".join(...)` over a
   BYTES value, a `kinds` SET, and tuple-in-list parts. Not probed.

## RECORDED BOUNDARIES — do not re-grind without new capability

- **`_subscript_item` — [UNANNOTATED OPTIONAL-NODE LOCAL]** (RE-DIAGNOSED this session; the
  old "flow-sensitive narrowing / `return lower`" record was WRONG — `return lower` emits
  fine). See ladder 0 for the exact recipe, and the stub's own comment.
- **`_fstring_replacement` — [OPTIONAL-LOCAL FLOW + TUPLE-PARAM INTERFACE].** See ladder 1.
  Its `format_spec is None` guard lowered to the literal `false` — a WRONG branch
  condition, worth remembering as the shape of this failure.
- **`_fin` — [ERASURE-LEDGER], a JUDGEMENT not a wall (lesson (bd)).** Proved 1612/1612 and
  reverted anyway: it trades a COUNTED marker for an UNCOUNTED erasure-ledger entry and
  buys nothing. Do not re-spike; read (bd) and (bf) §3 first.
- **`_set_ctx(node, _N("Store")())` — [CORRECTNESS].** `emit_ir` is IMMUTABLE and `ctx` IS
  modelled. Blocks `namedexpr_test`, `_comp_target`, `_for_target`, `expr_stmt`, `del_stmt`,
  `_with_item`. Reopening: a functional `set_ctx` in the LIVE SOURCE. The POSITION plane is
  NOT part of this (lesson (az)) — only `ctx`.
- **`small_stmt` — [HETEROGENEOUS CONVERTED RETURNS]** (lessons (av)-(ax)). Ladder 3.
- **`_pattern_number`, `atom`, `closed_pattern` — [MODEL].** `Constant(value=…)` needs the
  parser's own number/constant classification. **The `irconst` carrier built this session is
  the frame for it**: add an `ICNum`-shaped arm and a faithful `_parse_number` interface and
  these reopen. Until then a non-string, non-None literal DECLINES fail-closed, which is
  what keeps them honest.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION].** Ladder 2.
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
| `frontend/pure_ast` | **1985** | ~36 min |

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

## Method notes this session paid for (full text in wall-lessons.md, (bh)-(bj))

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
- Still live: **(am)** ASSUME TWO PRODUCERS — it bit twice more this session (the tuple
  return-type map on a MODULE-level function, and the concrete-sibling allowlist);
  **(ai)** never stack whole-file proofs; **(ay)** run BOTH untrusted-emitted and
  shadowed-selfcalls every increment; **(bf)/(bj)** decline a conversion that buys a marker
  with a new hole.
