# OPEN ROUTE #348 — NamedTuple / collections.namedtuple / FROZEN DATACLASS ARE LOWERED AS MUTABLE RECORDS
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r348/`: `d11_namedtuple_store.py`, `j02_namedtuple_mutation_alias.py`, `j03_frozen_dc_free_fn.py`, `j07_collections_namedtuple.py`.

Emission `type n = { mutable x: int; mutable y: int }` and `n.x <- 5`: any field store on these types proves under `no_exception`; CPython raises AttributeError / FrozenInstanceError. (j01 method store: Why3 type error; d08 frozen store in a method: FAILs on its postcondition — not by design.)

Repair: Refuse attribute stores (and setattr/delattr) on NamedTuple, namedtuple and frozen-dataclass records, or emit them as raising.
