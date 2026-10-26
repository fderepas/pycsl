# OPEN ROUTE #407 — §7.49 (1) "PRIMITIVE ARITHMETIC" (AND BoolOp / IfExp / slice) OVER A CONTAINER GLOBAL IS TAKEN AS HASHABLE
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r407/`: `b04_global_arith_list.py`, `f29_global_add_lists.py`, `f30_global_or_list.py`, `f31_global_dict_union.py`, `f32_global_set_minus.py`, `f35_global_slice_list.py`, `f36_global_ifexp_list.py`, `q07_global_listdisplay_mul.py`, `q18_global_tuple_add_list.py`, `q17_classattr_list_mul.py`.

```
#407 §7.49 (1) "PRIMITIVE ARITHMETIC" (AND BoolOp / IfExp / slice) OVER A CONTAINER GLOBAL IS TAKEN AS HASHABLE  [slips past #394]
  b04  A = [1]; K = A * 2; {K} PROVED                                                          TypeError
  f29  K = A + B;  f30 K = A or 1;  f31 K = A | {"b": 2} (dict);  f32 K = A - {2} (set);  f35 K = A[:];  f36 K = A if A else (1,)
  q07  K = [1] * 2 (no global operand at all);  q18 K = .. if False else B + [3];  q17 the same in a CLASS body, {C.K}
  (list(..), a comprehension, [*A], sorted(..), a set display, {**A} are refused: q08-q12, q20.)
  (b05 `K = (1, A)` is refused correctly: the tuple source reads its components.)
  REPAIR: arithmetic `+ * | - & ^` with a container operand has the container's class; BoolOp / IfExp is the union
  of the operand classes; a slice of a list / str / tuple is that class; anything else UNKNOWN.
```
