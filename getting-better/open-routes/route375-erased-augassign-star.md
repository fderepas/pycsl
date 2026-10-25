# OPEN ROUTE #375 — AUGMENTED ASSIGNMENT / STAR-UNPACK OF AN ERASED VALUE IS UNCHECKED
**Status: OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r375/`: `p12_star_list.py`, `p21_augadd_self.py`, `p45_alias_add_param.py`, `p47_star_set_erased.py`, `p49_alias_mul_noexc.py`.

R337 refuses `self += 1` directly but not through an alias (`t = self; t += 1` / `*= 2`, p21/p49) or on a parameter (p45); a starred display element `[*self]` / `{*self}` is emitted as the plain element (p12/p47). Slips past #358/#337/R343. CPython TypeError.

Repair: Propagate erasure through simple aliases into AugAssign (refuse / failing assertion under no_exception); lower starred elements of an erased value through the failing iteration assertion.
