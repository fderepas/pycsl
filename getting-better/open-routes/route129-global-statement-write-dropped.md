# ROUTE #129 — a write through a `global` declaration is DROPPED (lowered to a fresh local), and every read
# of a non-constant module variable is ONE opaque constant, across the write

**Status: OPEN (found by gen #24, 2026-09-15) — not repaired; scope below.**
**Severity: SEV-1. First-order.**

## MEASURED at HEAD `0a3d1d2e`
```python
XS: List[int] = [1, 2, 3]
N = len(XS)

#@ assigns \nothing
def setn() -> None:
    global N
    N = 5

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = N
    setn()
    return a - N
```
`[+] Verification SUCCESS`; CPython prints -2. Emission: `val constant n : int`; `setn` = `let n = ref 0 in let n = ref
5 in ()` (a fresh local); `f` = `a := n; setn (); !a - n`. The frame `assigns \nothing` on `setn` is false and
proved; the honest `#@ assigns N` is refused ("Undefined variable 'N' referenced in contract").
Control (FAIL-CLOSED): with a foldable `N = 3`, `setn(); return N == 3` is refused (a written global is not folded).

## WHY IT IS NOT A ONE-LINE REFUSAL
`src/pycsl_lib` writes module state exactly this way under `#@ assigns \nothing`: warn/__init__.py
(`__exit__`: `global _filter_actions, _filter_categories`), sysmod, iomod, subproc, tmpf; python-reference 0181
(`global _test_g; _test_g = 10; return _test_g`, expected PASS). A refusal of every `global` write in a lowered
function refuses those stdlib modules wherever a stdlib test ingests them. CENSUS FIRST: which of those functions
are lowered (not `\trusted`), whether any caller reads the written global, and whether a `writes`-carrying model
of the global (the `_shared_var_names` concurrency path already derefs `!name`) can be reused.
Driver: `scratchpad/g24/p5/global_unannotated_write.py`.
