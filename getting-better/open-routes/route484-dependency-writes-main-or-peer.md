# OPEN ROUTE #484 — A DEPENDENCY WRITES INTO THE CLAIMED MODULE (`import __main__; __main__.K = 0`), OR REBINDS A PEER DEPENDENCY'S FUNCTION AT IMPORT TIME (ENSURES-ONLY; EXTENDS #474's DECLARED RESIDUAL)
**Status: REPAIRED (driver run #3, executor y2; see Repair below), Severity 1.** Red-team round 40 (2026-10-30, on dcf424f75 after #475-#480 repaired / #474 partial: 624 probes + 1009 mode re-proofs / 129 confirmed (probe, mode) pairs on 103 probes; rt39's 141 all closed). Census TSV `scratchpad/rt40/census.tsv`; the family block below is quoted from `scratchpad/rt40/FINDINGS.txt`.
Witnesses `witnesses-r484/` (10): `g80_a8601_dep_writes_main_ens.py`, `g82_c8990_dep_rebinds_main_callee_ens.py`, `g82_c8992_dep_alias_main_ens.py`, `g82_c8995_dep_writes_main_list_ens.py`, `g91_p9506_dep_writes_main_str_ens.py`, `g91_p9512_pkg_init_writes_main_ens.py`, `g92_r9600_peer_rebinds_dep_func_ens.py`, `g92_r9601_peer_rebinds_dep_func_attr_ens.py`, `g92_r9607_peer_rebinds_in_function_ens.py`, `g92_r9609_peer_setattr_dep_func_ens.py`.

Driver repro: `scratchpad/rp40/repro.sh` (session scratchpad) on dcf424f75, 2026-10-30T07:30Z: all 16 rt40 verify exemplars (2+ per family, F5 under --memory-model typed / store) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F3 A DEPENDENCY WRITES INTO THE CLAIMED MODULE (`import __main__; __main__.K = 0`), OR REBINDS A PEER DEPENDENCY'S FUNCTION AT IMPORT TIME (ENSURES-ONLY; EXTENDS #474's DECLARED RESIDUAL) (18)
  WHAT: a module the claimed file imports rebinds, at import time, a constant / str constant / callee / dict item of the CLAIMED file (`__main__`), or a function of another dependency (`import h; h.g = ...` in a peer module, also via setattr or inside a function the peer calls); the claimed file's own constant fold and callee resolution are judged on its text alone
  EXEMPLAR: g80/a8601_dep_writes_main_ens.py (main: `K = 1`, `import h8600`, `#@ ensures \result == n`, `return n * K`; h8600.py: `import __main__` / `__main__.K = 0`); g82/c8990_dep_rebinds_main_callee_ens.py (h8990: `__main__.g = lambda x: 0`, f returns `g(n)` under `ensures \result == n`)
  CPYTHON: f(1) returns 0 (len 2 for a str constant) -> VIOLATION contract; the no_exception twins (a8600, p9505, p9508, p9510) are REFUSED by route #466 (the dependency's attribute store is not on its allow-list); the peer function-rebinding rows (r9600 r9601 r9607 r9609) also prove under typed and store (counted as pairs). NOT COUNTED: r9606 (a peer module rebinds an imported STR constant) is exactly #474's declared residual (excluded.txt)
  WHY IT PROVES: Module3_Weaver.py's binding-site guard and the in-file constant fold see only the claimed file's bindings; a dependency's `__main__.K = 0` is an attribute store on ANOTHER module object (the Weaver's rebinding rule fires for a store on the dependency's OWN module, a8100, and for the same `__main__.K = 0` placed inside a dependency FUNCTION, c8993 / c8994, but not for it at the dependency's top level); route #466, the only pass that runs the dependency's top-level code, is consulted only for `no_exception` claims (pycsl.py, `_run_pipeline` #466 block). Route #474's README residual names exactly this class for IMPORTED constants (`import h; h.K = 0` in a peer module); these rows are the same mechanism with new targets: the claimed module itself, its callees / class methods / dict items, and the functions of other dependencies (builtins / stdlib patching, p9500 / p9503 / p9504, and peer method / container writes, r9603 / r9604, did NOT prove).
  PROPOSED SYSTEMATIC REPAIR: the residual's whole-program fact, made total: run route #466's real import claim-free for EVERY verified file that imports a program module, snapshot the claimed module's namespace and each imported module's namespace AFTER all imports complete, and REFUSE (or fall back to the opaque value) any folded constant / resolved callee / modelled container whose runtime value differs from the model's (allow-list: admit only names whose post-import identity is the object the model describes). Witness: the F3 probes; control: a dependency that only reads `__main__.K`.
  PROBES: g80/a8601_dep_writes_main_ens.py g82/c8990_dep_rebinds_main_callee_ens.py g82/c8992_dep_alias_main_ens.py g82/c8995_dep_writes_main_list_ens.py g91/p9506_dep_writes_main_str_ens.py g91/p9512_pkg_init_writes_main_ens.py g92/r9600_peer_rebinds_dep_func_ens.py g92@typed/r9600_peer_rebinds_dep_func_ens.py g92@store/r9600_peer_rebinds_dep_func_ens.py g92/r9601_peer_rebinds_dep_func_attr_ens.py g92@typed/r9601_peer_rebinds_dep_func_attr_ens.py g92@store/r9601_peer_rebinds_dep_func_attr_ens.py g92/r9607_peer_rebinds_in_function_ens.py g92@typed/r9607_peer_rebinds_in_function_ens.py g92@store/r9607_peer_rebinds_in_function_ens.py g92/r9609_peer_setattr_dep_func_ens.py g92@typed/r9609_peer_setattr_dep_func_ens.py g92@store/r9609_peer_setattr_dep_func_ens.py
