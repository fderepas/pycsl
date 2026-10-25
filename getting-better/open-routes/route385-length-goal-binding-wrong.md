# OPEN ROUTE #385 — THE `\length` CONSTRUCTOR GOAL BINDS THE FIELD AT ITS STORE; `[] * N`; UNCHECKED `requires` AT `super().__init__`
**Status: OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r385/`: `c02_len_inv_empty_repeat.py`, `c03_len_inv_param_cleared_in_init.py`, `c31_len_inv_subclass_super_empty.py`, `c34_len_inv_mutable_default_shared.py`, `c35_len_inv_tuple_unpack_store.py`, `c45_len_inv_param_tok_extend.py`, `l04_sub_super_slice.py`.

A later `toks.clear()` / `toks.extend()` through the parameter alias or a tuple re-store is ignored by the goal; `[] * 4` yields premise `length = 4`; the `requires len(toks) >= 1` premise is never checked at `super().__init__([])` / `super().__init__(toks[1:])`. CPython IndexError / count 4 against `<= 1`. (c34 boundary: the unverified caller keeps an alias and clears it.)

Repair: Bind the field from its value at the END of `__init__` or refuse when an alias / call / second store can reach it; `[] * N` has length 0; check `__init__`'s `requires` at every `super().__init__(..)` / `C.__init__(self, ..)` site.
