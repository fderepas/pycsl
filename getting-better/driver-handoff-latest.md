# HANDOFF — read this FIRST on relaunch (rewritten 2026-09-01, RELAUNCH #21 worker)

## What #21 got, and what it did with it

A **~65-minute** window (same deadline `.driver-deadline` = 1788251064). No multi-hour build was
started. #20's lesson — *a reopening capability is a claim; TRY it before you scope it* — was
applied to **#20's own ladder item 1a**, and it paid off exactly the same way.

## THE RESULT — ladder 1a is BUILT, and its price was wrong too

**`e140e4d8` + `935c0cee`. Unannotated `*args` now lowers to a `seq int` (pyval) formal instead
of being DROPPED.** #20 priced this as *"CORPUS-AFFECTING … an M1-discipline build … budget it as
a real increment, not a one-liner"*.

**Measured:**
- It is **~40 lines** across the three surfaces #20 named, plus **two** #20 did not.
- **The corpus blast radius is ZERO.** Exactly THREE non-mirror files in the whole tree have an
  unannotated vararg (`test-suite/corpus/python-reference/0209.py` `__aexit__`,
  `…/0093.py` `__exit__`, `src/pycsl_lib/typ/__init__.py` `__call__`) and **all three emit
  BYTE-IDENTICAL `.mlw`**. The `: str` gate was not protecting the corpus from anything.
- **`pure_ast.py` reaches `L3-tc ✓`** — which **#20's `seq string` variant never did**.
- Mirror sweep **52/52 TC_OK, TC_FAIL=0**; 3 files changed (`pure_ast`, and stub-signature-only
  changes in `Module3_Weaver` / `Module5_IREmitter`, e.g.
  `val _contractparser__at_op (self: _contractparser)` gains `(vals: seq int)`).
- **Markers 491 · grep 516 · offset 25 · unattached 0 — UNCHANGED. Ledger 3.**

### The two surfaces #20 did NOT name (they are why it typechecks now)

1. **Call-site element coercion.** Packing had to run each actual through `_coerce_to_int`, or a
   string-literal actual lands in a `seq int` (`Seq.cons " in " (Seq.empty: seq int)`). The
   `seq int` model carries the SAME `str_hash_op` ints the drop-behaviour used for the collapsed
   single argument — so `write(" in ")` becomes `self_write_1 (Seq.cons 260070937 (Seq.empty: seq int))`.
2. **Abstract self-call stub inference** (`expressions.py`, the `param_types[i]` inference block
   around line 5660). A vararg passed on to another self-method (`self._source.extend(text)`)
   default-typed the stub's parameter `int`. It now types it `seq <elem>`.

### THE NAMED RESIDUE — and this one WAS tried, and refused

**STARRED-ARGUMENT FORWARDING (`g(*args)`).** A starred argument lowers to its bare inner value
(`expressions._expr_to_whyml`, `"Starred"` at ~14613), so the callee receives the whole sequence
where it declares a scalar. Modelling it needs Python's positional re-binding of an
**unknown-length** sequence against the callee's arity. Until that capability exists, a
star-forwarding function **keeps the historical drop behaviour** — gated in Module5 by an
`ast.walk` for `Starred(Name(vararg))`. In `pure_ast.py` that covers `_new`, `Ellipsis.__new__`
and `Constant.__init__`; **`_Unparser.write` and `set_precedence` are NOT affected**, so the
51-marker lever is unblocked.

## THE #1 ITEM FOR THE NEXT WINDOW — cash the lever

Ladder 1a is the *capability*. **The marker payoff has not been taken yet.**

1. **Prove `pure_ast.py` whole-file** with the new lowering
   (`--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`, budget ~45 min). Nothing above ran a prover.
2. **Then un-trust the `_Unparser.write` family** (~51 of the 491 markers; `pure_ast.py` holds 96).
   `write` is now a REAL parameterized method: `let _unparser__write (self: _unparser) (text: seq int) : unit`,
   and `len(text)` / `text` reads / membership all lower faithfully.
3. **Open question worth one probe, not a scope**: #20 measured that a `seq string` vararg turns
   **40 of the 56** `write` call sites into REAL Why3 string literals — a fidelity gain `seq int`
   does not give. `seq int` is *uniform and annotation-free*; `seq string` is *more faithful but
   splits the model* (16 int-sourced sites are unbridgeable). The infrastructure now supports BOTH
   element types via `vararg_elem_type`, so this is a per-function choice, not a global one. That
   is a new degree of freedom nobody has used yet.

## Then, in this order (carried forward, still valid)

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

## The method note THIS session paid for (#21)

**THE LESSON GENERALIZES ONE STEP FURTHER: a recorded PRICE is a claim too.** #20 corrected a
recorded *reason* and then, in the same file, wrote a *price* ("corpus-affecting, M1 discipline,
budget a real increment") for the follow-on build. That price was measured, in five minutes, by
one 20-line `ast` scan over the corpus — and it was **zero**. The gate's own comments
(`Module5_IREmitter.py:5095-5096`, `functions.py:41-42`) asserted the corpus needed protecting;
**nobody had ever counted the files it was protecting.** Before budgeting any gate-lifting build,
COUNT THE FILES THE GATE ACTUALLY GUARDS. It is an `ast.walk`, not an increment.

Second, smaller note: **`check-self-annotate-sync.sh` is a live plane for EMITTER edits, not only
mirror edits.** Touching an un-trusted emitter body (`_build_method_param_types_map`) silently
pushed DIVERGED 2 -> 3. Run it after ANY `src/pycsl/` change and port the same lines to the mirror.

## The method note #20 paid for

**A REOPENING CAPABILITY IS A CLAIM, AND IT DESERVES THE SAME SUSPICION AS THE BOUNDARY IT
PRICES.** This campaign has now learned seven times that a recorded boundary's *reason* is
usually wrong. It had not yet checked the other half of the record. The `_Unparser` capability
had been named 16 hours earlier, by this same campaign, in good faith — and it was already
built. **The first move against any named capability is to try it, not to scope it.** It cost
one 1.8-second emission to find out.
