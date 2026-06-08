# return-arr.md — array-returning functions with early returns (the `Return_seq` payload)

**Date:** 2026-06-08
**Status:** P1 IMPLEMENTED (the `Return_seq` mechanism — driver 0651 proves, corpus 608/608, sound).
P2/P3 (os listdir/walk payoff) BLOCKED on a newly-found sub-gap: `_detect_seq_promotion`
(`Module5_IREmitter.py`) only treats `+=`/`a+b` as list growth, NOT `.append()`. So listdir's
append-built `names_out` stays an array-local, and its seq conversion snapshots the 1024-element
backing rather than the logical length — listdir can't prove `\length(\result) <= 16`, which `walk`
needs (modular). Applying P2/P3 net-REGRESSED os 39→41 (walk's 6 cleared, but listdir+scandir added 8
unprovable postcondition goals), so the os application was reverted. **Remaining work:** promote
`.append()`-built lists to seq (a broad model change — measure corpus/os impact) OR a `_len`-aware
array→seq conversion in the `Return_seq` raise path. Then re-apply P2/P3 (expected os 39→≤33).
**Owner:** PyCSL tool ([TOOL], `src/pycsl/**`)
**Motivation source:** os-coverage follow-on ([[os-coverage-progress]]) — `walk`'s 3 loop-variant
timeouts are blocked on `listdir` returning a length-bounded array, which it can't because it has
guarded early returns.

---

## 1. The problem

A function that **returns a list/array** (`-> list`, WhyML `array int`) **and has an early or
in-loop `return`** is not soundly supported today. PyCSL lowers early/in-loop returns by raising an
internal `Return` exception caught by a `try … with Return r -> r end` wrapper around the body
(`statements.py:_wrap_body_with_return_catch`). But:

- the `Return` exception is **monomorphic `int`** (`preamble.py:417` — `exception Return int`);
- so on the raise path, an array result is **collapsed to `0`** — lossy and wrong
  (`stmt_control_flow.py:_handle_return_stmt`, lines ~558–585, `val = "0"`);
- and `_wrap_body_with_return_catch` therefore **leaves `array int` bodies unwrapped**
  (`statements.py:880` — `if return_type == "array int": return body_code`), so an early
  `raise (Return …)` is an **uncaught exception** → Why3 error `this expression raises unlisted
  exception Return`.

The current escape hatch is **`\trusted`** (the "Class M auto-trust path",
`docs/self-annotate-layer2-queue.md`): mark the function trusted so Module6 emits a spec-only `val`
and never verifies the body. That defeats verification — exactly what we want to avoid.

**Concrete blocker:** `os.listdir` has three guarded `return []` + a final `return names_out`. To
fix `walk`'s variant it must carry `ensures \length(\result) <= 16`, which requires `array int`
typing — but its early returns hit this gap. `walk` (3 timeouts) and any Python function using the
ubiquitous **guard-clause + list-return** idiom are blocked.

## 2. Why the obvious fix (`Return_arr (array int)`) does NOT work

Mirroring the tuple `Return_{arity}` / `Return_void` pattern with `exception Return_arr (array int)`
**fails**: Why3 **forbids mutable types (`array int`) in exception payloads**. Confirmed empirically —
wrapping `array int` and raising `Return arr` yields:

```
This expression has type array.Array.array int @rho, but is expected to have type int
```

and the `ref (array int)` slot + signal workaround trips Why3's region/linearity tracking
(`Array.make` in the body "prohibits further usage of _ret_array_slot"). The existing code comments
(`stmt_control_flow.py:558`) already record this dead end. **The payload must be an immutable type.**

## 3. The design — carry returns as an immutable `seq int`, materialise at the catch

PyCSL already has an immutable list model — **`seq int`** (`seq.Seq`) — and a faithful
**seq↔array bridge** built for 07-1705-rev4 P4: `_seq_locals`, `_materialize_bridge()`, and the
`materialize : seq int -> array int` function. Returning a seq-local where the function's declared
return is `array int` already lowers to `(materialize !x)` (`stmt_control_flow.py:531`).

`seq int` is **immutable**, so Why3 **allows it in an exception payload**. The fix:

For an array-returning function that has early/in-loop returns, lower returns through a dedicated
**`exception Return_seq (seq int)`** and **materialise to `array int` at the catch**:

```whyml
  exception Return_seq (Seq.seq int)

  let listdir (filepath: int) : array int
    ensures { Seq.length result <= 16 }   (* \length(\result) <= 16 *)
  =
    try
      ...
      if bad then raise (Return_seq Seq.empty) ;          (* return []   *)
      ...
      (* build seq, then: *)
      raise (Return_seq !names_seq)                        (* return names_out *)
    with Return_seq s -> materialize s end
```

Each `return <list-expr>` in such a function becomes `raise (Return_seq <seq-of-expr>)` (a list
literal → `Seq.cons` chain, already implemented by `_seq_init_expr`; an array-local → `snapshot`).
The single catch materialises once at the boundary — the materialised array is bound at the function's
result slot and never rebound into a region, so it sidesteps the linearity problem the `array int`
payload hit.

