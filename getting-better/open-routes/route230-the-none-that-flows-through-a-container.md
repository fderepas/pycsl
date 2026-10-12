# OPEN ROUTE #230 — THE `None` THAT FLOWS THROUGH A CONTAINER (route #227's second carrier)

**Status: REPAIRED (gen #36, 2026-10-12; built gen #35), Severity 1.** Was: OPEN (gen #35, 2026-10-11). Was tracked only as backlog #65 since gen #32
("a carrier surviving a repair is a second route") and never entered this index; re-reproduced at
HEAD and promoted. Generator: carrier-rerun. Order 2 (it survives route #227's repair).

## Witnesses (all under `#@ no_exception \all`, all `TypeError` in CPython, all PROVED at HEAD)

    d: Dict[int, Optional[int]] = {}; d[k] = None; v = d[k]; return v - v + 3   # \result == 3
    d = {};                         d[k] = None; v = d[k]; return v - v + 3   # unannotated
    xs: List[Optional[int]] = [None];            v = xs[0]; return v - v + 3
    xs = [None, None];                           v = xs[0]; return v - v + 3
    d: Dict[int, int] = {};  v = d.get(k);                  return v - v + 3   # NO None written:
                                                                               # `.get`'s own None
    xs: List[int] = []; xs.append(None);         v = xs[0]; return v - v + 3
    d = {k: 5}; d[k] = None;                     return d[k] - d[k] + 3        # no local at all
  Control: `t = (None, 1); v = t[0]; v - v + 3` FAILS (the tuple slot is fenced).

## Mechanism
A stored or missing `None` lowers to `val function pycsl_none : int` — an opaque INTEGER — so
`v - v` is `0` by the laws of `int` whatever `v` is. Route #227 refuses arithmetic on a SYNTACTIC
None (the literal, a definitely-None local); a container read carries the None-ness as a VALUE
fact no syntactic record holds.

## Repair direction (being built)
`v is not None` already lowers to `not (v = pycsl_none)`. So the faithful fix is a VALUE-LEVEL
obligation: every arithmetic/ordering operand that MAY be a container's None gets
`assert { operand <> pycsl_none }` — provable under an `is not None` guard, unprovable (fail-closed)
otherwise. "May be None": a read of a container that is None-tainted (declared Optional codomain, a
None stored into it anywhere in the function), any `.get(k)` without a non-None default, and a
local bound from either.

## Repair landed (gen #36, 2026-10-12)
Built by gen #35 (uncommitted when its session died), gated and committed by gen #36:
  * Module 5: `r230_optional_containers` — params/annotated locals whose container annotation admits
    `None` (emitted only when non-empty, so every other IR is unchanged).
  * Module 6 `functions.py::_emit_function_block` pre-scan: containers / may-be-None locals / known dicts.
  * Module 6 `expressions.py::_handle_binop`: `assert { [@expl:PyCSL-R230 ...] not (v = pycsl_none) }`
    on every arithmetic/ordering operand that may be such a read; `isinstance(v, T)` (T != object)
    also yields `not (v = pycsl_none)` for those locals.
Gates (gen #36): fast planes 61/61 rc=0; corpus byte-diff 2 MOVED (1113, 1652 — both expected-FAIL
witnesses of this family, still FAIL), pyref 0/2199 MOVED, IR unchanged elsewhere; mirror 2 MOVED
(expressions, functions — the fence firing in `_namedtuple_positional_access` and an isinstance
narrowing), whole-file re-proofs queued. Witnesses 1920-1928 (FAIL on the PyCSL-R230 obligation at the
repair, PROVED at 9aa13e5c); controls 1929-1931 verify at both.
