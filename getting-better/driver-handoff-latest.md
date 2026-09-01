# HANDOFF — read this FIRST on relaunch (rewritten 2026-09-01, RELAUNCH #20 worker)

## Why this handoff is short

Relaunch #20 got a **~70-minute window**, not a 96-hour one: the supervisor relaunched me with
the deadline (`getting-better/.driver-deadline` = 1788251064, Sep 1 08:24 UTC) already ~73
minutes out. I deliberately did NOT start a multi-hour build. One increment landed, it is a
**re-priced CERTIFIED-BOUNDARY correction on the largest single lever left on the count**, and
the rest of the window went into leaving this file accurate. Relaunch #19's handoff (the long
one) is still substantially valid — read it at `git show a292802b:getting-better/driver-handoff-latest.md`
or just `git log` back one revision of this file; everything under its "Instrument facts",
"Recorded boundaries carried forward" and "Method notes" sections still holds.

## State, verified from the surface at end of session

- **Count: MARKERS 491 · grep-substring 516 · offset 25 · unattached 0. UNCHANGED.**
  From `bin/count-trusted-directives.py`, never a hand-rolled grep.
- Ledger **3**. Emitted axioms **0**. Corpus **814** files.
- Fidelity at the standing baseline: `check-self-annotate-sync.sh` **2 DIVERGED**
  (`module6_whyml/expressions.py::_handle_var_expr`, `module6_whyml/stmt_control_flow.py::_handle_for_stmt`);
  `self-annotate-mirror-check.sh` **3 mirrors drifted, exit 1 — that IS the baseline**.
- `bin/check-shadowed-selfcalls.py`: **13 methods / 33 sites, ratchet 13** (unchanged; this
  session's edit was a comment, emission byte-identical).
- `bin/check-trusted-frame-honesty.py`: **trusted 0 model-visible / 70; converted 2 / 68**
  (unchanged, same reason).
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, `prompt*.txt`,
  `scratchpad/**`). `getting-better/.driver-deadline` intact and UNTOUCHED.
- **58 commits local-only. Nothing was pushed. Do not push.**

## WHAT THIS SESSION LANDED — one increment, `fb2f9fe8`

