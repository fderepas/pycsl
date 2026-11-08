# OPEN ROUTE #281 — int -> str OF > 4300 DIGITS RAISES ValueError (sys.int_max_str_digits), UNMODELLED
**Status: REPAIRED (gen #37, 2026-10-19; opened the same day), Severity 2.** Faithful trigger, no assumption needed (measured cost 0). Red-team round 6; driver-reproduced at 78162575 (4 files rc=0; CPython 3.11+ ValueError).
Witnesses `witnesses-r281/`: `str(x)`, `f"{x}"`, `print(x)` under `no_exception \all` / `no_exception ValueError` with
`x = 10**5000`. Repair: an exception trigger (ValueError unless |x| < 10**4300) on every int->decimal-str conversion
(str/f-string/format/print/repr/%d), or a declared model assumption with an opt-in strict mode (#250/#276 precedent).

## REPAIR (2026-10-19, r277 executor, off 72ab1c57) — the faithful trigger

**Rule.** New `exception_model.TRIGGERS` row `("call", "int_str")`: `ValueError` unless
`(- 10^4300) < x < 10^4300` (CPython 3.11+ `sys.int_max_str_digits` = 4300 digits; the literal
constants are emitted, no `int.Power`), mirrored verbatim in `src/self-annotate/src/exception_model.py`.
Wired through the single chokepoint `_maybe_emit_no_exception_assert` (so only under a
`no_exception` covering `ValueError`, never in a contract) at every int -> DECIMAL conversion the
emitter lowers, asserting on the OPERAND so a term keeps its head (local typing reads it):
`str(x)` (`str_of_int`), `repr(x)` / `format(x)` (`*_conv`), every non-string `print` argument,
the int parts of the int-model f-string joiner and of the `@mutable_state` string joiner, a
`FormattedValue` with an int operand under `!s`/`!r`/`!a` or a decimal spec (none/`d`/`n`; a
computed spec owes it too; `b`/`c`/`o`/`x`/`X` do not, float types raise `OverflowError`, outside
the tracked set), and the int operands of `"…" % x` / `% (…)`. All edited methods have `\trusted`
mirror twins; no new def; ledger 3. Docs: static semantics (no_exception obligation), translational
§T.8 trigger table, the `pycsl-exception-model` skill table, README.

**Probe table** (rc; CPython 3.11+ raises `ValueError` for `x = 10**5000` in each FAIL row):

| shape | 72ab1c57 | after |
|---|---|---|
| p173 / **3114** `str(x)`, `no_exception \all` | PROVED | FAIL (assertion) |
| p174 / **3115** `f"v={x}"` | PROVED | FAIL |
| p175 / **3116** `print(x)` | PROVED | FAIL |
| p176 / **3117** `str(x)`, `no_exception ValueError` | PROVED | FAIL |
| **3118** `repr(x)`, `f"{x!r}"`, `f"{x:d}"` | PROVED | FAIL |
| **3119** controls: bounded `x` through every form, `f"{x:x}"` unbounded, `no_exception KeyError`, no `no_exception` | PASS | PASS |

**Cost: 0.** The corpus/pyref/mirror byte-diff shows NO file moved on account of this rule (the
movers are all #277/#278's) — no existing `no_exception` function converts an int to decimal text,
so the declared-assumption fallback was not needed.
Residuals: `"%d" % x` bound to a local is already a type error (`ref 0` local typed int against
`str_mod_op`'s string — fail-closed, pre-existing); `format(x, spec)` (two arguments) and
`"{}".format(x)` are refused under `no_exception` by route #161's whitelist (not whitelisted);
`str(xs)` / `print(xs)` of a LIST of ints is a Why3 type error (fail-closed), so the element-wise
obligation is not needed today; `int(s)` of a > 4300-digit string (the reverse direction) is
already refused under `no_exception` (`int(<str>)` partial case, route #161).
