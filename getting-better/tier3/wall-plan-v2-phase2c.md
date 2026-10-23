# Wall-plan-v2 Phase 2′c — synthesis subsystem census + scoped plan (2026-07-07)

**Verified honest NO-GO for this session: 0 landed, count 1248, tree clean, ledger==3, theory still inert.**
Brick 2 (the loop→recursion + helper-synthesis pass) is confirmed a **~4–6-day new-subsystem build**, not
completable-and-certifiable in one agent run. The precise plan below is the deliverable.

## Brick 1 — E5-for-methods: mechanism works, but converts NOTHING standalone
Census (AST script + Explore sweep) of `\trusted` methods that mutate a `Set`/`Dict` **parameter** by ref:
- `find_named_expr_targets`, `_collect_assign_targets` — pair mutation with a generic `.items()`/`.values()`
  walk ⇒ **need Brick 2**.
- `_scan_2d_in_expr/_stmt`, `_handle_assign_stmt`, `_handle_tuple_unpack_stmt` — large emission methods
  `\trusted` for **many other unsupported constructs**; lifting the param-mutation rejection alone won't
  prove them.
- `_handle_seq_assign`, `_emit_new_ghost_ref` — **already un-trusted** (no count to reclaim).
Verified: lifting the WL-05b method exclusion makes the `ref`+`writes {p}` frame thread correctly for a
method param — but since **no `\trusted` method converts on E5-for-methods alone**, it is **foundation for
Brick 2 only** and was (correctly) not landed standalone (converts nothing + call-contract-map drift risk).

## Brick 2 — the make-or-break: `find_named_expr_targets` does NOT prove (4 verified defects)
Ported verbatim + rejection lifted, the emitted WhyML is nowhere near the proven S1 shape:
1. **Universal value int-collapsed** — `obj: int`, `needs_pydict` never set (L1 theory inert).
2. **`.items()` collapse** (`Module5_IREmitter.py:1477`) — `while` over an opaque int-iterator; the tuple
   target `k,v` **leak into the signature as phantom `(k:int)(v:int)` params**.
3. **Self-recursion as an opaque abstract `val`** (wrong arity/type) — a single `while` function, **not** a
   `let rec` recursion → the hard typecheck error.
4. **No `variant`** — even post-typecheck, `v = iter_get obj i` is opaque ⇒ no `size`-decrease (the
   phase2b root cause).

## The scoped subsystem (reuses landed L1 theory + scc.py's `let rec … with …` printer)
1. **Pattern recognizer** (~0.5d): match `if isinstance(obj,dict): [add]; for k,v in obj.items()[:filter]:
   self(v,acc) elif isinstance(obj,list): for item: self(item,acc)`. Fires on **0** corpus programs
   (verified) ⇒ byte-diff-0 for the gated path.
2. **Type override + `needs_pydict`** (~0.5d): retype walked param → `pyval`, accumulator → the by-ref set;
   flip `needs_pydict` so the certified theory emits.
3. **Multi-helper synthesis — THE CORE** (~2–3d): synthesize `walk` (isinstance→`match v`), `walk_dict`
   (loop→cons-spine: `match d with DNil->() | DCons _ v rest -> walk v acc; walk_dict rest acc`),
   `walk_list`, as a `let rec … with …` group from ONE method, threading `size`/`size_dict`/`size_list`
   variants + the `writes{acc}` frame. This is the new code generator.
4. **`.items()` k/v via the spine** (in #3): the `DCons` cell supplies `(key,val)`; a *general* Module5:1477
   fix would break byte-diff, so the binding lives inside the synthesis.
5. **Monomorphic key reads (E2)** (~1d): `obj.get("type")=="NamedExpr"` / `obj["target"]` →
   `K_type`/`K_target` constructor-spine matches (string-theory-free); `if k=="stmt": continue` → skip the
   `K_stmt` cell; the `type=="NamedExpr"` guard → a value-tag test gating the add.

**Estimate:** minimal toy (unconditional walk, no guards) proving the synthesis core ≈ **2–3d**; verbatim
`find_named_expr_targets` (real add-guard + skip) ≈ **4–6d**. A genuine multi-session build, distinct in
kind from routing.

## Status of the three-layer decomposition
- **L1 value modeling** — SOLVED, certified (banked, ledger==3).
- **L2 target-shape provability** — SOLVED (Phase 2′a, both provers).
- **L3 emitter code-generation** — precisely scoped above; a ~4–6d loop→recursion + helper-synthesis
  subsystem, byte-diff-0-feasible (0 corpus programs hit the recognizer). Not yet built.