### Three touch points (all mirror existing seq / Return_void machinery)
- **`preamble.py` (~211–230, 415–427):** add a `needs_return_seq` branch — when a function with
  early/in-loop returns has `find_return_type == "array int"`, set the flag (instead of falling into
  `needs_return_exc`); declare `exception Return_seq (Seq.seq int)`. Pulls in `seq.Seq` (already
  gated by `needs_seq`).
- **`stmt_control_flow.py:_handle_return_stmt` (~547–585):** on the `use_raise` path, when
  `_func_return_type == "array int"`, emit `raise (Return_seq <seq>)` — converting the return value
  to a seq via the existing `_seq_init_expr` / `_seq_operand` (list literal → `Seq.cons`; array-local
  → `snapshot`). Replaces today's lossy `val = "0"; raise (Return …)`.
- **`statements.py:_wrap_body_with_return_catch` (~880):** for `return_type == "array int"` **when the
  function has early returns**, wrap as `try\n{body}\n with Return_seq s -> materialize s end`
  (instead of returning the body unwrapped). Functions with NO early returns stay unwrapped
  (byte-identical).

## 4. Soundness

`seq int` is a faithful immutable snapshot of the list's contents; `materialize` is the verified
bridge already used at seq→array return boundaries (P4). The body is still a verified `let` (no
`\trusted`), so the postcondition (`\length(\result) <= N`, element facts) is proven against the real
control flow — strictly better than today's collapse-to-`0` or trust-the-whole-body. The catch
materialises exactly once at the result slot.

## 5. Phasing

| Phase | Delivers | Gate |
|---|---|---|
| **P1** | `Return_seq` declared + raised + caught for array-returning funcs **with early returns** | minimal driver: `def f(x)->list: if x<0: return []; return [1,2,3]` with `ensures \length(\result)>=0` **proves** |
| **P2** | apply to `os.listdir`: `-> list` + `ensures \length(\result) <= 16` | listdir proves standalone; `scandir` too (same shape) |
| **P3** | `walk` variant `len(names) - i` (now `len` = `Seq.length`/`Array.length` of a bounded array) | `walk`'s 3 variant goals discharge; **os 39 → ≤ 36** |

## 6. Acceptance criteria
1. The P1 driver proves (early `return []` + tail `return [..]`, array return), body verified (NOT `val`).
2. A **false** length `ensures` makes the function FAIL (body still checked — the anti-`\trusted` gate).
3. listdir proves `\length(\result) <= 16`; walk's variant discharges; **os ≤ 36**; os formal 18/18.
4. **Byte-identical** corpus for every array-returning function **without** early returns (the wrap is
   only added when early returns exist) — full `bin/run-reference-tests.sh --pycsl` unchanged.
5. New corpus driver (the P1 shape) added to `test-suite/corpus/pycsl-reference/` + traceability.

## 7. Risks
- **Region/linearity at the materialise boundary.** The whole reason `array int` payloads fail. Must
  verify the `with Return_seq s -> materialize s` result binds cleanly at the result slot without
  re-regioning. P1's minimal driver is the canary — if it can't be made to prove, the fallback is the
  per-function single-return refactor (§8), not this feature.
- **Mixed return shapes.** A function returning `[]` (empty), an array-local, and a `Seq.cons` literal
  on different paths — all must lower to `seq int` uniformly. `_seq_init_expr` already handles literal
  + bridge; verify the empty-list and array-local-snapshot paths.
- **Existing collapse-to-0 functions.** Some array-returning functions with early returns may today
  "pass" only because the lossy `0` collapse made their (weak) contract trivially hold. Switching to
  the faithful seq payload could expose real unproven goals in those — that's *correct* (they were
  never truly verified), but measure the corpus/os delta and fix or annotate as found.
- **Element type.** `seq int` abstracts non-int elements (listdir's names are strings). Fine for the
  length-driven variant goal; element-precise facts are a separate (string-modelling) concern.

## 8. Out of scope / alternatives
- **Per-function single-return refactor** (rewrite guard-clauses as nested if/else over a result var):
  a source-level workaround, no tool change — but invasive and error-prone for functions with
  dependent guarded reads (listdir reads `inode = _read_inode(ino)` only after the `ino` guard).
  Keep as the fallback if §7's region risk proves fatal.
- **`\trusted` (Class M):** the status-quo escape hatch — explicitly what this feature replaces.
- `Return_seq` for **tuple-of-array** or **nested-list** returns — generalise later if a driver needs it.

> **In one line:** array-returning functions with early returns can't use the monomorphic `int`
> `Return` exception, and Why3 forbids a mutable `array int` exception payload — so carry such returns
> through an **immutable `exception Return_seq (seq int)`** and **`materialize` to `array int` at the
> single catch** (reusing the P4 seq↔array bridge), which lets `os.listdir` prove `\length(\result)
> <= 16` and unblocks `walk`'s 3 variant timeouts (os 39 → ≤ 36) — gated by a byte-identical corpus
> for early-return-free array functions and a false-`ensures`-fails-the-body soundness check.
