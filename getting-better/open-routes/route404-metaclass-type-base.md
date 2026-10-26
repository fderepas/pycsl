# OPEN ROUTE #404 — S1 ADMITS `type` AS A BASE, SO A FILE METACLASS IS MODELLED AS NOTHING: ITS __eq__/__hash__/__bool__/ATTRIBUTES ARE IGNORED
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r404/`: `a12_metaclass_eq_hash.py`, `f07b_metaclass_hash_raise.py`, `f10_metaclass_classattr.py`, `f12_metaclass_instance_hash.py`, `j36_metaclass_eq_tuple_hash.py`, `j35b_metaclass_bool_while.py`, `h15_metaclass_attr_fallback.py`, `j33_metaclass_init_raise_attr.py`.

```
#404 S1 ADMITS `type` AS A BASE, SO A FILE METACLASS IS MODELLED AS NOTHING: ITS __eq__/__hash__/__bool__/ATTRIBUTES ARE IGNORED  [slips past S1 BASE-MODEL / §7.49 (1)(2)]
  a12  class M(type) with __eq__ only; class K(metaclass=M); {K} PROVED (a class is "a hashable object")  TypeError
  f07b M.__hash__ raises (conditionally);  {K}                                                     ValueError
  f10  {C.K} for a nested class K(metaclass=M);  f12 {type(k)};  j36 {(C, 1)}                     TypeError
  j35b `if C:` with M.__bool__ raising (no_exception)                                              ValueError
  h15  {C.K} where K is bound only on the metaclass (M.K = [1])                                    TypeError
  j33  {C.K}: C's body binds K = 1 but M.__init__ stores cls.K = [1]                               TypeError
  (h16 metaclass @property K, h21 / h25 / j30 / j34 ensures forms, f08 / j32b Type[B] params: Unknown / refused.)
  WHYML: `{K}` -> `any int`; `if C` -> `c <> 0` over a `val constant c`; C.K reads the class body binding.
  REPAIR: drop `type` from the BASE-MODEL table (S1 refuses `class M(type)` like any unmodelled base) unless the
  metaclass defines nothing; or: a class whose metaclass is a file class is UNKNOWN for hashing / truthiness /
  class-attribute sources, and `metaclass=` with a non-`type`/non-ABCMeta/non-EnumMeta value refuses the class.
```
