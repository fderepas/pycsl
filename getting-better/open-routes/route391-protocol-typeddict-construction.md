# OPEN ROUTE #391 — PROTOCOL / TypedDict CONSTRUCTION AND isinstance PROVE
**Status: OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r391/`: `j08_protocol_instantiation.py`, `m02_typeddict_attr.py`, `m07_protocol_direct.py`, `n12_isinstance_typeddict.py`, `n13_isinstance_protocol.py`.

`P()` for a Protocol (also `Q(P, Protocol)()`), `TD(a=1).a` for a TypedDict (the call returns a dict), `isinstance` against a TypedDict or non-runtime_checkable Protocol, all under no_exception (#380 residual 4). CPython TypeError / AttributeError.

Repair: Refuse constructing a Protocol / TypedDict class; under no_exception refuse isinstance / issubclass against a TypedDict or a non-runtime_checkable Protocol.
