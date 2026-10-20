# OPEN ROUTE #289 — A TUPLE HOLDING A LIST IS OPAQUE AND WRITES THROUGH ITS ELEMENT ARE NO-OPS
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r289/`. a028 `t: Tuple[List[int], int] = (xs, 0); b = t[0]; b[0] = 5; return xs[0]` proves `== \old(xs[0])` (CPython 5); a025 local variant (`return a[0]` folded to 1). The tuple lowers to `any int` and the store to a no-effect `val subscript_set (x:int)`. Repair: refuse stores/mutation through any value extracted from a tuple/container holding a mutable (or model it); census container-of-mutable shapes.

## REPAIR (2026-10-20, worktree pycsl-rB off 7313506b)
Root cause (located on the emission): a tuple holding a list is erased to `t := (any int)`; an element
taken from it is an int (`b := (subscript_get !t 0)`), and a store through that int reaches the last
fallback of `_handle_array_set_stmt`: `subscript_set !b 0 5` against `val subscript_set (x: int) (i: int)
(v: int) : unit` — no `writes`, no result: a NO-OP. The mutation of the aliased list is absent.

Probe table (`pycsl.py`, rc; base = 7313506b; 22-probe census under `scratchpad/rB/p289`, CPython violates
every claim):

| shape | base | after |
|---|---|---|
| `t: Tuple[List[int], int] = (xs, 0); b = t[0]; b[0] = 5; return xs[0]` (a028 / 3383) | PROVED | REFUSED |
| local twin (a025 / 3384), `t[0][0] = 5` (3385), nested tuple `((a, 0), 0)` (3386), unannotated tuple + `b[0] += 4` (3387), `(a, a)` second slot | PROVED | REFUSED |
| `t = mk(a)` (tuple returned by a call), tuple unpack `b, k = t` / `b, k = (a, 0)`, `List[List[int]]` element, `Dict[int, List[int]]` value, NamedTuple / dataclass field (`t.xs`), `b: List[int] = t[0]` annotated | FAIL (ill-typed, L3-tc) | unchanged FAIL (fail-closed) |
| `t[0].append(5)` / `b.append(5)` / `b.reverse()` on the element | REFUSED (#280 / #283 A / #14) | unchanged |
| partner write `a[0] = 5; return t[0][0]` | FAIL (`subscript_get` of `any int`: unknown) | unchanged FAIL |
| control 3388: a store through the list's own name beside a tuple | PASS | PASS |

Rule (`pycsl.py::_run_pipeline`, a GATE on the emission, next to #269's vanished-call check; new code
`PYCSL-SEM-STORE-THROUGH-OPAQUE-ELEMENT`): any APPLICATION of the abstract `subscript_set` (occurrences
beyond its `val` declaration) is refused, whatever reached it — that op has no modelled effect, so every use
is a dropped mutation. Placed as a gate rather than a `raise` in `_handle_array_set_stmt`, whose mirror stub is
`\trusted` with no `#@ raises` and whose live body raises nothing today (lesson d5: the raise would move
`check-trusted-raises-honesty`); `_run_pipeline` already raises. A faithful model (a tuple of an `array int`
and scalars) is the value-model capability routes #13/#17 need; measured disproportionate to the population
(below).
Census (container-of-mutable shapes): tuple (annotated, unannotated, nested, returned, unpacked), list of
lists, dict of lists, NamedTuple field, dataclass field — the stores that EMITTED all lowered to
`subscript_set` and are refused; the others are ill-typed before and after. Measured population of
`subscript_set` applications at 7313506b: corpus root 1 (0849, a `List[Dict[int,int]]` inner store,
`# pycsl-expected: FAIL`, ill-typed), pyref 0, mirror 0.
