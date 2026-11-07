# OPEN ROUTE #396 — GD FOLDS getattr's DEFAULT WHEN ONLY A SUBCLASS BINDS THE ATTRIBUTE
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r396/`: `g01_subclass_sets_k.py`, `k52_subclass_classattr.py`, `k53_subclass_dataclass_field.py`, `k54_grandchild.py`, `k60_subclass_for_target.py`, `k61_subclass_property.py`, `k62_subclass_method.py`, `k63_subclass_mangled_self.py`, `g29_mangled_in_subclass.py`.

```
#396 GD FOLDS getattr's DEFAULT WHEN ONLY A SUBCLASS BINDS THE ATTRIBUTE  [slips past GD §7.43 / #376]
  g01  getattr(r, "k", 0) == 0 for r: R; S(R).__init__ stores self.k = 5                         CPython 5
  k52  S(R) class attribute k = 5;  k53 @dataclass S(R) k: int = 5;  k54 grandchild T(S(R)) stores k;  k61 S(R) @property k;
  k62  S(R) def k (getattr(r, "k", None) is None proved, CPython bound method);  k60 S(R) `for self.k in [5]`
  g29 / k63  getattr(r, "_S__k", 0) with S(R) storing self.__k (the #389 mangling repair maps only R's own fields)
  WhyML: `let f (r: r) : int ensures { result = 0 } = 0`. The class_binds_r376 map walks the receiver's MRO, never its
  descendants, although a receiver typed R may hold any subclass instance (§7.21 already says this for fields).
  REPAIR: in class_binds_r376 a class binds k when it, any base or ANY FILE DESCENDANT binds k (class body, field store,
  mangled spelling, property/method), and a class with descendants defined in __main__-reachable code counts them too.
```

## REPAIR (2026-10-26, e2 executor off 3b2d2e763; code + corpus + docs ffec1ac18 and follow-ups on this branch; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no emission change, ledger unchanged)
**Design: the default is the answer only if NO class of the static class's closed-world SUBCLASS closure can bind the name.**
`class_binds_r376[C]` is now the union, over every file class D deriving from C (C included), of the bindings of D and each of D's
file ancestors (+ the global attribute stores of #397). A class-scope node binds every identifier it carries unless its kind is on an
allow-list of NON-binding forms (loads, constants, call keywords, parameters, class-pattern attribute names, an import's module), so
annotation-only members (dataclass fields), `except .. as k`, `case k`, `global k`, type parameters all bind; `_C__x` is added for
every `__x` C binds. Docs annotations §7.53, translational §T.6.64. Witnesses 5624-5632 (g01, g29, k52, k53, k54, k60, k61, k62,
k63) and latent 5654 (`except .. as k` in a subclass body), PROVED at 3b2d2e763 -> REFUSED (`PYCSL-R376-GETATTR-CLASS-BINDING`,
message extended); control 5681 (a subclass binding another name) PROVED both. Residuals: a subclass defined in ANOTHER module and a
base from a user module (§7.43) are still not read.
Over-refusal measured (emission sweeps vs a worktree at 3b2d2e763, logs `getting-better/repair-r393-400/gates/`): root corpus 2424 -> 2431 .mlw (7 new controls), 0 MOVED / 0 GONE / 0 APPEARED; python-reference 2186 -> 2186, 0 / 0 / 0; mirror 53 / 53, 0 / 0 / 0 (no OWED proof). The FIRST cut over-refused 3 files, each removed by a justified refinement: mirror `frontend/pure_ast` (`class PyCSLSyntaxError(SyntaxError)` raised `(msg, (file, line, col, text))`: the SyntaxError family is now MODELLED by its constructor shape instead of refused) and corpus 0889 / 0890 (a CONTRACT's `r.n` on a TypedDict is the spec notation for a required key, not a runtime attribute read).
