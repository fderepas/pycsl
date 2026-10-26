# OPEN ROUTE #409 — §7.49 (3) A STANDARD-LIBRARY MODULE ATTRIBUTE IS ADMITTED AS A HASHED VALUE WITHOUT CLASSIFYING IT
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r409/`: `b21_stdlib_mutable_obj.py`, `f37_from_os_environ.py`, `f43_global_stdlib_attr.py`, `f38_sys_argv.py`, `f40_logging_root_handlers.py`, `q13_environ_copy.py`.

```
#409 §7.49 (3) A STANDARD-LIBRARY MODULE ATTRIBUTE IS ADMITTED AS A HASHED VALUE WITHOUT CLASSIFYING IT  [slips past #394]
  b21  {os.environ}  f37 from os import environ; {environ}  f43 E = os.environ; {E}  f38 {sys.argv}
  f40  {logging.root.handlers};  q13 {os.environ.copy()} (a method call on the stdlib object)    TypeError
  (b22 {sys.path} and f39 {sys.modules} are refused by the imports layer.)
  REPAIR: "by the real object" must read the attribute's value: type(value).__hash__ is None (or the object is a
  container) => unhashable; a dotted chain through a non-module object, or an attribute not resolvable => UNKNOWN,
  refused in a hashing position.
```
