# OPEN ROUTE #308 — `c[k] op= v` EVALUATES THE INDEX/RECEIVER TWICE (`c[k] = c[k] op v` desugar)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 14; driver-reproduced on main (o05b, q03b rc=0; CPython violates).
Witnesses `witnesses-r308/`: o05b (index side effect counted twice), q03b (store lands in a different slot), o15 (dict),
q02 (list field), r04 (attribute list). Mechanism: Module5_IREmitter._py_stmt_augassign builds `ArraySet(c, k, BinOp(c[k], v))`
lowering `k` twice: emitted `ys[(nxt cnt)] <- (ys[(nxt cnt)] + 1)`.
Repair: evaluate the container and index ONCE into temporaries (Python: target container, index, then load, then v, op, store),
or refuse when the index/receiver expression is not side-effect-free (a pure name/literal/arith over locals). Interacts with #307
(order of `v` vs the load): Python evaluates container, index, load c[k], THEN v.
