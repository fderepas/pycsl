# OPEN ROUTE #275 — `sorted(..., reverse=..., key=...)` IS MODELLED AS AN ASCENDING SORT
**Status: REPAIRED (gen #36, 2026-10-18; opened the same day), Severity 1.** Red-team round 5; driver-reproduced at HEAD (o07/o09 rc=0; CPython False).
Witnesses `witnesses-r275/`. Emission `sorted_1 xs` drops the keywords, and `sorted_1` ensures ascending order.
Repair: honour `reverse` (descending) and refuse/opaque any `key` (or keyword not modelled) — never drop keywords
(route #259 noted the generic path drops keyword args for every builtin: census all builtins).

## REPAIR (2026-10-18, branch r275 off 5a307a33)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 5a307a33 | after |
|---|---|---|
| `sorted([1,2], reverse=True)`, claim `ys[0] <= ys[1]` (o07 / 2980) | PROVED | FAIL (goal unproven) |
| `sorted([1,2], key=lambda v: -v)`, same claim (o08 / 2981) | PROVED | FAIL |
| `sorted(xs, reverse=True)` any 2-list (o09 / 2982) | PROVED | FAIL |
| `sum([1,2], start=10) == 3` (2983; CPython 13) | PROVED | REFUSED |
| `sorted(xs, key=lambda v: -abs(v))`, ascending claim (2984) | PROVED | REFUSED (key body invokes `abs`) |
| `sorted(xs, reverse=True)` DESCENDING true claim (2985) | FAIL | PASS (coverage) |
| `len(sorted(xs, key=...)) == 2` (2986), `reverse=False` / `key=None` ascending (2987), `print(sep=, end=, file=sys.stderr, flush=)` under `no_exception \all` (2988) | PASS | PASS |
| `min/max(xs, key=)`, `int("10", base=16)`, `enumerate(xs, start=1)`, `round(x, ndigits=)`, `zip(strict=)`, `s.split(maxsplit=)` false claims | FAIL (opaque) | REFUSED / FAIL |

Rules (inline, no new defs, ledger 3 — no axiom; both edited methods have `\trusted` mirror twins):
- `sorted` arm (`_call_named_builtins`): `reverse=True` (bool literal) -> `val sorted_desc_1` (same length,
  adjacent `>=`, `permut`); a `key` other than `None` (or any other keyword spelling) -> `val sorted_perm_1`
  (same length + `permut` only — what holds for EVERY order); `reverse=False` / `key=None` keep `sorted_1`.
- CENSUS of the generic builtin path (`_reset_function_state`, next to route #69's prescan): a call to a bare
  builtin (not shadowed by a user definition, route #75) carrying a keyword is REFUSED unless that keyword is
  one a lowering reads — `pow` (route #259, owes `false`), `max`/`min` `default` (route #160; the 1-arg form is
  opaque), `sorted` `reverse=<bool literal>` / `key=None` / a lambda whose body makes no call, and `print`'s
  `sep`/`end` (str literal or None), `flush` (bool literal), `file=sys.stdout|sys.stderr` (output unmodelled;
  these spellings neither raise nor reach user code). Census before the rule: corpus `max(default)` (1553) and
  `pow(exp|mod)` (2705/2706) only; mirror `print(file=sys.stderr)` x5 (pycsl.py) and `sorted(key=lambda c:
  c.lineno)` (Module1_Ingestor); stdlib `open(encoding=)` in json/tool.py (package already refused).
  Contracts cannot spell a keyword argument (the contract grammar refuses `f(x=...)`), so no spec-side escape.
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1773 base / 1780 candidate, 7 new sources), pyref
0/0/0 (2186/2186). Mirror 0 MOVED / 0 GONE / 0 APPEARED (53/53; `pycsl.py` and `Module1_Ingestor`, the two mirror
files that carry builtin keywords, emit byte-identical). No mover, so no M1 re-proof was owed.
Gates (logs under the r275 scratchpad): witnesses 2980-2984 rc=0 at 5a307a33 -> rc=1 after (2980/2981 goal
unproven, 2982 goal unproven, 2983/2984 refused); 2985 rc=1 -> rc=0; 2986-2988 rc=0 both. byte-diff-sweep base/after
rc=0 (2381 / 2390 sources); byte-diff-compare root rc=0, pyref rc=0; mirror-emit-sweep base/after rc=0, compare
`--min-files 50` rc=0; refusal-witness census +2 rows (2983, 2984) via the plane's own `_census_row`
(refusal-witness-coverage OK, 5 undemonstrated = ceiling); `run-soundness-planes.sh --slow` rc=0, all 84 green
(fast 61 + slow 23); check-self-annotate-sync.sh rc=0 (920 verbatim); self-annotate-mirror-check.sh rc=0 (53).
Residuals: dotted METHOD keywords are outside this census (`xs.sort(...)` is already refused as an unmodelled
in-place mutation; `s.split(maxsplit=1)`'s false claim FAILS because the split model is opaque). `no_exception
\all` does not cover `TypeError` (KNOWN_EXCEPTIONS is the five Phase-1 exceptions), so `print("x", end=5)`
proving `no_exception \all` was within the documented scope; it is refused now anyway (non-literal `end`).
