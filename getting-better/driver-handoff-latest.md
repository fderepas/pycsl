# HANDOFF — read this FIRST on relaunch (rewritten 2026-09-01, RELAUNCH #22 worker)

## What #22 had, and what it did

A **~55-minute** window against the same deadline (`.driver-deadline` = 1788251064). The window was
too short to start a build, and the supervisor named exactly one job: **run a prover on ladder item
1a**, which #21 built and gated only to `L3-tc`. Lesson (hh) — *type-check success is not a
conversion criterion* — is the whole reason this had to happen before anything was banked on 1a.

## THE JOB: whole-file proof of `src/self-annotate/src/frontend/pure_ast.py`

Launched at T-53min, detached (`nohup`, so it survives a turn ending — instrument fact 8 is about
watchers, not about the proof process itself):

```
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad
PYTHONHASHSEED=0 python3 -u src/pycsl/pycsl.py \
  src/self-annotate/src/frontend/pure_ast.py \
  --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' \
  > scratchpad/r22/pure_ast_proof.log 2>&1 &
```

**VERDICT: see `## PROOF VERDICT` below — it is the first thing to read.**

## What #22 VERIFIED about 1a independently (all fresh, from the emitted `.mlw`)

`--no-proof --keep-mlw` on `pure_ast.py` (1.8 s, instrument fact 7) leaves
`src/self-annotate/src/frontend/pure_ast.mlw` on disk (gitignored, so it never dirties the tree).
In it, **the 1a capability is really present** — this is not a no-op emission:

- `let _unparser__write (self: _unparser) (text: seq int) : unit` at line 4847 — a **real
  parameterized `let`**, not a `val`, and not a zero-parameter facade.
- `val _unparser__set_precedence (self: _unparser) (precedence: int) (nodes: seq int) : unit`
  at line 4241 — the vararg is a formal here too.
- **58 `write` call sites**, every one materialized as `Seq.cons … (Seq.empty: seq int)`
  (266 `Seq.cons` occurrences file-wide). Element values are the same `str_hash_op` ints the
  drop-behaviour used: `self_write_1 (Seq.cons 260070937 (Seq.empty: seq int))`.
- `L1 ✓ L2 ✓ L3-tc ✓` reproduced independently of #21.

## THE RECORDED PRICE OF THE NEXT LEVER WAS WRONG (again) — and it is BIGGER, not smaller

Applying #21's own lesson (*a recorded price is a claim too*) to the price #21 itself recorded:

| record | recorded | **measured by #22** |
|---|---|---|
| markers in `pure_ast.py` | 96 | **95** |
| `_Unparser` family lever | 51 | **54 markers** (51 of them attach to `_Unparser` methods; 1 sits behind an `@_contextmanager` decorator; the rest are nested/decorated defs) |

Per-class marker census of `pure_ast.py` (95 total):
`_Unparser` **54** · `_Parser` 24 · `AST` 5 · `Comment` 3 · `NodeVisitor` 3 · `_Tok` 2 ·
`_ABC`/`Ellipsis`/`NodeTransformer`/`_Precedence` 1 each.

So `_Unparser` is **54 of 491 = 11.0%** of the whole campaign's remaining metric in ONE class in ONE
file. It is by a wide margin the largest single lever left, and the recorded figure understated it.

**Also measured, and it matters for how step 3 is planned:** all 51 trusted `_Unparser` methods are
`\trusted` *stubs with elided bodies* — an `ast.walk` over the mirror finds **zero** `self.write`
calls and **zero** starred forwarding inside them, because there is nothing inside them. The 58
`Seq.cons` call sites above are in the ALREADY-CONVERTED methods. Step 3 is therefore a *porting*
job (bring each real body into the mirror), not a *repair* job, and the `write` signature it must
target is the one now verified above.

## THE #1 ITEM FOR THE NEXT WINDOW

**Un-trust the `_Unparser.write` family — 54 of the 491 markers.** It is the campaign's largest
remaining single lever and, as of this window, the emitter capability under it is proved-or-refuted
(see the verdict) rather than merely type-checked.

Two live degrees of freedom, both opened in the last two windows and **neither one used yet**:

1. **`vararg_elem_type` makes the element type a PER-FUNCTION choice.** #20 measured that
   `seq string` turns **40 of 56** write call sites into real Why3 string literals (a fidelity gain)
   while 16 int-sourced sites are unbridgeable; #21's `seq int` is uniform and annotation-free.
   These were believed mutually exclusive. They are not, since #21's infrastructure carries the
   element type per function. Worth ONE probe, not a scope.
