# OPEN ROUTE #406 — GD's STORE CENSUS (§7.53) MISSES STDLIB CALLS THAT SET ATTRIBUTES ON AN ARGUMENT
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r406/`: `c20_getattr_ns_init.py`, `f49_getattr_ns_init_module_fn.py`, `c21_getattr_update_wrapper.py`, `f44_getattr_parse_args_ns.py`, `k01_getattr_optparse.py`, `k02_getattr_mock_patch.py`, `f47_getattr_objgetattribute_dict.py`, `k04_getattr_ns_classattr_hash.py`, `h14_classattr_ns_shadow.py`.

```
#406 GD's STORE CENSUS (§7.53) MISSES STDLIB CALLS THAT SET ATTRIBUTES ON AN ARGUMENT  [slips past §7.43 / §7.53 / §7.49 (2)]
  c20  R.__init__: argparse.Namespace.__init__(self, k=5); getattr(r, "k", 0) == 0 PROVED      5
  f49  same call from a module function on the receiver
  c21  functools.update_wrapper(self, S(), assigned=(), updated=("__dict__",))                 5
  f44  argparse.ArgumentParser().parse_args([], namespace=self)                                5
  k01  optparse.Values.__init__(self, {"k": 5});  k02 unittest.mock.patch.object(self, "k", 5, create=True).start()
  f47  object.__getattribute__(self, "__dict__")["k"] = 5 (the `__dict__` touch is a STRING)  5
  k04  the same Namespace call rebinding a FIELD x = [1]; {r.x} PROVED                          TypeError
  h14  class attribute K = 1 shadowed by Namespace.__init__(self, K=[1]); {c.K} PROVED          TypeError
  (setattr through functools.partial / map / importlib, object.__setattr__ via a dict lookup, a subclass
  __getattr__ / __getattribute__ are refused: n01, n02, k03, c30, h10, h11.)
  REPAIR (allow-list): a receiver (self, or any object) passed as an argument to a callee that is not a file
  function / a modelled builtin with a known frame, or appearing in `object.__getattribute__(x, "__dict__")` /
  any string-named dunder access, makes its class's binding set UNKNOWN for GD and its fields / class-attribute
  reads UNKNOWN as hashed-value sources.
```
