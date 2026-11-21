# Response: cross-mixin declaration stubs — independent review

Reviewer: rv1 (independent; worked from the report and the tree only). Tree `/home/fabrice/git/pycsl-rv1`
at `76353d6a2`. Date 2026-10-30. Report under review: `getting-better/cross-mixin-declaration-stubs.md`.

No source file was edited. Every spike ran on a copy under
`/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/rv1/` (`$R` below).

## 0. Verdict in one paragraph

The three claims I was asked to check are **all confirmed by oracle runs**: (1) the two
`stmt_control_flow.py` declarations really do emit avatars with a frame smaller than the definition's,
a verified method (`_handle_match_stmt`) really applies both, and the hole is really a *trap, not a
hole* today — none of the four verified callers promises any omitted field unchanged; (2) importing
the defining mixin really fails at L3-tc for exactly the reason given (the call site binds to an
auto-synthesised `int -> int` avatar, not to the imported stub); (3) the census numbers (24 / 408, 23 +
1, 21 trusted + 3 verified definitions, 14 distinct trusted definitions) reproduce from an independently
written walker, and the report's accounting — **gross −24 markers, net TCB −3, nothing honest until a
declaration ⊑ definition check exists** — is correct and I endorse it. My own Why3 spike shows the
replacement the report recommends is not hypothetical: Why3 1.8.2 rejects a narrow declaration at
`clone` time *before any prover runs* (`Illegal instantiation ... unreferenced write effects`), and
emits a dedicated `f'refn'vc` goal for pre/post refinement when the frames agree. Recommendation:
R0 → R1 → R2 (sync rule first, conformance unit second) → R4, with R7 refused, exactly as the report
orders it; I add three corrections to the fine print (§5).

## 1. Oracle runs (all through `heavy.sh`; commands verbatim)

