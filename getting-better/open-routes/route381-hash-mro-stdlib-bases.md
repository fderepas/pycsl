# OPEN ROUTE #381 — STDLIB BASES ARE SKIPPED IN THE `__hash__` MRO LOOKUP
**Status: OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r381/`: `h01_userlist.py`, `h02_userdict.py`, `h03_deque.py`, `h04_ordereddict.py`, `h05_counter.py`, `h06_defaultdict.py`, `h07_simplenamespace.py`, `h11_array.py`, `h12_argparse_ns.py`, `h13_collections_mod.py`, `h48_mixin_second_stdlib.py`, `h49_frozen_field_stdlib_sub.py`, `h51_abc_set_impl.py`, `h52_abc_mapping.py`.

Route #371 skips outside bases: `class D(B)` with B in UserList / UserDict / deque / OrderedDict / Counter / defaultdict / SimpleNamespace / array.array / argparse.Namespace / collections.UserList / abc.Set / abc.Mapping, `D(N, UserList)`, a frozen dataclass with a UserDict-subclass field: `{d}` under no_exception proves; CPython TypeError unhashable.

Repair: A table of stdlib classes known unhashable; any other outside base unknown => unhashable (per #371's own unknown rule).
