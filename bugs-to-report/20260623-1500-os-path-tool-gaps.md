# os.path tool gaps — rfind/split/join opaque + variadic type error

**Date:** 2026-06-23 15:00 (updated 2026-06-23 16:30)
**Status:** PARTIALLY RESOLVED (3/6 body-verified; 3/6 remain `\abstract`)
**Filed by:** test-supervise-sl (os.path + codec fleet run)

## Summary

Six of ten `os.path` functions (`abspath`, `basename`, `dirname`, `join`,
`normpath`, `splitext`) could not be body-verified by PyCSL due to two tool
gaps in string-operation lowering. They were marked `#@ \abstract` (zero-TCB
bodyless vals, no `ensures`) in `src/pycsl_lib/os/path.py`.

**UPDATE (2026-06-23):** Strategy A (pure-Python reimplementation with
PyCSL-supported string primitives) LANDED for **basename, dirname, join** —
now body-verified with length-bound `ensures`, zero-TCB. The remaining
**3/6** (`abspath`, `normpath`, `splitext`) stay `\abstract`; their specific
blockers are documented per-function below.

## Gap 1 — `str.rfind`, `str.split`, `str.join` lower to opaque abstract vals

PyCSL lowers `path.rfind('/')`, `path.split('/')`, and `'/'.join(parts)` to
opaque WhyML `val`s (`path_rfind_1`, `path_split_1`, `join_1`) with **no
contracts** (no `ensures` on the return value). The bodies of `basename`,
`dirname` (rfind), `normpath` (split + join), `abspath` (calls normpath),
and `splitext` (rfind + slicing) depend on these return values; with no
contract, the substring bounds and result values are unpinnable.

**Affected functions:** `basename`, `dirname`, `normpath`, `abspath`,
`splitext`.

**Why `\abstract` (not `\trusted`):** `\abstract` emits a bodyless `val`
with NO `ensures` — a pure signature that assumes nothing (zero TCB growth).
`\trusted` would assume the body unchecked (TCB growth, forbidden by the
doctrine). The Python body is retained for runtime; only the verification
body is discarded.

## Gap 2 — variadic `*parts: str` emits a WhyML `string + int` type error

`os.path.join(a: str, *parts: str)` uses a variadic parameter. PyCSL models
`*parts` as an opaque int iterator (`val constant parts : int`,
`val iter_get (x: int) (i: int) : int` — returns `int`, not `string`).
The body's `result = result + p` (string + string) emits as
`py_result := !py_result + !p` where `!p` is `int` → WhyML type error
" This expression has type int, but is expected to have type string". This
error prevents the ENTIRE module from loading (no goals discharge).

**Affected function:** `join`.

**Fix applied:** mark `join` `#@ \abstract` (bodyless val) → suppresses the
type error, module loads, other functions verify.

## Repro

```bash
# Before the \abstract marks (on the unmodified path.py), the module fails:
PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/os/path.py
# → "This expression has type int, but is expected to have type string" (join)
# After the \abstract marks: SUCCESS (4 functions body-proven, 6 abstract)
```

## What IS proven (the 4 body-verified os.path functions)

- `exists(p)` — `ensures \result == 0` (no filesystem binding)
- `expanduser(p)` — `ensures \result == p` (identity, no home binding)
- `isabs(p)` — `ensures \result ∈ {0,1}` + leading-slash ==> 1 + empty ==> 0
- `isdir(p)` / `isfile(p)` — `ensures \result == 0` (no binding)

These are caller-tested in `src/pycsl_lib_test/formal_os_path.py` (8 theorems,
all SUCCESS, 0 `\trusted`).

## Suggested tool fix (for the PyCSL tool team)

1. Model `str.rfind` / `str.split` / `str.join` with faithful contracts
   (return-range + length bounds) instead of opaque no-contract vals.
2. Model variadic `*parts: str` as an iterator returning `string` (not
   `int`), or unroll small variadic arities.

Either fix would let the 6 `\abstract` functions become body-verified
(zero-TCB reduction — shrinking the abstract surface).