2. **STARRED-ARGUMENT FORWARDING (`g(*args)`) is deliberately still gated out** (Module5 `ast.walk`
   for `Starred(Name(vararg))`; a starred arg lowers to its bare inner value at
   `expressions._expr_to_whyml` `"Starred"` ~14613). It keeps the historical drop behaviour.
   Reopening capability: positional re-binding of an unknown-length sequence against the callee's
   arity. **It affects `_new` / `Ellipsis.__new__` / `Constant.__init__` ONLY — `_Unparser.write`
   and `set_precedence` are NOT affected, so the 54-marker lever is unblocked by it.**
   Per lesson (#20): the first move against this capability is to TRY it, not to scope it.

## Then, in this order (carried forward, still valid)

2. **`ControlFlowStmtMixin._handle_return_stmt`** — the ONE non-constructor model-visible false
   frame left (18 fields via-callee). `module6_whyml/stmt_control_flow` is 1846 goals, ~45 min.
3. **`scratchpad/w3/fix_assigns.py` IS THE REUSABLE TOOL.** It converges `#@ assigns` / `#@ raises`
   / `#@ \diverges` against Why3's own error text. Point its `MIR` constant at another mirror.
   **Every wall whose recorded reason is "the effect summary cannot be made exact" should be
   re-tested with it FIRST.**
4. **The `pyx_view` ADT redesign / record AST model** remains the soundness floor under the
   object-identity question. Obstacle: `pure_ast`'s node classes are SYNTHESIZED AT IMPORT by
   `type(name, (base,), body)` from `_NODE_SPEC`.
5. `val function csl_to_ir_op` is **CLOSED** (relaunch #19). Do not re-open it.

## Recorded boundaries carried forward — do not re-grind without the named capability

- `_csl_to_ir` is **BROKEN**; strike it from any ladder that still lists it.
- **The attribute-store third horn** works and is axiom-free; blocked on OBJECT-IDENTITY INJECTIVITY.
- **`crosscheck_ir.pairwise`** — spiked and working, demand NIL.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]** (33 sites / 13 methods).
  Same disease as the `_Unparser` finding, one type-family over.
- `_fin` / `_max_end` / `_fin_block` — [ERASURE-LEDGER]; `node(self, name, start_tok, **kw)` —
  [MODEL]; `_slice`; **`Module2_Parser`'s contract-expression cluster** (TERMINUS);
  `_decode_escapes` / `_decode_string`; `identifiers.whyml_ident` / `stable_hash`;
  `struct_format.parse_format` / `calcsize`; `proof2why3/normalize`'s whole file (regex).
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
   **#22 confirms this directly: `pure_ast.py` produced 0 `Prover result` lines for its entire
   first 20 minutes with exactly one live prover child throughout.**
7. A FAILING `pycsl.py` run is much FASTER than a passing one. **Emitting `pure_ast.py` alone
   with `--no-proof --keep-mlw` takes 1.8 SECONDS** — a vastly cheaper probe than a sweep.
8. BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING. **But a `nohup … &` proof process DOES**
   (#22 relied on this). `scratchpad/w3/prove.sh` / `prove_wt.sh` prove a list sequentially;
   `bin/byte-diff-sweep.sh` runs `--no-typecheck`.
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

## The method note THIS session paid for (#22)

**THE PRICE LESSON IS NOT A ONE-OFF — IT REPEATS ON THE VERY NEXT RECORD YOU READ.** #21 discovered
that a recorded price is a claim and corrected #20's. #22 then applied the same five-minute
`ast`-and-`grep` census to the price #21 itself had just written down, and it was wrong too — in the
*favourable* direction (54, not 51). Both directions matter: an overstated price stops a build that
should happen, and an understated one under-funds it. **The census that corrects a price costs
minutes; the record it corrects has stood for windows.** Run it as reflex on any figure you are
about to plan against, including one written an hour ago by the immediately preceding worker.

Corollary specific to this metric: **counting `\trusted` markers is not the same as counting
convertible methods.** In `pure_ast._Unparser` those numbers are 54 and 51 — the gap is markers on
decorated and nested defs. Quote the marker count for the metric, the method count for the plan,
and never silently substitute one for the other.

## The method notes #20 and #21 paid for (still the operating rule)

**A REOPENING CAPABILITY IS A CLAIM, AND SO IS A RECORDED PRICE.** This campaign has now found a
recorded boundary's *reason* wrong seven times, a recorded *price* wrong twice, and a named
*capability* already-built-and-working once. The standing rule: **verify every part of a record —
reason, capability, AND price — against the emitted `.mlw` and the actual tree**, before you spend
a window on it. `check-self-annotate-sync.sh` is a live plane for EMITTER edits too, not only
mirror edits; run it after ANY `src/pycsl/` change.
