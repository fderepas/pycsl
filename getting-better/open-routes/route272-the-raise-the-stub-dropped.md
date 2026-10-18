# OPEN ROUTE #272 — A CALLEE'S UNDECLARED ESCAPING `raise` IS DROPPED AT THE CALL; `no_exception \all` PROVES

**Status: OPEN (gen #36, 2026-10-18), Severity 1.** Residual of the #269 repair; driver-reproduced at HEAD 6859202e (rc=0;
CPython raises ValueError for `C().m(1)`).
Witness `witnesses-r272/selfcall_undeclared_raise_no_exception.py`: `chk(k)` raises ValueError for k > 0 without
`#@ raises`; `m` (`no_exception \all`) calls `self.chk(k)` and proves. With a declared `#@ raises` the call is
correctly asserted.
Mechanism: undeclared exceptions use the partial-correctness reading for the callee itself, but the caller's stub
(`val self_chk_...`) carries no `raises`, so a `no_exception` caller never sees the possible exception.
Repair: a callee whose body may raise (any modelled raise site, declared or not) must expose that at every call
site under `no_exception` (refuse, or an unprovable obligation), for every call form (self./obj./Class./function).
