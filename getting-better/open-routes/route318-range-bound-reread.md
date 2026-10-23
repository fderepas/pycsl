# OPEN ROUTE #318 — THE BOUND OF `range(<expr>)` IS RE-EVALUATED AT EVERY ITERATION (Python evaluates it once)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day; faithful capture), Severity 1.** Red-team round 17; driver-reproduced on main f44477b7 (rc=0; CPython violates).
Witnesses `witnesses-r318/`: `n = 2; for i in range(n): n = 5; c += 1` proves `\result == 5` (CPython 2) (l41); `range(len(s))` with s
rebound in the body (l43); `range(n + 1)` (l45); shrinking bound in a nested loop (l54). Emitted loop test `while !_idx_i < <bound>`
where <bound> is `!n` / `(!n + 1)` / `(str_length_op !s)`; constant and field bounds are captured once (`let _len_idx_i = o.n`) and
correct; `range(lo, hi)` start is correct. Needs user invariants + loop variant (no automatic variant for a live bound).
Repair: capture every range argument (start, stop, step) ONCE into a fresh immutable binding before the loop, in Python order (#307), for
every bound shape; census every for-range lowering path (incl. seq-promoted lists, enumerate/zip ranges, l53 near-miss).

## REPAIR (2026-10-23, r318 executor off 8610363c; commit 654ef3a4 + docs commit)
**Census of for-loop lowering paths** (single handler `_handle_for_stmt`; comprehensions are one expression, never re-read):
`range(stop)` / `range(start, stop)` -> counter `ref start` (read once) + guard `!idx < stop` — **the hole**; a stop with no
`!` and no source variant was already hoisted by #29 (`let _len_<idx> = stop`, field/subscript included), so the hole was
every `!`-bearing stop (rebound local `!n`, `(!n + 1)`, `str_length_op !s`, seq-promoted `Seq.length !xs`) and every
stop under a source `#@ loop variant` (`o.n`, `xs[0]`). `range(a, b, c)` -> opaque `iter_length (py_range_3 ..)`
re-evaluated as an UNSPECIFIED `val` (any count; sound over-approximation, unchanged). `enumerate`/`zip`/`reversed` over a
range -> opaque `iter_length` (hoisted when `!`-free; otherwise unspecified each call; unchanged). Collection loops
(`Array.length`, `Seq.length`, string, hval, split/literal materialisations) bound the live collection — Python's list
iterator also re-reads `len`, so those are faithful (route #320 handles in-place literal rebinds during iteration).
**Rule** (`_handle_for_stmt`, after the #29 hoist; inline): when `is_range` and the #29 hoist did not fire and the stop is
not an int literal, a bare `!`-free identifier, or `Array.length` / `str_length_op` of one, emit
`let _stop_<idx> = <stop> in` before the counter and guard on it. No invariant/variant is added (a source variant may be
present; the counter may start below 0). Start/stop order: the start is the counter initialiser; an order-sensitive pair is
refused by #307 first.

| witness | CPython | 8610363c | after |
|---|---|---|---|
| 4110_gen37_r318_range_stop_rebound_in_body (l41) | violates | PROVED | FAIL |
| 4111_gen37_r318_range_len_of_rebound_str (l43) | violates | PROVED | FAIL |
| 4112_gen37_r318_range_stop_expression (l45) | violates | PROVED | FAIL |
| 4113_gen37_r318_range_stop_shrunk_in_body (l54) | violates | PROVED | FAIL |
| 4114_gen37_r318_range_stop_field_rebound (field stop + variant) | violates | PROVED | FAIL |
| 4115_gen37_r318_range_stop_rebound_control | ok | FAIL | PROVED |
| 4116_gen37_r318_range_len_appended_control (seq-promoted, l53 shape) | ok | FAIL | PROVED |
| red-team l53 near-miss | violates | FAIL | FAIL |

**Gates** (worktree off 8610363c): corpus byte-diff root 1 MOVED (`0708`, #318 capture of `!m`, PASS -> PASS re-proved
rc=0) and 3 GONE (`3578`/`3580`/`3582`, route #300 expected-FAIL witnesses whose list/dict parameter is rebound in an `if` arm:
FAIL -> REFUSED by #319); pyref 0 MOVED / 0 GONE (2186/2186); mirror-emit-sweep (`--min-files 50`) 1 MOVED
(`frontend/Module3_Weaver` `_desugar_for`: `let _stop_idx_m = !hi in` — `hi` is not written in the loop), L3-tc rc=0;
fidelity `check-self-annotate-sync.sh` rc=0 (926 verbatim), `self-annotate-mirror-check.sh` rc=0 (53); `doc-coherency --check`
rc=0; `check-assumed-facts` rc=0 (85 facts, unchanged); raises-honesty rc=0 (ratchet 61 silent, unchanged: both new raises sit
in `_handle_assign_stmt`, whose `\trusted` twin already declares `#@ raises PyCSLSemanticError`); `check-dropped-mutation`
rc=0 (0/51/5/0); `check-refusal-witness-coverage` (no flags) rc=0 (261 demonstrated, 5 undemonstrated = base; census rows for
4110-4114/4117-4120/4122-4125 produced by `_census_row`); fast soundness planes: see README entry. Ledger 3; no gate
loosened; no new def / field / IR change (lesson a4: inline walks).
**Residuals:** `range(a, b, step)` and `enumerate(range(..))`/`zip` keep the opaque, unspecified lowering (sound, contentless);
docs annotations §7.12, translational §T.6.23, static-semantics (no new code).
