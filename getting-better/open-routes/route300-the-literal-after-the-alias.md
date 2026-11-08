# OPEN ROUTE #300 — A LITERAL REBINDING AFTER A NON-LITERAL FIRST BINDING REGISTERS A FIXED FOLD SIZE (#297 residual)
**Status: REPAIRED (gen #37, 2026-10-22; opened the same day), Severity 1.** Red-team round 10; driver-reproduced at 2cef1801 (2 probes rc=0; CPython violates).
Witnesses `witnesses-r300/`: `d = e; if c == 1: d = {"a": 1}; return len(d)` proves `\result == 1` (CPython g(0, {}) = 0, j04); loop
variant k04. The fold registration in src/pycsl/module6_whyml/types.py (~88-100) blacklists a rebound name only when its FIRST
binding was a literal; a later literal binding registers size/elements that are then used on every path. Route #297's residual (1).
Repair: register a fold only for a name bound EXACTLY ONCE (single static binding, not in a loop/branch, never re-bound / aliased
/ mutated), otherwise blacklist; census all binding forms (params, aliases, loops, branches, augmented assignment, del, walrus,
for-targets, with-as, except-as) and every fold consumer (len, subscript, truthiness, sum, in).

## REPAIR (2026-10-22, r299/r300 executor off f11bba0e; commits 56175045 + 8ee6ee54 + route docs)
Probe table (`src/pycsl/pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | f11bba0e | after |
|---|---|---|
| route witnesses j04, k04 | rc=0 PROVED | rc=1 (L3-tc: unfolded dict `len` fails closed) |
| 3576 `d = e; if c == 1: d = {"a": 1}; len(d) == 1` (j04) | PROVED | FAIL |
| 3577 loop twin `for i in range(c): d = {"a": 1}` (k04) | PROVED | FAIL |
| 3578 list PARAMETER rebound in one arm, `len(d) == 2` | PROVED | FAIL |
| 3579 `s = e; if c == 1: s = "ab"; len(s) == 2` (string) | PROVED | FAIL |
| 3580 list PARAMETER rebound in one arm, `d[0] == 5` (element fold) | PROVED | FAIL |
| 3582 dict PARAMETER rebound in one arm, `len(d) == 1` | PROVED | FAIL |
| 3583 str PARAMETER rebound in one arm, `len(s) == 2` | PROVED | FAIL |
| 3584 string loop twin `for i in range(c): s = "ab"` | PROVED | FAIL |
| 3581 CONTROLS: single literal binding keeps its fold (dict len, tuple index, list len, str len) | PASS | PASS |
| scratch: for-target / walrus / TupleUnpack first binding + literal arm (list) | FAIL (pre-existing: L3-tc `d_len` / unbound `d`, or route #264 refusal) | FAIL |

Rule (inline in `_reset_function_state`, a `\trusted` mirror stub; no new def/field, no axiom — ledger 3): the
pre-pass counts every STATIC binding of each name — a formal parameter (`formal_params`), `with ... as`
(`with_bindings`), any string `target` in the body (Assign, AugAssign, GhostAssign, For, NamedExpr, comprehension
generator), any `targets` / `tuple_targets` list (TupleUnpack, tuple-For), an `except ... as` handler `name`, a
`match` `Capture` name. A name bound more than once goes into `_fold_unsafe_sizes` AND `_fold_unsafe_elems` (so
`_track_collection_metadata` registers nothing for it, whatever its first binding was), and, if any of its
bindings is a collection/string literal, into `_rebound_collections` (what that set always meant; its consumers
— the all/any oracle decline, the route #159 `length 0` — only get more conservative). A `del x` and an
`import ... as` lower to nothing in the IR (no read survives them); a comprehension variable is its own scope in
Python 3, so counting it over-refuses (completeness only).
CENSUS of fold consumers (all read `_known_collection_sizes` / `_known_collection_elements`, whose ONLY producer
is `_track_collection_metadata`, now gated by the pre-pass; route #60's store increment only grows a registered
entry): `len` (Var arm), truthiness (`_r31_sizes`), `sum`, the indexed read, the all/any oracle decline, the route
#159 bounds `length 0`, the statement-side store bounds. `in` / `for` never consulted the fold.
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED, pyref 0/0/0, mirror 0/0/0 (same sweeps as route #299).
No mover: no M1 re-proof and no mirror proof OWED.
Gates: as route #299 (one combined increment).
Residuals: (1) a NESTED `def` assigning the name through `nonlocal` is not counted (the inner body is not walked as
a binding of the outer local) — unmeasured. (2) A single literal binding inside a branch/loop keeps its fold; the
only other path reaches the read with the name unbound, which route #264 refuses (UnboundLocalError) — measured on
the for-target probe. (3) Witness probes q*/r*/s* live in the executor scratchpad only.
