# OPEN ROUTE #408 — THE READ-ONLY TEST OF A MODULE CONTAINER GLOBAL (§7.49 (1)) DOES NOT SEE A SUBSCRIPT STORE IN THE __main__ DRIVER
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r408/`: `b02_global_sub_store_main.py`.

```
#408 THE READ-ONLY TEST OF A MODULE CONTAINER GLOBAL (§7.49 (1)) DOES NOT SEE A SUBSCRIPT STORE IN THE __main__ DRIVER  [slips past #394]
  b02  XS = [1, 2]; f hashes {XS[0]}; __main__ does XS[0] = [5] then calls f                   TypeError
  (The same store in a module function (b01), a rebinding of K in __main__ (b07), XS.append in __main__ (f23),
  G["a"] = .. / del G["a"] in __main__ (f24, f28), C.XS[0] = .. in __main__ (f25) are refused. f26 / f27, the
  ensures / IndexError forms, time out -- not counted.)
  REPAIR: the read-only census counts every Store-context Subscript / AugAssign whose base is the global, in the
  driver too (the rebinding census already reads the driver).
```
