# ROUTE #181 — the source-level exception checks of #175/#179 ignore imported modules

**Status: REPAIR DRAFTED by gen #29 (worktree wtAB, branch wip/g29-r181, on top of #180).** Severity 1.
Generator: carrier-rerun of the landed #175/#179 (multi-file).

## Measured at `65d0b736`, each PROVED

    # lib: class C: __init__ raises ValueError on v < 0;  class MyErr(ValueError)
    from lib import C       try: C(-1) except ValueError: return 9; return 0     == 0   (CPython 9)
    from lib import C       #@ no_exception ValueError   C(-1)                           (CPython raises)
    from lib import MyErr   try: raise MyErr() except ValueError: return 9           == 0   (CPython 9)

`pycsl.py::_run_pipeline` parsed only the main file's source; the imported class's base and raising
constructor were invisible. (A callee raising the imported subclass was already refused.)

## Repair (draft)

The dependency modules named by imports (resolved against the main file's directory and
`--import-path`, transitively, capped at 64 files) are parsed; their classes, aliases and functions
feed the class / raise maps of both checks, while only the main file's functions are checked (and a
dependency function's `#@ raises` directive is not read from the main file's lines). The census
exposed a latent bug in both checks: trusted functions were matched by `name.rsplit("__")`, which
drops a leading underscore (`cls___m` -> `m`); they are now matched by exact IR name
(`<class_lower>__<method>`). Emission byte-inert (corpus/pyref/mirrors) after that fix (before it, the
mirror `Module6_WhyMLTranspiler` was refused). Witnesses 1639-1641 (XFAIL), 1642 (PASS), helper
`multi_file_lib/r181_raising.py`. Fast planes 19/19, conformance, sync green.
