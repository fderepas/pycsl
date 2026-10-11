# OPEN ROUTE #230 — THE `None` THAT FLOWS THROUGH A CONTAINER (route #227's second carrier)

**Status: OPEN (gen #35, 2026-10-11), Severity 1.** Was tracked only as backlog #65 since gen #32
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
