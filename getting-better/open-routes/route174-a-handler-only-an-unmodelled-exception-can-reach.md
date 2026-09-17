# ROUTE #174 — a handler only an unmodelled exception can reach is dead in the proof

**Status: REPAIR DRAFTED by gen #29 (worktree wtU, on top of #173).** Severity 1. Generator: hand
(recorded open in route #173's batch).

## Measured at `546e366f` (and on the #173 draft), each `#@ ensures \result == 0`, CPython 9

    c: Optional[C] = None;  try: v = c.x               except AttributeError: return 9
    try: f = float(10 ** 400)                           except OverflowError: return 9
    try: s = bytes([255]).decode("utf-8")               except UnicodeDecodeError: return 9
    c: Optional[C] = None;  try: v = c.x               except Exception: return 9

The model raises only the five modelled implicit exceptions (routes #170-#173 widen and check those)
and explicit raises. Any other exception class is invisible, so its handler is dead code in the
proof; `except Exception` / `BaseException` / bare catch those classes too.

## Repair (draft)

`_reset_function_state` (trusted), in a claiming function (the #171/#172 gate: non-trivial
`ensures`, an assertion, a loop invariant/variant): a `try` handler is refused when it is broad
(`Exception`, `BaseException`, bare), or when its class covers none of the modelled implicit
exceptions and none of the classes raised explicitly in the `try` body (`raise` statements, or calls
to functions of this file declaring `raises`). Emission: corpus GONE = only #170/#172 witnesses
1585 (XFAIL), 1592 (XFAIL) and 1594, whose #172 PASS control (in-bounds read under `except
BaseException`) is now XFAIL by design; python-reference and mirrors inert. Witnesses 1599-1602
(XFAIL), 1603 (PASS: explicit FileNotFoundError under `except OSError`). Fast planes, conformance,
sync green.

## Completeness cost (recorded)

A claiming function can no longer use a broad handler at all, even around code that raises only
modelled or explicit exceptions (census: no PASS program in either corpus or the mirrors did).