**The `_Unparser` family boundary's reason was wrong AGAIN, and the reason it replaced was
16 hours old — written by this same campaign (relaunch #19 inc8, `ebe049de`).**

inc8 said the blocker is that `_Unparser.write(self, *text)` is VARIADIC, and named the
reopening capability as *"a `*args` parameter model — a `seq string` formal, with the call
site materializing its actual arguments into it."*

**THAT CAPABILITY ALREADY EXISTS AND ALREADY WORKS END-TO-END.** Annotating the vararg
(`def write(self, *text: str)` in the mirror AND in the live `src/pycsl/frontend/pure_ast.py`)
with **ZERO emitter changes** immediately emits

    let _unparser__write (self: _unparser) (text: seq string) : unit
      = let _ = (self__source_extend_1 text) in ()

with `val self_write_1 (x0: seq string) : unit`, and the emitter materializes every call site
itself as `Seq.cons <arg> (Seq.empty: seq string)`. Module5's `_cur_func_vararg_str`
(`Module5_IREmitter.py:4966-4977`, `:5087-5099`, `:5177-5179`) and Module6's
`functions._vararg_str_param` (`functions.py:38-43`, `:344-352`, `:7406-7411`) already do all of it.

**THE REAL WALL IS THE [STRING-MODEL SPLIT] AT THE MATERIALIZATION SITE — measured, not argued:**
- **40 of the 56** write call sites in the converted part of the class become **REAL Why3
  STRING LITERALS** (`Seq.cons " in " (Seq.empty: seq string)`) where they were opaque hash
  ints (`self_write_1 260070937`). **That is a large fidelity gain nobody in this campaign had
  ever seen**, and it is evidence about the string model well beyond `_Unparser`.
- **The other 16** come from INT-MODELLED sources: 7 node-field projectors
  (`get_name`/`get_id`/`get_attr`/`get_arg`), 3 `str_concat`-over-int-locals, `replace_3`,
  `repr_conv`, and the int-typed params `extra` / `start` / `py_end` / `!operator`. Each is a
  hard `seq string` vs `seq int` Why3 type error. **L3-tc fails on the first**,
  `_write_str_avoiding_backslashes`, whose `quote_type`/`string` locals are ints because
  `_str_literal_helper` is still a stub returning ints.
- **No coercion bridges it.** `str_hash_op` goes int-ward and is not invertible; an
  int→string direction would be a fiction.

## THE #1 ITEM FOR THE NEXT WINDOW — a BUILD, not a boundary

**Lower an UNANNOTATED vararg to a `seq int` (pyval) formal instead of DROPPING it**, rather
than lowering an ANNOTATED one to `seq string`.

- **Why it wins:** it removes the split entirely. The vararg then lives in the SAME model as
  every other value in `pure_ast.py`; all 56 sites materialize as `Seq.cons <int> Seq.empty`;
  the write payload stops being discarded; and no source file needs a (dishonest) annotation.
- **Where:** exactly the three surfaces named above — Module5 record the vararg name when it
  has NO annotation (a sibling field to `vararg_str_param`, e.g. `vararg_pyval_param`),
  Module6 `functions._param_type_str` return `(safe: seq int)`, and the call-site
  materialization in `functions.py:7406-7411` emit `(Seq.empty: seq int)`.
- **KNOW THE COST BEFORE YOU START — it is CORPUS-AFFECTING.** The `: str` gate exists
  *precisely* so that every corpus and `pycsl_lib` function with a plain `*args` stays
  byte-identical (the comments at `Module5_IREmitter.py:5095-5096` and `functions.py:41-42`
  say so in as many words). Lifting it is therefore an **M1-discipline build**: the byte-diff
  must be EXACTLY the vararg correction, and every affected program must re-prove 0 non-Valid.
  Budget it as a real increment, not a one-liner.
- **Payoff: 51 of the 491 markers** — the largest single lever left. `pure_ast.py` holds 96 of
  the 491 in total.
- **Second-order:** the same annotation experiment showed the emitter WILL emit real Why3
  `string` literals when a `string`-typed sink demands them. Worth asking, separately, how much
  of the int-hash string model is a default rather than a necessity.

## Then, in this order (carried forward from #19, still valid)

2. **`ControlFlowStmtMixin._handle_return_stmt`** — the ONE non-constructor model-visible false
   frame left (18 fields via-callee). Expect relaunch #19's landing-5 shape: find which
   shadow/oracle erases the write, make it carry its receiver and its frame, then let
   `scratchpad/w3/fix_assigns.py` converge. `module6_whyml/stmt_control_flow` is 1846 goals, ~45 min.
3. **`scratchpad/w3/fix_assigns.py` IS THE REUSABLE TOOL.** It converges `#@ assigns` /
   `#@ raises` / `#@ \diverges` against Why3's own error text. Point its `MIR` constant at
   another mirror. **Every wall whose recorded reason is "the effect summary cannot be made
   exact" should be re-tested with it FIRST.**
4. **The `pyx_view` ADT redesign / record AST model** remains the soundness floor under the
   object-identity question. Obstacle: `pure_ast`'s node classes are SYNTHESIZED AT IMPORT by
   `type(name, (base,), body)` from `_NODE_SPEC`.
5. `val function csl_to_ir_op` is **CLOSED** (relaunch #19). Do not re-open it.

## Recorded boundaries carried forward — do not re-grind without the named capability

- `_csl_to_ir` is **BROKEN**; strike it from any ladder that still lists it.
- **The attribute-store third horn** works and is axiom-free; blocked on OBJECT-IDENTITY INJECTIVITY.
- **`crosscheck_ir.pairwise`** — spiked and working, demand NIL.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]** (33 sites / 13 methods).
  Note it is the SAME disease as the `_Unparser` finding above, one type-family over.
- `_fin` / `_max_end` / `_fin_block` — [ERASURE-LEDGER]; `node(self, name, start_tok, **kw)` — [MODEL];
  `_slice`; **`Module2_Parser`'s contract-expression cluster** (TERMINUS); `_decode_escapes` /
  `_decode_string`; `identifiers.whyml_ident` / `stable_hash`; `struct_format.parse_format` /
  `calcsize`; `proof2why3/normalize`'s whole file (regex).
- `pure_ast._Parser.error` / `.unsupported` — they DO convert (491→489) but
  `bin/check-emitted-vacuity.py --emit` reports 2 NEW erasures. **REOPENING: a modelled message
  payload on the raise** — the same decision `_fin` needs.
- **`exception_model.bases_closure`** — the wall is the VALUE MODEL, not termination.

## Instrument facts — unchanged and still load-bearing

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. `--import-path src/pycsl` is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. `.gitignore` has `*.mlw` — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof. A run can sit at ZERO prover results for 50 minutes and then
   flush 1500 — do NOT conclude "stuck"; check for live `alt-ergo`/`z3` children.
7. A FAILING `pycsl.py` run is much FASTER than a passing one. **Emitting `pure_ast.py` alone
   with `--no-proof --keep-mlw` takes 1.8 SECONDS** — a vastly cheaper probe than a sweep.
8. BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING. `scratchpad/w3/prove.sh` /
   `prove_wt.sh` prove a list sequentially; `bin/byte-diff-sweep.sh` runs `--no-typecheck`.
9. `scratchpad/w2/sweep.sh <abs-root> <abs-outdir>` emits all 52 mirrors WITH L3-tc in ~35 s
   and writes an md5 manifest. **PASS ABSOLUTE PATHS.**
10. `--fun` CANNOT probe `Module5_IREmitter` at all — whole-file or nothing.
11. A git worktree is the right place for a spike. Sync with
    `git checkout --detach $(git -C <main> rev-parse HEAD)`.
12. A PROOF TRANSFERS BETWEEN TREES WHEN THE EMISSION MANIFEST IS IDENTICAL.
13. The Alt-Ergo pin at `pycsl.py:1318` is stale. Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`
    EXPLICITLY; do NOT edit the pin.
14. `grep` here is ugrep and MISBEHAVES on `driver-progress.log`. Use python, via a
    `python3 - <<'PYEOF'` heredoc, never inline `-c`.
15. `cd` PERSISTS ACROSS A COMPOUND BASH COMMAND. Use absolute paths after any `cd`.
16. **NEVER put a `\trusted` marker LITERAL in a mirror comment** — it counts as a MARKER.
17. `TMPDIR=/home/fabrice/git/pycsl/scratchpad` for `bin/check-shadowed-selfcalls.py`.

## The method note this session paid for

**A REOPENING CAPABILITY IS A CLAIM, AND IT DESERVES THE SAME SUSPICION AS THE BOUNDARY IT
PRICES.** This campaign has now learned seven times that a recorded boundary's *reason* is
usually wrong. It had not yet checked the other half of the record. The `_Unparser` capability
had been named 16 hours earlier, by this same campaign, in good faith — and it was already
built. **The first move against any named capability is to try it, not to scope it.** It cost
one 1.8-second emission to find out.
