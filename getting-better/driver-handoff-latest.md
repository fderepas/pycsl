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

## PROOF VERDICT — **GREEN. 2857 / 2857 Valid, 0 non-Valid.**

**Ladder item 1a STANDS.** The unannotated-vararg -> `seq int` pyval lowering is not merely
type-checking; the whole of `pure_ast.py` proves under it.

| | |
|---|---|
| proof obligations | **2857** |
| `Valid` | **2857** |
| `Unknown` / `Timeout` / `Failure` / `Invalid` | **0** |
| provers | Alt-Ergo 2.6.3, Z3 4.13.3 (`--timelimit 5`, `-a split_vc`) |
| wall clock to full flush | ~13 min (the proof engine phase) |

Evidence: `scratchpad/r22/pure_ast_proof.log` (2857 `Prover result is: Valid` lines, zero
non-Valid; tally it with a python heredoc, NOT `grep` — instrument fact 14).

**This retires lesson (hh)'s open exposure on 1a.** #21 landed 1a on `L3-tc` alone and the campaign's
own rule is that a type-check is not a conversion criterion. It has now been paid: the criterion was
applied, and 1a passed it. Nothing built on top of 1a is resting on an unproved emitter change.

**Caveat, stated precisely so nobody over-reads the green.** The run had, at window end, moved past
the proof engine into pycsl.py's **per-goal non-vacuity phase** (one `why3 prove -g` per goal against
`scratchpad/.pycsl_vac_*.mlw`; it was ~200 goals in and still going). That phase is a SEPARATE gate
from the proof and it had NOT finished. **The proof plane is green; the vacuity plane is UNFINISHED,
not failed.** First action next window: re-run and let it finish, or run
`bin/check-emitted-vacuity.py --emit` (remember: a false green without `--emit`, instrument fact 3).

**One more fact worth having: the emitted `pure_ast.mlw` declares ZERO `axiom`s.** So those 2857
goals are discharged without the module contributing anything to the ledger. The campaign ledger
stays at 3 and this file adds nothing to it.

**The other two L-planes are INHERITED, not re-run.** The tracked tree has not changed since #21
gated them at `44150508` (this window's commits touch `getting-better/` only), so #21's fidelity
(2-DIVERGED baseline) and byte-inertness (3/3) results carry over unchanged. #22 re-verified the
metric itself fresh: **markers 491 · grep 516 · offset 25 · unattached 0 · ledger 3.**


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

## STEP 3 IS FULLY SCOPED BY #22 — it is 503 lines of PORTING, and 48/51 are unblocked

`src/pycsl/frontend/pure_ast.py` is the live counterpart of the mirror (note the path: it is under
`frontend/`, NOT `src/pycsl/pure_ast.py`). Measured by AST diff against it:

- **All 51** trusted `_Unparser` stubs have a live body available. **Zero missing.**
- **Total live body lines to port: 503.** Size distribution: **23 bodies are <=5 lines**,
  19 are 6-15, only 9 are 16+. Largest five: `visit_arguments` 50, `_str_literal_helper` 38,
  `visit_JoinedStr` 32, `visit_ClassDef` 23, `visit_MatchClass` 22. Smallest are 2-3 lines
  (`require_parens`, `visit_ParamSpec`, `visit_TypeVarTuple`, `fill`, `set_precedence`,
  `visit_Delete`, `visit_Global`, `visit_Import`).
- **Start with the 23 <=5-line bodies.** They are a natural first batch and, at ~0.45 markers per
  line ported, the cheapest markers left anywhere in the campaign.

### THE STARRED BLOCKER IS REAL FOR THIS FAMILY — but it is NOT the shape the record names

The record (and `Module5_IREmitter.py:4986-4999`) says star-forwarding "affects `_new` /
`Ellipsis.__new__` / `Constant.__init__` only" and that "`_Unparser.write` and `set_precedence` are
NOT affected". **The first half is right about the GATE; the second half is wrong about the FAMILY.**

Read the gate: it walks the *defining* function and drops the vararg only when that function's OWN
vararg NAME is star-forwarded (`isinstance(_n.value, ast.Name) and _n.value.id == _va0.arg`).
`set_precedence`'s own 3-line body forwards nothing, so it correctly keeps its `seq int` formal —
confirmed in the `.mlw`. **But three of the 51 live bodies to be ported are CALLERS that pass a
starred actual INTO that vararg formal:**

```
visit_comprehension : self.set_precedence(_Precedence.TEST.next(), node.iter, *node.ifs)
visit_Compare       : self.set_precedence(_Precedence.CMP.next(),  node.left, *node.comparators)
visit_MatchOr       : self.set_precedence(_Precedence.BOR.next(),  *node.patterns)
```

This is a **different capability** from the recorded one: not `g(*args)` forwarding of an enclosing
vararg, but **MIXED positional-plus-starred packing at a call site into a `seq int` formal**
(`f(a, *b)` — concat a materialized prefix onto an existing sequence). Nothing in the tree gates it
today, so its behaviour on port is UNKNOWN and must be probed, not assumed. Two of the three even
have a non-starred positional *before* the star, which is the hard sub-case.

**#22 RAN THAT PROBE.** Isolated it in a 15-line standalone file (`scratchpad/r22/star_probe.py`,
a `sink(self, p, *nodes)` plus a star-only caller and a mixed caller) rather than editing the mirror
— zero risk, ~2 s. **The result is unambiguous, and it is the same for BOTH shapes:**

```
let p__caller_star_only (self: p) (xs: array int) : unit =
  let _ = (self_sink_2 1 (Seq.cons xs (Seq.empty: seq int))) in ()
let p__caller_mixed (self: p) (a: int) (xs: array int) : unit =
  let _ = (self_sink_2 1 (Seq.cons a (Seq.cons xs (Seq.empty: seq int)))) in ()
```

A `Starred` actual in a vararg position is packed **as a single ELEMENT** — `Seq.cons xs …` — so the
whole sequence lands where one element belongs. It does not splat. `L3-tc ✗`:

> `This expression has type seq.Seq.seq int, but is expected to have type seq.Seq.seq (array.Array.array int @rho)`

**Two things follow, and the second is the important one:**

1. The 3 bodies are genuinely blocked. Star-only (`visit_MatchOr`) is blocked exactly as hard as
   mixed (`visit_Compare`, `visit_comprehension`) — the prefix is not the hard part; the splat is.
2. **The failure is LOUD, not silent.** It is a Why3 TYPE error at L3-tc, not a mis-typed-but-
   accepted lowering. So this residue can never quietly produce a wrong proof — porting one of the
   3 by accident fails the gate immediately. That makes "port the 48 now" safe to do without first
   solving the 3.

**PRECISE REOPENING CAPABILITY (supersedes the vaguer `g(*args)` wording):** at a call site, a
`Starred` actual in a vararg position must lower to a sequence **CONCATENATION** of its inner value
(coerced to `seq elem`) onto the materialized prefix — `Seq.(++) (Seq.cons a Seq.empty) (to_seq xs)`
— instead of today's `Seq.cons xs`. That is a call-site packing change in the same materialization
code #21 added, not the "positional re-binding against the callee's arity" the record describes;
re-binding is only needed when a starred actual feeds NON-vararg formals, which is the
`_new`/`__new__`/`Constant.__init__` case, not this one. **These are two different capabilities and
the record conflates them.**

**Consequence for the plan: port the 48 unblocked bodies now — do not let the 3 hold up 94% of the
lever.** The 3 are a bounded, well-typed follow-on.

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
