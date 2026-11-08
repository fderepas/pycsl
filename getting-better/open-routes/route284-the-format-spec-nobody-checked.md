# OPEN ROUTE #284 — f-STRING FORMAT SPECS ON int/str: THE #281 DIGIT-LIMIT TRIGGER AND INVALID-SPEC ValueError ARE NOT EMITTED
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Faithful trigger + emit-time spec validity, no assumption. Red-team round 7; driver-reproduced at 83aa79bd (p223/p057/p063/p064/p062 rc=0; CPython ValueError).
Witnesses `witnesses-r284/`. (a) `f"{x:d}"`, `:5`, `:05d`, `:n`, `:,`, `:>10`, `v={x:d}` under `no_exception \all`: the #281
`("call","int_str")` guard is computed in the literal-spec branch (~expressions.py:19449) but its assert is never emitted
(corpus 3118 FAILs only because of its repr/!r lines — the witness over-claims coverage). (b) invalid specs raise ValueError in
CPython and are not modelled: `f"{x:s}"` / `f"{x:.2}"` on int, `f"{s:d}"` on str. Repair: emit the digit-limit assert for every
int decimal rendering spec (not `:b/:x/:o`), and refuse or trigger on every spec not valid for the operand's type.

## REPAIR (2026-10-20, r284 executor, off 323066f9)

**(a) Root cause — a one-identifier typo.** The literal-spec branch of the `FormattedValue` lowering
(`_expr_to_whyml`, ~expressions.py:19449) computed the presentation type into `_r281_ty` and then tested
`_r231_ty in ("", "d", "n")` — `_r231_ty` is the operand's WhyML TYPE (`"int"`/`"string"`), so the test was
False for every literal spec without a conversion and the #281 assert was never emitted. Now tests `_r281_ty`.

**(b) Invalid specs — new row `("call", "format_spec")`: `ValueError`, template `false`** (mirrored verbatim in
`src/self-annotate/src/exception_model.py`). Consulted (only under a `no_exception` covering `ValueError`) when:
- a LITERAL f-string spec is invalid for the formatted type — decided at EMIT TIME by CPython's own
  `format(sample, spec)`: sample `""` for a str operand or after a `!s`/`!r`/`!a` conversion, `0` for an operand
  SHOWN to be an int (int literal, `int`/`bool` local, `len`/`int`/`abs`/`ord`/`hash`/`sum`, an int-only
  operator), and BOTH otherwise (the "i" operand class only means "not shown to be a str": an int-hash-modelled
  str element is an int in Why3). Spec validity is value-independent for int and str. A width/precision of more
  than 6 digits is not tried (allocation) and counts as undecided;
- the spec is COMPUTED (`f"{x:{w}}"`): `w = "s"` raises, validity is not modelled;
- a `%` format (`"…" % x`, `_handle_binop`) is not a literal, or CPython's `%` with one `0` per operand (retried
  with a `defaultdict(int)` mapping for `%(k)…`) raises `ValueError`, or neither sample decides it. SAME GAP,
  found while auditing the sibling paths: `"%q" % x` PROVED `no_exception \all` (bounded x, `-> str` / `print`
  shapes; a local binding of a `%` result is a pre-existing Why3 type error, fail-closed).
- `format(x, spec)`, `format(x)`, `"{:s}".format(x)` were VERIFIED already refused under `no_exception` by the
  route #161 call whitelist (also inside a comprehension) — no change needed.

Both edited methods (`_expr_to_whyml`, `_handle_binop`) have `\trusted` mirror twins (body `return ""`); no new
def, no new field, no axiom (ledger 3). Docs: README, static semantics (no_exception obligation), translational
§T.8 trigger table, `pycsl-exception-model` skill table.

**Probe table** (`pycsl.py` rc; CPython ground truth in each corpus file's `__main__`):

| shape | 323066f9 | after |
|---|---|---|
| p223 / **3260** `f"{x:d}"`, x unbounded | PROVED (rc 0) | FAIL (rc 1, int_str assert unproven) |
| p226 / **3261** `f"v={x:d}"` | PROVED | FAIL |
| p057 / **3262** `f"{x:5}"` | PROVED | FAIL |
| p060 / **3263** `f"{x:05d}"` | PROVED | FAIL |
| p059, p051 / **3264** `f"{x:n}"`, `f"{x:,}"` | PROVED | FAIL |
| p055 / **3265** `f"{x:>10}"` | PROVED | FAIL |
| p063 / **3266** `f"{x:s}"` on int (3266: x bounded) | PROVED | FAIL (`assert false`) |
| p064 / **3267** `f"{x:.2}"` on int (bounded) | PROVED | FAIL |
| p062 / **3268** `f"{s:d}"` on str | PROVED | FAIL |
| **3269** `print("%q" % x)` (bounded) | PROVED | FAIL |
| **3270** `f"{x:{w}}"` computed spec (bounded) | PROVED | FAIL |
| **3271** controls: bounded x through `:d` `v={x:d}` `:5` `:05d` `:n` `:,` `:>10` `!r:>5`; unbounded x through `:x` `:#06x` `:b`; str through `:>5` `:s` `:.2` `:^7`; `print("%5d\|%s\|%%" % (x, x))` | PASS | PASS |
| 3118 (`repr`/`!r`/`:d`) | FAIL (via repr/!r only) | FAIL (now also via `:d`) — docstring corrected |

All 10 route witnesses `witnesses-r284/` rc=0 at HEAD -> rc=1 after.

**Blast radius.** Corpus root 1 MOVED = 3118 (its `:d` line gains the bound; the intended change; re-proved:
FAIL as expected), 0 GONE, 0 APPEARED; pyref 0/0/0 (2186/2186); mirror 1 MOVED = `exception_model.mlw` (the
new data constants; type-check + whole-file proof SUCCESS). No existing `no_exception` function in either
corpus or the mirror uses a decimal/invalid/computed spec or a non-literal `%` format.

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

**Residuals.** A float/real operand of a spec is a Why3 type error (fail-closed, unchanged). `OverflowError`
(`f"{10**400:f}"`, `%c` out of range) and `TypeError` (`"%d" % "a"`) are outside `KNOWN_EXCEPTIONS` (scope).
An operand not shown to be an int now needs a spec valid for BOTH int and str (`:d` on a list element) —
incompleteness only. A width/precision of more than 6 digits always owes `false` (incompleteness).