```

## Repair (driver run #3, executor y2, off e3b3711a2) -- routes #483 and #484 closed together

ONE structural rule, allow-list polarity, every claim kind (inline in `_run_pipeline` right after route #466, whose
own refusal keeps precedence under `no_exception`; mirror twin `\trusted`; no new def, no axiom; new code
`PYCSL-R483-IMPORT-TIME-NAMESPACE-WRITER`; annotations.md 7.370). Over the program's import closure (this file and
every module its imports resolve to, any depth, package `__init__`s included) the code that RUNS AT IMPORT TIME --
module statements outside `def` bodies (the claimed file's `if __name__ == "__main__":` block excepted), decorators,
defaults, annotations, class bodies, lambdas, closed by NAME to a fixpoint (a function named in reached code; a class
named there is live with its bases: its dunders and its methods named in reached code; a base's subclass hooks; a
metaclass's methods; a module-level `__getattr__`) -- must, in every module but the claimed one, stay in the fragment
whose effect on other namespaces is understood: imports only of program modules, installed libraries and an
allow-listed standard library (never `__main__` / the claimed file; `sys` only through allow-listed attributes); no
`exec` / `eval` / `compile` / `globals` / `vars` / `locals` / `setattr` / `delattr` / `getattr` / `__import__` /
annotation evaluators / dunder names outside a small allow-list (`__builtins__` ...) -- except `getattr(x,
"<literal, not dunder>")`, `setattr` / `delattr` on the enclosing method's own `self`, and `g = globals()` bound once
to a name no import-time code reads; no dunder attribute outside a read-only allow-list, no frame / code attribute,
no `.modules` / `._getframe` / `.meta_path` / `.builtins` on any receiver; a plain-imported module name only as an
attribute-read receiver; no attribute store / delete whose NAME is bound at a module top level or in a class body of
the closure (on the method's own `self`: only a method name of that class's family). Otherwise REFUSED.

Why this and not route #466's real run claim-free (the brief's two candidates, both measured on the 195 corpus /
mirror / red-team-control files whose closure holds a program module, base e3b3711a2): the #466 runner, run
claim-free, refused the mirror's `pycsl.py` (an attribute store in `frontend/pure_ast.py`) and
`Module6_WhyMLTranspiler.py` (a mixin decorator it does not admit) and 3 corpus files with a relative import, and
executes the program's code inside the verifier; the allow-list above refuses 0 honest corpus files, 0 mirror files and
0 red-team PASS controls (only route #474's own NOT PROVED witnesses 7570-7572 move to REFUSED).

Residuals (named, not closed): a dependency function the claimed code calls at RUN time (its effects are its
contract's, route #119 / the Weaver's rebinding rules); a dependency method invoked unbound with a CLASS as `self`
(`C.m(D)`) storing a data attribute of `D`; file-system writes at import (`os` / `pathlib` / `subprocess` are on the
allow-list) changing a module the verifier already read; an installed library's own import-time code (a declared
library, as under route #466).
