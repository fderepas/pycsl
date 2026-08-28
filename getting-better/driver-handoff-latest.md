# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-28, RELAUNCH #9 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 530 · grep-substring 555 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep hits
  are one boilerplate module-docstring line repeated across 25 mirror files. Every historical
  absolute figure (the famous "687") is overstated by that 25.
  **Window delta so far: markers 532 -> 530, grep 557 -> 555 — TWO conversions in five gated
  increments**, plus ONE new L-plane oracle, ONE faithfulness capability, and TWO clean
  refutations that landed nothing.
- Ledger **3**, untouched. No new axiom (emitted axioms in pure_ast: 0, unchanged).
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **780 / 763 / 0 / 0**.
  **check-shadowed-selfcalls 50 / 259** (see below — this is NEW). emitted-vacuity `--emit`:
  no NEW erasure, 0 input-blind. Corpus byte-diff **0 over 813/813**.
  `bin/self-annotate-mirror-check.sh` is byte-identical to the HEAD baseline (3 mirrors with
  pre-existing mirror-only defs — that is the standing baseline, not new drift).
- Tree clean apart from the pre-existing user/build dirt (`session.txt`,
  `src/formal-semantics/rocq/.lia.cache` + `.vo` artifacts, untracked `scratchpad/`,
  `prompt`, `prompt.txt`). Leave it alone. `getting-better/.driver-deadline` intact
  (Sep 1 08:24 UTC). 228 commits unpushed; that is deliberate.

## THE HEADLINE FINDING OF THIS WINDOW — a faithfulness hole NO existing gate saw

**`bin/check-shadowed-selfcalls.py` is a NEW L-plane oracle. Run it every increment.**

`check-untrusted-emitted.py` asks whether an un-trusted function is EMITTED AS A DEFINITION.
That is necessary and NOT sufficient. Module 6 lowers `self.<m>(...)` either to the CONCRETE
sibling application `(<class>__<m> self args)` — the caller gets the real body and contract —
or to a synthesized receiver-less `val self__<m>_<n>`, whose result is **UNCONSTRAINED**.
When a CONVERTED method's call sites take the second route, the `let` is emitted, it is
proved, untrusted-emitted is green, the corpus byte-diff is 0, fidelity is unchanged and
emitted-vacuity sees nothing — and **no caller can see a single thing the body computes**.
The erasure is not in any FUNCTION's parameters; it is in the CALL EDGE between two of them.

