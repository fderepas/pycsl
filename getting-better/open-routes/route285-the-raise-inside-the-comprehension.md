# OPEN ROUTE #285 — EXCEPTIONS INSIDE COMPREHENSIONS/GENEXPS: ONLY DIVISION AND SUBSCRIPT TRIGGERS ARE CHECKED
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Table-driven refusal, no assumption. Red-team round 7; driver-reproduced at 83aa79bd (p196/p211/p214 rc=0; CPython ValueError).
Witnesses `witnesses-r285/`. Under `no_exception \all`, `[str(x) for x in xs]`, f-string/repr elements, `",".join(str(x) for ...)`
(digit limit, #281), `[chr(x) ...]`/`{x: chr(x)}` (chr range), `[1 << x ...]`/`sum(1 << x ...)`/`[x >> n ...]` (negative shift) all
prove; the same operations outside a comprehension are caught (p206/p210/p213/p216). The comprehension refusal enumerates
ZeroDivisionError and IndexError/KeyError only. Repair: drive the comprehension check from the exception-trigger table itself
(every trigger row, present and future), not a hand list; census the trigger table against it.

## REPAIR (2026-10-20, r284 executor, off 323066f9)

**Rule.** The route #177 comprehension refusal in `_reset_function_state` (`module6_whyml/functions.py`,
mirror twin `\trusted`) no longer carries a hand list. New data in `exception_model` (mirrored verbatim):
`TRIGGER_EXPR_SHAPES: Dict[TRIGGERS key, List[(shape, arg)]]` — for EVERY `TRIGGERS` row, the expression shapes
that reach it: `("BinOp", op)`, `("Subscript", "")`, `("Call", name)` (bare builtin), `("Method", name)`,
`("FString", "")` (a non-literal part), `("FormattedValue", "")`; an EMPTY list = statement-only. Under an
active `no_exception`, a ListComp / SetComp / DictComp / GenExp whose element / key / value / `if` / iterable
contains a shape of a row whose exception is active is REFUSED (PYCSL refusal message names the row:
"a comprehension contains an operation that the trigger row ('call', 'chr') can make raise ValueError ...";
the division / subscript wording of route #177 is kept for those rows, so their census rows are unchanged).
**Future rows:** a `TRIGGERS` row with NO `TRIGGER_EXPR_SHAPES` entry makes EVERY comprehension refused under
its exceptions (measured by monkeypatching a fake row `("call", "zz_future")`: 3279's accepted
comprehensions are then refused naming it). No new def / field / axiom (ledger 3).

**Census of the trigger table against the comprehension path** (base = what the comprehension check caught at
323066f9):

| TRIGGERS row | exception | shapes | base | after |
|---|---|---|---|---|
| `binop div/mod/"/"/"//"/"%"`, `binop **` | ZeroDivisionError | BinOp op | refused (#177 hand list) | refused (table) |
| `binop <<`, `binop >>` | ValueError | BinOp op | **PROVED** (p214/p235/p237) | refused |
| `subscript read`, `read_str`, `map_get` | IndexError / KeyError | Subscript | refused (#177) | refused |
| `subscript write`, `write_bytes`, `del` | IndexError / ValueError / KeyError | — (statement-only) | n/a | n/a |
| `call chr` | ValueError | Call chr | **PROVED** (p211/p236) | refused |
| `call divmod`, `attr_call pop`, `attr_call index`, `call next` | ZDE / KeyError / ValueError / StopIteration | Call / Method | refused (route #65 orphan walk descends into comprehensions; measured) | refused (both) |
| `call int_str` (#281) | ValueError | Call str/repr/format/print, FString, FormattedValue, BinOp `%`/`mod` | **PROVED** (p196/p199/p207/p208) | refused |
| `call format_spec` (#284, new) | ValueError | FormattedValue, Call format, Method format | — | refused |

Non-table refusals (route #161 call whitelist, #66 `int(<str>)`, #72 `split`) walk the whole body and already
fire inside comprehensions (measured: `[int(v) for v in ss]`, `[format(v, "s") ...]` refused at base).

**Probe table** (rc; CPython ground truth in each `__main__`):

| shape | 323066f9 | after |
|---|---|---|
| p196 / **3272** `[str(x) for x in xs]`, `xs = [10**5000]` | PROVED (rc 0) | REFUSED (rc 1) |
| p199 / **3273** `",".join(str(x) for x in xs)` | PROVED | REFUSED |
| p207 / **3274** `[f"{x}" for x in xs]` | PROVED | REFUSED |
| p208 / **3275** `[repr(x) for x in xs]` | PROVED | REFUSED |
| p211 / **3276** `[chr(x) for x in xs]`, `xs = [-1]` | PROVED | REFUSED |
| p236 `{x: chr(x) for x in xs}` | PROVED | REFUSED |
| p214 / **3277** `[1 << x for x in xs]` | PROVED | REFUSED |
| p235 `sum(1 << x for x in xs)` | PROVED | REFUSED |
| p237 / **3278** `[x >> n for x in xs]`, `n = -1` | PROVED | REFUSED |
| **3279** controls: `[x + 1 ...]`, `sum(x for ...)`, `[x for ... if x > 0]` under `\all`; `[str(x)]`/`[chr(x)]`/`[1 << x]` under `no_exception KeyError` | PASS | PASS |
| `[x // n ...]`, `[xs[n] ...]` (route #177) | REFUSED | REFUSED (same message) |

All 9 route witnesses `witnesses-r285/` rc=0 at HEAD -> rc=1 after.

**Blast radius.** No corpus / pyref / mirror file moved, went GONE or APPEARED on account of this rule (the only
movers are #284's: root 3118, mirror `exception_model`). The table over-approximates (any `str(...)`/f-string/
`%` in a comprehension under a `ValueError` context, whatever the operand type) — measured cost 0.

**Gates** (logs under the r284 executor scratchpad `scratchpad/r284/` in the worktree): witnesses (corpus 3260-3279
and all 19 route witnesses) at 323066f9 vs after as tabled (every false claim rc 0 -> rc 1; controls 3271/3279
rc 0 both sides); byte-diff-sweep base/after rc=0 (2479 / 2499 sources); byte-diff-compare root rc=0 with
`--expect-moved 3118_gen37_r281_repr_and_formatted_huge_int_false_claim` (1 MOVED, 0 GONE, 0 APPEARED, 13 new
sources emitted, 7 new refusals), pyref rc=0 (0/0/0, 2186/2186); mirror-emit-sweep base/after rc=0, compare
1 MOVED = `exception_model` (type-check + whole-file proof `pycsl.py --import-path src/pycsl
src/self-annotate/src/exception_model.py` SUCCESS); check-self-annotate-sync.sh rc=0 (923 verbatim, 37
constants subset); self-annotate-mirror-check.sh rc=0 (53); refusal-witness census +18 rows (7 REFUSAL via the
plane's `_census_row`, 11 VERIFY-FAIL as measured), refusal-witness-coverage OK (240 demonstrated, 4
undemonstrated, ceiling 5); `run-soundness-planes.sh` fast rc=0, all 61 green. OWED: `--slow` (23 planes).

**Residuals.** The comprehension is still REFUSED, not modelled (write the loop: the per-statement obligations
then apply). Shape matching is syntactic over the IR: a same-file callee raising inside a comprehension is route
#178's (callee) concern, not this table's. `TypeError`/`OverflowError` are outside `KNOWN_EXCEPTIONS`.
