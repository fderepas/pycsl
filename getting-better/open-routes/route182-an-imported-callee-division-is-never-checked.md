# ROUTE #182 — a division inside an imported (trusted) callee is never checked

**Status: REPAIR DRAFTED by gen #29 (worktree wtAC, branch wip/g29-r182, on top of #181).** Severity 1.
Generator: carrier-rerun of #178 (imported callees).

## Measured at `76f39779`

    # lib: def div(x: int) -> int: return 10 // x
    from lib import div
    #@ no_exception ZeroDivisionError     v = div(0)                                   PROVED (CPython raises)
    try: v = div(0) except ZeroDivisionError: return 9;  return 0    == 0              PROVED (CPython 9)

An imported function is a trusted stub: its body is not verified in the importer, so `10 // x` carries no
obligation anywhere. Route #178 excluded ZeroDivisionError on the ground that callee divisions are
always checked in the callee — true for same-file verified functions (measured: refused), false for
trusted / imported ones. Imported KeyError/IndexError readers were already refused by #178.

## Repair (draft)

In #178's scan, a division (`/`, `//`, `%`, `**`) inside a `\trusted` / abstract function (every imported
stub) is a ZeroDivisionError source, and ZeroDivisionError joins the active set. Emission byte-inert.
Witnesses 1643, 1644 (XFAIL), 1645 (PASS, made non-vacuous after the vacuous-drivers ratchet flagged
the first draft), helper `multi_file_lib/r182_divider.py`.
