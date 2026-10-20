# OPEN ROUTE #287 — sorted(..., key=lambda ...) KEY BODY RAISES ARE DROPPED
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r287/`. w008 `sorted(xs, key=lambda v: 10 // v)` and w014 key `d[v]` prove under `no_exception \all` (CPython ZeroDivisionError/KeyError); w015 `try: return sorted(xs, key=lambda v: 10//v) except ZeroDivisionError: return []` proves `len(result) == len(xs)` (CPython []). Route #275 admits a key lambda "whose body invokes nothing" and lowers to `sorted_perm_1 xs`, dropping the body; #285 census does not look into lambdas. Repair: the key body is evaluated per element: refuse unless its body is raise-free by the trigger table (or model the raise), incl. under try/except. Census every builtin that takes a callable (min/max/sorted key, map/filter, functools).

## REPAIR (2026-10-20, executor rA off 7313506b; commit 79a2d92f)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 7313506b | after |
|---|---|---|
| `sorted(xs, key=lambda v: 10 // v)` under `no_exception \all` (w008 / 3340) | PROVED | REFUSED |
| key `d[v]` (w014 / 3341), key `xs[v]` (c006 / 3342) under `no_exception \all` | PROVED | REFUSED |
| `try: sorted(xs, key=lambda v: 10 // v) except ZeroDivisionError: return []`, `len(\result) == len(xs)` (w015 / 3343) | PROVED | REFUSED |
| same with key `d[v]` / `xs[v]` and `except KeyError` / `IndexError` (3344, probe u4) | PROVED | REFUSED |
| controls: key `v + 1` / `-v` under `no_exception \all`, `key=None, reverse=False` ascending (3345) | PASS | PASS |
| census: `min/max(xs, key=...)` | REFUSED (#275/#160) | REFUSED |
| census: `list(map(lambda v: 10 // v, xs))`, `list(filter(...))`, `map(k, xs)` with a named `k` | ill-typed (rc 1) | ill-typed |
| census: `functools.reduce(lambda ...)` under `no_exception` | REFUSED (#161) | REFUSED |
| census: `any(10 // v > 1 for v in xs)`, `[10 // v for v in xs]` in a try region | REFUSED (#177/#285) | REFUSED |
| census: `sorted(xs, key=k)` with a named `k` | REFUSED (#275) | REFUSED |
| census: `l = lambda v: 10 // v; l(0)` under `no_exception` | REFUSED (#161) | REFUSED |

Rule (inline in `_reset_function_state`'s #177/#285 walker, mirror `\trusted`; no new def/field; ledger 3):
a `Lambda` node is censused exactly like a comprehension element — its `body` is matched against
`exception_model.TRIGGER_EXPR_SHAPES` for every row whose exception is ACTIVE (declared `no_exception`, or
widened by a handler, route #171), and an uncensused TRIGGERS row still refuses (#285 fail-closed). A hit
raises "a lambda's body contains ... (route #287)". The comprehension message is unchanged (census rows
keyed on message text). Without an active context a key-body raise is ambient, as everywhere else.
Census of callable-taking builtins: the only one whose lowering DROPS a callable while modelling the
result is `sorted(key=lambda ...)` (#275 admitted it); every other one is refused or ill-typed today
(table). A lambda body with a call was already refused by #275's sorted arm.
Blast radius: corpus root 0 MOVED for this route (the five new refusals are new sources), pyref 0, mirror 0.
Gates (logs under the rA scratchpad; all heavy jobs via heavy.sh): witnesses at 7313506b vs after in
the table; byte-diff-sweep base/after rc=0 (2510 / 2529 sources); byte-diff-compare root rc=0 with ONE
declared mover (1915, below), pyref rc=0 (2186/2186, 0 MOVED / 0 GONE / 0 APPEARED); mirror-emit-sweep
base/after rc=0, compare `--min-files 45`: 1 MOVED (`frontend__pure_ast`, route #291, below), 0 GONE,
0 APPEARED; check-self-annotate-sync.sh rc=0 (923 verbatim); self-annotate-mirror-check.sh rc=0 (53);
refusal-witness census +15 rows (3340-3344 REFUSAL, 3346-3350/3352-3354/3356-3357 VERIFY-FAIL) via
`--append-new` (that run also found 234 pre-existing FAIL witnesses with no row at 7313506b — not
appended here, out of scope; reported to the driver); run-soundness-planes.sh --slow rc=1 -> 82/84 green; vacuous-drivers (3358) and hashed-literal-purity
(re-keyed baseline rows for the format-keyed struct symbols) fixed and re-run rc=0; assigns-writes-survival
TRAP 1447 > 1445 is identical at 7313506b (pre-existing).
Residuals: none known for the trigger table's exceptions; a key lambda whose body raises an UNTRACKED
exception (`AttributeError`, `TypeError`) is outside `no_exception`'s documented set (KNOWN_EXCEPTIONS).