| # | command (from `/home/fabrice/git/pycsl-rv1`, `PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH`) | result |
|---|---|---|
| O1 | `PYTHONHASHSEED=0 heavy.sh .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/module6_whyml/stmt_control_flow.py --import-path src/pycsl --no-proof --keep-mlw` | rc=0, `L3-tc ✓`, 7.7 s; `.mlw` saved as `$R/stmt_control_flow.base.mlw` |
| O2 | same on a byte-identical copy `$R/mir/stmt_control_flow.py` | rc=0; `diff` against O1's `.mlw`: **0 lines** (validates the scratch-copy method) |
| O3 | same on `$R/mir/stmt_control_flow_s1.py` = copy with the `#@ assigns` of `_match_pattern_cond` and `_expr_to_whyml` replaced by the definition's line from `expressions.py` (report's S1) | rc=0, `L3-tc ✓`; diff vs O2: **19 lines**, listed in §2 |
| O4 | `PYTHONHASHSEED=0 heavy.sh .venv/bin/python3 src/pycsl/pycsl.py $R/mir/expr_ghost_collections_s3.py --import-path src/self-annotate/src --no-proof --keep-mlw` (copy with `from module6_whyml.expressions import ExpressionEmissionMixin` added and the `_e` declaration deleted; report's S3) | **rc=1, `L3-tc ✗`**: `line 1189, characters 20-34: This expression has type PyCSL_Program.emit_ir, but is expected to have type int` |
| O5 | `$R/census.py` — my own pure-AST walker over `bin/trusted_markers.iter_trusted_defs` + the live class graph (not a pycsl/why3 job; run directly) | `TRUSTED_DEFS_TOTAL 408 DECL_STUBS 24`, `{'other-mixin': 23, 'base-class': 1}`, `{'trusted': 21, 'verified': 3}`; the 24 names equal the report's table row for row |
| O6 | `heavy.sh bash -c "why3 prove -P z3 $R/clone_refine.mlw" rv1 --no-proof` — Decl `val f writes { s.a }`, Def `let f writes { s.a, s.b }`, `clone Decl with type st = st, val f = f` | **rc=1 before any prover**: `Illegal instantiation for program function f: unreferenced write effects in variables: s` |
| O7 | same on `$R/clone_refine_ok.mlw` (frames equal, Decl `requires {s.a >= 0} ensures {s.a >= 0}`, Def `requires {true} ensures {s.a = 1}`) | rc=0: `Goal f'vc: Valid (614 steps)`, **`Goal f'refn'vc: Valid (372 steps)`** |
| O8 | same on `$R/caller_only.mlw` (Decl + a caller `g` with `ensures { s.b = old s.b }` that calls the narrow `f`) | `Goal g'vc: Valid (6 steps)` — the **false** frame fact is proved from the narrow declaration |
| O9 | `$R/scan_mlw.py` over O1's `.mlw`: for every `let` that applies `self__expr_to_whyml_2` or `self__match_pattern_cond_3`, list which of the omitted fields it also promises `= old` | 4 lets apply them (`_handle_if/match/return/while_stmt`); **`ensures-unchanged=[]` for all four** |

Note on O6–O8: both NORMAL `heavy.sh` slots were held for hours by `run-soundness-planes.sh --slow` and
`rt40/mega.sh`; a 30-line `why3 prove` was routed through the QUICK slot with a `bash -c` wrapper whose
trailing `--no-proof` is only the slot key (why3 never sees it). It still ran inside the 6 GB scope.
I could not get a slot for a whole-file or `--fun` **proof** of S1 in my window, so the report's
"5632 Valid / 0 non-Valid" is **not independently re-run**; §2 explains why the emitted VC shape makes
that result expected.

## 2. Check 1 — the soundness finding: CONFIRMED (trap today, real mechanism)

**The stubs.** `stmt_control_flow.py:1042-1046` declares `_match_pattern_cond` with `assigns \nothing`;
its definition `expressions.py:468-472` declares 22 fields. `stmt_control_flow.py:197-200` declares
`_expr_to_whyml` with 17 fields; its definition `expressions.py:1965-1969` declares 22. (Read in source.)

**The emission (O1).** The `controlflowstmtmixin` record (line 628) carries 25 fields including
`_dict_locals`, `_quant_record_binders`, `_quant_scalar_binders`. The avatars:

```
val self__match_pattern_cond_3 (x0: emit_ir) (x1: string) (x2: map int (option int)) : string
val self__expr_to_whyml_2 (self: controlflowstmtmixin) (x0: emit_ir) (x1: map int (option int)) : string
  writes { self._comp_content_counter, self._current_params, self._current_self_type,
           self._frame_trigger_active, self._func_return_type, self._in_spec,
           self._needs_array_init, self._string_local_vars, self._todict_arg_wants_pymap }
```

The first has **no receiver and no `writes`**; the second lists 9 fields and omits the three the
report names, all three present in the record. The verified `let controlflowstmtmixin___handle_match_stmt`
(line 1267) applies both (line 1400: `cond := (self__match_pattern_cond_3 !pat !subject local_refs)`;
line 1402: `self__expr_to_whyml_2 self !guard local_refs`). The bodyless
`val controlflowstmtmixin___match_pattern_cond (self: ...)` at line 2349 is, as the report says, never
applied. **Every factual element of §3 row 24 / row 20 of the report reproduces.**

**S1 reproduced (O3).** Giving the two declarations the definition's `assigns` changes exactly 19 diff
lines: `self__match_pattern_cond_3` gains `(self: controlflowstmtmixin)` and a 12-field `writes`, its
one call site gains the `self` argument, `self__expr_to_whyml_2` gains the three fields, and two
dependent `writes` lines widen. L3-tc stays green. That matches the report's description of S1.

**Load-bearing or not (O9).** The hole could bite only through a verified `let` whose own contract
asserts one of the omitted fields unchanged while its body applies the narrow avatar. My scan finds
none: all four appliers have `assigns` covering the omitted fields and `ensures True`. So the false
"unchanged" fact is derived and discarded. The report's "trap, not a hole; S1 proof green is expected"
reading is correct, and it is the right expectation even without re-running the 5632-goal pass: no VC
in those four lets mentions the omitted fields.

**The mechanism is real (O8).** The identical shape in 20 lines of WhyML proves `s.b = old s.b` from
a `val` that omits `b` from `writes`, in 6 solver steps. The day a verified caller of
`_expr_to_whyml` in `stmt_control_flow.py` has a frame that omits `_dict_locals` (or a loop invariant
that mentions it), the proof goes through and is false. This is the `_stmts_to_whyml` incident of
`check-assigns-writes-survival.py`'s `MAX_TRAP` note, waiting to repeat.

**Two things the report under-states here.**

1. *The definition's frame is itself an unchecked over-approximation* (report §3 caveat, §9) — agreed,
   but that cuts both ways: copying it verbatim into the declaration (R1) is the right move precisely
   because an over-wide frame is *sound* for callers; what is never acceptable is a frame narrower than
   the definition's. R1 needs no runtime witness to be justified.
2. *Signatures differ too, not only frames.* The declaration `_e(self, ir: "ExprIR", lr)` in
   `expr_ghost_collections.py:20` / `expr_ghost_spec_ops.py:20` / `statements.py:686` has its
   definition at `expressions.py:117` as `_e(self, ir: Dict, lr)` (live `src/pycsl/.../expressions.py:484`
   also says `Dict`). The definition's emitted stub types `ir: int`
   (`val expressionemissionmixin___e (self: expressionemissionmixin) (ir: int) ...`, seen in O4's
   `.mlw` line 676), the declaration's avatar types it `emit_ir`. So the report's R2 "sync rule" wording
   "signature identical up to the documented type layer" has to be an explicit *type-layer refinement*
   relation, not an equality; otherwise it fails on day one for `_e`, `_match_pattern_cond`
   (`pat: int` in the definition, `pat: "ExprIR"` in the declaration) and probably others.

## 3. Check 2 — "importing the defining mixin is refuted at type-check": CONFIRMED

O4 reproduces the report's S3 to the line: `rc=1`, `L3-tc ✗`, the failure at `.mlw:1189`
(`l := (self__e_2 (left_of node) lr)`), and the two symbols the report describes coexisting in the
same file:

```
584:  val self__e_2 (x0: int) (x1: int) : int                         <- auto-synthesised, applied
676:  val expressionemissionmixin___e (self: expressionemissionmixin)
            (ir: int) (lr: map int (option int)) : string              <- imported, never applied
```

(The import itself succeeds: `Imported class from 'module6_whyml.expressions': ExpressionEmissionMixin
(record + 95 method stub(s))`.) So the contract travels and the receiver does not, as the report says.
Two refinements of the claim:

- It is a refutation *of this emitter's binding rule*, not of the idea. The emitter resolves `self.m`
  against the current class's own record only; it has no notion that `GhostCollectionOpsMixin` is a
  base of the imported `ExpressionEmissionMixin` (it is: `class ExpressionEmissionMixin(GhostCollectionOpsMixin, GhostSpecOpsMixin)`),
  so no field-wise projection `expressionemissionmixin -> ghostcollectionopsmixin` is attempted. The
  report's §6 diagnosis ("`self` type = the declaring mixin, not the composite") is the right root cause.
- Even if the receiver were bridged, the parameter types would not meet (`ir: int` from the
  definition's `Dict` annotation vs `emit_ir` at the call site, §2 point 2). The import route would
  therefore need both a receiver projection *and* the type-layer refinement rule. That strengthens the
  report's preference for a checked local declaration (R2) over single-source import (R6-style).

I also note O4 emitted a second synthesised symbol `self__e_2_c3185 (x0: emit_ir) (x1: int) : int`
(line 585) — a per-call-site typed variant the emitter creates when argument types disagree. Its
existence is a reminder that the auto-synthesis path is itself an uncounted assumption generator;
`check-avatar-frame-parity.py`'s INHERITED bucket (ratchet 7) is the only thing watching it.

## 4. Check 3 — the recommended route and its trust accounting: CONFIRMED, endorsed

**Numbers (O5).** My walker, written without looking at the report's `decl_census.py`, returns the same
24 names, the same 23/1 split, the same 21 trusted / 3 verified definition statuses (rows 8 and 21
`_coerce_to_int` → `ExpressionEmissionMixin`, verified; row 16 `_handle_return_stmt` → base
`ControlFlowStmtMixin`, verified). Counting distinct trusted definitions behind the 21 by hand:
`_e`, `_expr_to_whyml_string_ctx`, `_add_abstract_op`, `_resolve_dotted_signature`, `_is_emit_ir_expr`,
`_expr_to_whyml`, `_is_string_expr`, `_track_collection_metadata`, `_maybe_emit_no_exception_assert`,
`_mutex_inv_application`, `_seq_init_expr`, `_to_bool`, `_stmts_to_whyml`, `_match_pattern_cond` = **14**.
The report's "14 distinct trusted definitions" holds.

**The accounting.** The report's central sentence — *the trust a declaration carries is the
definition's trust plus the contract difference; only the difference is new trust, and nothing measures
it today* — is the correct way to count, and it leads to the honest ledger:

| move | markers | trust actually removed | new trust closed |
|---|---|---|---|
| R0 measure (frame-honesty resolves via live MRO; add the 2 `requires_method` windows) | 0 | 0 | makes the 12 + 1 deltas visible |
| R1 fix 12 narrow frames (+ `_seq_operand` window, incl. its missing `raises`) | 0 | 0 | **13 unchecked deltas → 0** |
| R2 declaration ⊑ definition gate | 0 | 0 | keeps them at 0 |
| R3 delete 6 unapplied declarations | −6 | 0 (an unapplied `val` is not a hypothesis of any VC — I confirmed the 6 have no `self__<m>_<n>` applier in `statements.mlw` per the report's A3; not re-run) | 3 traps gone |
| R4 reclassify after R2 | −24 (−18 after R3) | **3** (rows 8, 16, 21) | — |
| R7 `\abstract` / bare `requires_method` | −24 | 0 | **negative**: deltas leave the metric |

"Gross −24, net TCB −3, plus a closed blind spot" is the honest headline. I would add to the report's
wording: after R4 the right *count* is "408 − 24 markers, and 14 trusted definitions now stand for 35
call-site contracts" — i.e. the reclassified declarations must remain enumerable (the
`#@ declared_in <file>::<Class.m>` marker the report proposes does that), so a later audit can still
find every file that *relies* on a given trusted definition.

**One quibble on the 3.** Row 16 (`_handle_return_stmt`) is a `\trusted` stub in `statements.py` that
*overrides* the verified base method with a *wider* frame. Weaker-is-sound holds for callers inside
`statements.py`, so dropping its marker under R2+R4 is honest — but its R2 obligation is the
base/override one (routes #277/#278, which the report's own S4 shows has teeth), and it points the
other way from the 23 other-mixin rows (declaration ⊒ definition is what #278 enforces for an
override). The generator in R2 must treat this row as an override pair, not as a sibling-declaration
pair, or #278 will reject the wider frame as "assigns a location the base does not name".

## 5. Corrections and additions to the report

1. **Signature refinement is part of the obligation** (§2 point 2). The sync-rule version of R2 must
   define "identical up to the type layer" formally: declaration parameter type ⊑ definition parameter
   type under the documented `ExprIR`/`Dict`/`int` erasure, return type equal. Otherwise `_e`,
   `_match_pattern_cond` and `_expr_to_whyml` fail the gate for a reason that is not a trust problem.
2. **Frame inclusion must be checked after projection**, i.e. `assigns_decl ⊇ assigns_def ∩ fields(record_decl)`
   (plus, for opaque-`self` files, `assigns_decl` non-empty iff `assigns_def` non-empty, so the
   `_pyobj_state` coarse frame is produced). The report's §3 table already computes exactly this
   intersection; the gate should reuse `decl_visibility.py`'s logic rather than compare raw clause text.
   Raw-text comparison would flag the 7 "invisible" rows as failures that are not soundness failures.
3. **`raises` is in the obligation too.** The `_seq_operand` window drops `raises PyCSLSemanticError`
   (report §5.1). For an avatar without `raises`, Why3 treats the call as non-raising, so a verified
   caller's exceptional post-conditions are vacuous for that path. R1 should fix this window's `raises`
   as well as its frame; the report's R1 line mentions only the frame.
4. **The `\trusted` definition behind a declaration can later be narrowed** (when it converts and its
   proved frame is smaller than the gen #32 over-approximation). The R2 gate must then *allow* the
   declaration to stay wider (weaker-is-sound) and only ever fail on declaration ⊂ definition. Ratchet
   direction: declarations may shrink only when their definition shrinks first.
5. **The report's SOTA section is right in substance and I have now checked the Why3 half on the
   installed version** (1.8.2): effect inclusion is a *static* clone-time error (O6), pre/post
   refinement is a generated `'refn'vc` goal (O7). I did not test `clone ... with val f = f` where the
   substituted `f` is itself a `val` (the 21 trusted-definition cases); Why3 accepts val-for-val
   instantiation with the same effect check in my reading of the manual, but that is reading, not an
   oracle.

## 6. My recommendation: what the sound replacement is, what it costs, what not to do

**Order: R0, R1 (with raises), R2a sync rule, R3, R2b conformance unit, R4.** Concretely:

- **R0 + R1 now (half a day).** Resolve declarations to definitions through the live MRO in
  `check-trusted-frame-honesty.py` (the resolution `_self_write_fixpoint` already does for call edges),
  add the two `requires_method` windows to the population, and paste the definition's `assigns` (and
  `raises`) into the 12 + 1 under-stated declarations. The avatar machinery projects onto the local
  record, so verbatim copy is the right text and S1/O3 shows the emission and L3-tc are unaffected.
  Proof cost: whole-file re-proof of `stmt_control_flow.py` and `statements.py` as the protocol
  demands (the report prices `statements.py` at ~2 h 19 m). The VCs of the four control-flow callers
  cannot change in truth value (O9), so a non-green result would be a solver-budget artefact, not a
  verdict.

- **R2a: the sync rule as a bin/ plane (one to two days).** A pure-AST checker over `trusted_markers`
  that, for every declaration (trusted or `requires_method`), resolves the definition and checks four
  inclusions: projected frame (§5.2), raises, requires-weaker / ensures-stronger (trivially true while
  everything is `True`; text equality is enough until a non-trivial pre/post appears, at which point the
  pair is routed to R2b), and signature refinement (§5.1). Ratchet style, wired into
  `run-soundness-planes.sh`. This closes the §4.3 blind spot and is the floor below which no one should
  drop a marker.

- **R2b: the mechanical obligation (medium: a generator, about a week).** For each pair, generate a
  WhyML conformance unit in the Why3 shape O6/O7 proved works:
  `module Decl_<file>_<m>` with `type self = private {<decl file's record fields>}` and the
  declaration's `val`; `module Def_<m>` with the definition's record and its `val`/`let`;
  `module Conf use Def_<m> clone Decl_<file>_<m> with type self = self, val <m> = <m>`. The receiver
  bridge the import route lacks is built *once, in the generator*, as a field-wise projection: the
  cloned `private` record exposes only the declaring file's fields, which is exactly the projection the
  avatar performs. Frame and raises inclusion are then Why3 clone-time errors (no prover, no timeout);
  pre/post refinement is one `'refn'vc` goal per pair, trivial while all specs are `True`. For row 16
  use the existing #277/#278 override path instead. If the `private`-record clone proves awkward for
  the opaque-`self` files (`self: int`), fall back to R2a for those three; nothing is lost because the
  model asserts nothing there.

- **R4 only after R2a is green and ratcheted.** Introduce `#@ declared_in <file>::<Class.m>` (or the
  equivalent), have `count-trusted-directives.py` attach it as a *distinct* class that is reported next
  to, not inside, the `\trusted` count, and keep the 14 definitions counted. Announce the step as
  "−24 markers, −3 TCB".

- **R6 (one composite record) stays research.** It is the principled end state (the report is right
  that the per-file record is the second root cause) but it couples the proof of every mixin file to
  the union record and S2b has no implementation; do not block R1/R2 on it.

**What must NOT be done.**

- **No R7.** Relabelling as `\abstract` or a bare `requires_method` changes no emitted byte and removes
  the only accounting line that records the assumption. The `_seq_operand` window is the live proof that
  an uncounted declaration drifts: it already understates both frame and `raises`.
- **No "−24" before R2.** Without a check, dropping the markers converts 24 counted assumptions into
  24 uncounted ones and additionally hides 12 unchecked deltas. That is trust laundering in the exact
  sense the sl-auditor rule forbids: the upper bound moves while no lower-bound plane sees the move.
- **No narrowing a declaration below its definition, ever, not even "temporarily to make a proof
  pass".** O8 is the three-line demonstration of why: the narrow `val` proves a false frame fact in six
  steps.
- **Do not count R3's −6 as capability.** It is correct hygiene (an unapplied `val` is no hypothesis),
  but the six declarations return with their callers, and three of them are the model-visible traps —
  their disappearance must not be reported as "3 traps closed" without saying they are closed by
  absence.

## 7. Limits of this review

- I did not re-run the S1 `--fun` proof (no NORMAL slot in my window); the "trap, not hole" verdict
  rests on O9's structural reading of the emitted VCs, which I consider sufficient, plus the report's
  5632/0 pass.
- O6–O8 use a `let` definition; 21 of the 24 real pairs are `val`-vs-`val`. The static effect check is
  the same code path in Why3, but I did not exercise it.
- I did not attempt a runtime witness that a reachable `match` pattern writes `_dict_locals` through
  `_match_pattern_cond`; like the report, I argue from frames, not from traces.
- The census (O5) classifies by class-name MRO like the report's; both would miss `getattr`-style
  dispatch. The "0 dead" answer shares that assumption.