Measured campaign-wide at the start of this window: **55 converted methods, 267 bypassing
call sites, ZERO concrete applications** — including the whole pure_ast STATEMENT CLUSTER
(`if_stmt`'s `orelse` child was an ARBITRARY array, not the parsed one) and Module 5's
`_csl_to_ir` (92 sites) and `_py_expr_to_ir` (44). Not unsound — an unconstrained result is
an over-approximation, exactly like a `\trusted` stub — but a LOST CONVERSION.

Now **50 / 259**, and the gate RATCHETS at 50. Full detail in lesson (ay).

## WHAT THIS WINDOW LANDED (five gated increments)

1. **`comparison` CONVERTED** (532 -> 531). Re-measured the interrupted in-flight patch from
   scratch; it was INCOMPLETE and L3-tc FAILED. Root cause: the `.append` lowering did
   `arg = self._coerce_to_int(arg)` UNCONDITIONALLY, and `_coerce_to_int` is a pure TEXT
   function that hashes any WhyML string LITERAL — so `ops.append(_N("NotIn")())` emitted
   `Seq.snoc !ops 441879163` while the const-dict sibling emitted the real string. Fixed by
   skipping the coercion on a local already classified `seq string`. New arm
   `IrPyCompare emit_ir (seq string) irlist`; `_pyast_ctor_arms` now parenthesizes a
   multi-word payload type; `_is_string_expr` recognizes a 0-field ASDL singleton; the
   const-dict chain BINDS ITS KEY ONCE (`_CMP[self.advance().string]` has an EFFECT).
2. **The new gate + lesson (ay)** (no count movement).
3. **`array <t>` in the concrete-sibling allowlist** — shadowed 55 -> 50. Two producers
   (`_handle_dotted_call` and `_record_return_sibling_methods`, which supplies the SCC
   ordering edge), then fourteen phase-offset variants over the statement cluster. Proved
   first try. Blast radius 2 of 52 mirrors (pure_ast + Module2_Parser), both re-proved
   SEQUENTIALLY.
4. **`_parse_type_params` CONVERTED** (531 -> 530). Three arms `IrPyTypeVar string iropt_ir`,
   `IrPyTypeVarTuple string`, `IrPyParamSpec string` (thirty-seven total). First beneficiary
   of increment 3 — both call sites now bind concretely. The first proof measured ONE missing
   link: `_name_str` carried only the NON-strict monotonicity clause; strengthened to the
   unconditional `ensures self.i > \old(self.i)` (the exact `expect_op` chain one token kind
   over), PROVED not assumed.
5. **Two clean refutations** — `trailers` and `_line_ends_with_colon`, lessons (az) and (ba).

## Pick up here — in this order

1. **`trailers` (lesson (az))** is the best-costed item on the board: a FOUR-PIECE chain,
   pieces (i) and (ii) already BUILT AND MEASURED WORKING in the spike and reverted with it.
   Rebuild all four in ONE increment ending in `trailers` converting:
   (i) shadow a reassigned `emit_ir` FORMAL PARAM as a ref (`let atom = ref atom in`; add it
   to `pre_decl_vars` but NOT to `_emit_ir_predecl`, so the initializer falls through to
   `init = safe_var`); (ii) `-> "Tuple[List[ExprIR], List[ExprIR]]"` in BOTH return-type
   producers; (iii) type the tuple-unpack TARGETS from the callee's tuple return; (iv) let the
   `irlist` payload binder accept an `array emit_ir` local (`seq_to_irlist (snapshot !args)`).
   Arms already written once: `IrPyCall emit_ir irlist irlist`,
   `IrPySubscript emit_ir emit_ir string`. Pieces (ii)-(iv) also unblock `_call_args` itself.
2. **The OTHER admission gate on the concrete-sibling route.** The remaining 50 shadowed
   methods are shadowed by the GATE, not the type: `_handle_dotted_call` admits the concrete
   route only when `_record_array_fields` is non-empty OR the callee carries an explicit
   `#@ sibling_concrete`, and the emitter mirrors (`statements`, `stmt_control_flow`,
   `expressions`, `functions`, `types`) have no List-of-record field, so the PROXY gate is
   empty for them even though their callees return `string`/`int` — types that have been in
   the allowlist all along. Replace the proxy with a direct predicate, or mark the callees.
   This is the single largest remaining faithfulness item, ~40 methods / ~200 call sites.
3. **`_line_ends_with_colon` (lesson (ba))**: extend the `_union_<fn>_<n>` carrier to a
   declared RECORD arm. Same construction one type-class over; also unblocks any other
   `Optional[<record>]` local.
4. **`global_stmt`** needs the last un-built sub-case of the variable-class-name recognizer:
   `_N(kind)(names=names)` where `kind` is a PARAMETER. The `seq string` payload slot it
   needs for `names` ALREADY EXISTS (increment 1). The construct would be an arm that carries
   the class NAME as a payload with `kind_of` projecting it — weigh that against the
   drift-proof table's discipline before building.

## RECORDED BOUNDARIES — do not re-grind without new capability

- **`_set_ctx(node, _N("Store")())` — [CORRECTNESS].** `emit_ir` is an IMMUTABLE ADT and
  `ctx` IS a modelled field. Blocks `namedexpr_test`, `_comp_target`, `_for_target`,
  `expr_stmt`, `del_stmt`, `_with_item`. Reopening: a functional `set_ctx` in the LIVE SOURCE.
  **NOTE (new, lesson (az)): this does NOT extend to the POSITION attributes.**
  `n.lineno = …` already emits nothing — `emit_ir` carries no position payload, the same
  pre-existing decision that makes `_fin`/`_fin_pos` elisions, and the reason `_subscript`
  converted. Never record a position write as a blocker.
- **`small_stmt` — [HETEROGENEOUS CONVERTED RETURNS]** (lesson (aw)). Blocked by five
  SIBLINGS converted onto harvested RECORD returns. Reopening: migrate `return_stmt`,
  `raise_stmt`, `assert_stmt`, `import_stmt`, `import_from` onto `_PYAST_IRNODE_CTORS` arms
  plus `alias`. The count does not move until the LAST one lands.
- **`trailers` — [COST/SCALE]**, four pieces, all named (lesson (az)).
- **`_line_ends_with_colon` — [MODEL]**, `Optional[<record>]` local (lesson (ba)).
- **`_subscript_item` — [MODEL].** Flow-sensitive narrowing.
- **`_pattern_number`, `atom`, `closed_pattern` — [MODEL].** `Constant(value=…)` needs the
  parser's own number/constant classification.
- **`atom_list` / `atom_brace` / `_dict_rest` / `atom_paren` — [MODEL].** `generators` is a
  list of harvested `comprehension` RECORDS (a payload slot type the family lacks); `keys`
  holds `None` ELEMENTS (optional list elements).
- **`_binop` — [RECOGNIZER].** `_BINOP` is a const dict of TUPLES destructured into two
  locals, then `_N(opname)()` on a LOCAL. Both const-dict sub-cases that ARE built (literal
  and string-valued-dict) do not cover it.
- **`classdef`** (value model); **`_py_stmts_to_ir`** [COST/SCALE]; **`for`-over-array
  termination** (the SOURCE cannot supply a variant).
- The `_Unparser` family (~60 stubs) is blocked by `self.interleave(lambda: …, self.traverse,
  node.names)` — LAMBDA + higher-order function, and `with self.delimit(…)` context managers.
  A fundamental modelling boundary, not a cost one.

## Instrument facts (unchanged, still true, still silently corrupting)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. **The Alt-Ergo pin at `pycsl.py:1318` is stale** (2.6.2 vs installed 2.6.3), so a
   nominally dual-prover run is silently Z3-only. Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`
   EXPLICITLY. Do NOT edit the pin — it is flagged for the user.
4. `check-emitted-vacuity.py` is a false green without `--emit`.
5. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files. `--keep-mlw`
   writes `<source>.mlw` NEXT TO THE SOURCE; delete it before committing.
6. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
7. **A HEAD worktree has no `.venv`**, and `bin/byte-diff-sweep.sh` uses
   `$ROOT/.venv/bin/python3`: without a symlink it emits ZERO files and the diff still
   reports 0. `ln -sfn <repo>/.venv <worktree>/.venv` first.
8. `python3 -u` on every proof, or the log stays empty until the run ends.
9. The Bash tool caps a foreground command at 10 minutes. Run the proof with `nohup … &` and
   WAIT with an `until ! kill -0 <pid>; do sleep 30; done` loop.
10. **NEW (relaunch #9, supervisor-reported): a gate that RAISES before it REPORTS is
    indistinguishable from a gate that found nothing.** `check-shadowed-selfcalls.py` first
    shipped with `os.replace` across a filesystem boundary and died with `Invalid cross-device
    link` before printing anything. Fixed (`shutil.move` + scratch under the repo) AND given
    an INCOMPLETE-POPULATION guard: fewer than 52 emitted mirrors is now a FAILURE, not a
    pass. Apply that guard to any new oracle you write.

## THE FASTEST THING THIS CAMPAIGN KNOWS — use it

**An emit-only run is a 30-second oracle.**
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --no-proof
--keep-mlw` type-checks (L3-tc is ON — this is NOT the `--no-typecheck` sweep, lesson (ww)
does not apply) and leaves the `.mlw` for inspection. BOTH refutations this window cost 30
seconds each. Every capability was designed by porting a body, emitting, READING the emitted
WhyML for facades, and iterating — before spending a minute of proof time.

## The §10.4 RE-PORT PRICE LIST (re-measured where touched this window)

| mirror | goals | wall clock |
|---|---|---|
| any `\trusted` mirror body | — | **0** |
| `frontend/Module2_Parser` | **714** | ~10 min |
| `module6_whyml/types` | 655 | ~8 min |
| `Module6_WhyMLTranspiler` | 706 | ~10 min |
| `frontend/pure_ast` | **1520** (was 1310) | ~25 min |
| `module6_whyml/statements` | 884 | ~15 min |
| `module6_whyml/stmt_control_flow` | 1821 | ~42 min |
| `module6_whyml/functions` | 1175 | ~45 min + vacuity |

A full mirror emission sweep WITH L3-tc (52 files) is ~13 min; the corpus byte-diff sweep
(813 files, `--no-typecheck`, 6 jobs) is ~90 s.

## Method notes this window paid for (full text in wall-lessons.md, (ay)-(ba))

- **(ay)** a CONVERSION can land, prove and pass every gate while NO CALLER sees its body.
  Two DIFFERENT questions: is the definition emitted (untrusted-emitted), and do the CALL
  SITES use it (shadowed-selfcalls). Run both.
- **(az)** `trailers` is a four-piece cost/scale boundary; and the POSITION-ATTRIBUTE plane
  is NOT a wall — only `ctx` is.
- **(ba)** an `Optional[<record>]` local is a different, unsupported shape from
  `Optional[<emit_ir>]`.
- Still live: **(am)** ASSUME TWO PRODUCERS — it bit twice more this window
  (`_record_return_sibling_methods` for the SCC edge, and the call-site half of the
  tuple-of-lists return); **(av)** converting one member of a recursive-descent chain makes
  its WHOLE group need a variant — at fourteen-member scale here, and the multiplier must
  exceed the deepest offset; **(ai)** never stack whole-file proofs (obeyed — pure_ast and
  Module2_Parser proved sequentially); **(aw)** a dispatcher can be blocked by its siblings'
  already-converted RECORD returns; **(ax)** a callee's CORRECTNESS boundary does not
  propagate to its caller — it needs the callee's TYPE and FRAME, not its value semantics.
