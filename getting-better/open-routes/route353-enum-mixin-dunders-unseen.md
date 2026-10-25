# OPEN ROUTE #353 — DUNDERS SUPPLIED BY A NON-ENUM MIXIN ARE NOT SEEN BY THE #339 CLASSIFIER
**Status: OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r353/`: `e03_mixin_sub_intenum.py`, `e04_mixin_eq_enum.py`, `e26_mixin_hash_raise.py`, `e27_intenum_via_int_mixin_class.py`, `e29_mixin_lt_enum_base_chain.py`.

Dunders are collected from the class body and the file's enum bases only. A mixin `M` before IntEnum / int supplying `__sub__` / `__lt__` / `__eq__` leaves the enum 'transparent' (e03, e27, e29: `x - x == 0`, `x < x` False proved; CPython 1 / True), or `==` / `hash` admitted on an opaque enum (e04 `x == x` True vs False; e26 `__eq__` without `__hash__` => hash TypeError).

Repair: Compute dunders over the whole C3 linearisation (reuse #344's MRO code); an enum is int-like only if every class before `int` in its MRO is a stdlib enum class or `int`; an `__eq__` without `__hash__` anywhere in the MRO means `__hash__ = None`.
