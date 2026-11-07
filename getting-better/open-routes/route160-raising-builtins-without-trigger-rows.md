# ROUTE #160 — builtins that raise with no trigger row prove a matching `no_exception`

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery H (with #158/#159).** Severity 1.

## Measured at `e27e6797` — each PROVED, CPython raises

    for i in range(0, 5, 0): ...     no_exception ValueError         (zero step)
    len("a".split(""))                no_exception ValueError         (route #72 carrier: expression receiver)
    pow(0, -1)                        no_exception ZeroDivisionError  (the `**` binop row is wired, `pow()` is not)
    max([])                           no_exception ValueError         (empty iterable, no default)

## Repair (route #65/#72 convention — refuse where no faithful obligation exists)

In `_reset_function_state` (trusted): a Call carrying `receiver` is keyed as an `attr_call`, so #72's
split refusal sees it; `range` with a step that is not a nonzero literal, `pow` whose exponent is not a
non-negative literal (and base not a nonzero literal), and single-argument `max`/`min` without
`default=` over anything but a non-empty literal are REFUSED when the function claims the matching
`no_exception`. Witnesses 1547-1550 (XFAIL), 1551-1553 (PASS controls).

**Battery H (every leg predicted and hit):** emission measured BEFORE predicting (stated) — vs the
#155-#157-closed tree 1180 -> 1196, 0 MOVED / 0 GONE / 0 APPEARED, python-reference and mirrors
inert; conformance 38/38 + 38/38; suite 3679/3697 same 18, zero XPASS; planes --slow 34/34.
