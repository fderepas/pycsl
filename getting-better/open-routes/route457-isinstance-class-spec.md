# OPEN ROUTE #457 — #441 CLASS-SPEC code admits any imported name: `isinstance(x, sqrt)`, `isinstance(x, Any)`, `(int, join)` (TypeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r457/` (5): `c23_i000.py`, `c23_i001.py`, `c23_i002.py`, `c23_i004.py`, `c23_i005.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F14 -- #441 CLASS-SPEC code admits any imported name: `isinstance(x, sqrt)`, `isinstance(x, Any)`, `(int, join)` (TypeError)   (5)
  EXEMPLAR c23/i005.py  PROVED (rc=0 Verification SUCCESS):
    | from json import loads
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(x: int) -> int:
    |     if isinstance(x, loads):
    |         return 1
    |     return 0
    CPython 3.14: f(1)  ->  VIOLATION TypeError isinstance() arg 2 must be a type, a tuple of types, or a union
  MECHANISM: #441's isinstance row codes argument 2 as CL (class or tuple of classes) but, as its residual (4) states, the code
  admits ANY imported name -- a function (`sqrt`, `math.sqrt`, `json.loads`, `os.path.join` inside a tuple) and
  `typing.Any`; #442 then simply does not narrow, and the call lowers to an opaque test with no raises.
  Subscripted generics (`List[int]`, `Sequence[int]`), TypeVar, Literal, non-runtime Protocols ARE refused.
  REPAIR: ALLOW-LIST for CL: a name resolving (statically, through the import) to an object `o` with `isinstance(o, type)`
  (checked on the real imported object, as #442 does for builtins), a PEP 604 / typing.Union of such, or a tuple
  of these; refuse functions, typing.Any and every other special form (TypeError).
  MEMBERS: c23/i000.py c23/i001.py c23/i002.py c23/i004.py c23/i005.py
```
