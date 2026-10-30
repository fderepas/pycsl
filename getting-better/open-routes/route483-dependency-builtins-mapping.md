# OPEN ROUTE #483 — DEPENDENCY CODE REACHES exec / setattr THROUGH ITS `__builtins__` MAPPING (ENSURES-ONLY CLAIM: ROUTE #474 FOLDS THE STALE CONSTANT)
**Status: REPAIRED (driver run #3, executor y2; see Repair below), Severity 1.** Red-team round 40 (2026-10-30, on dcf424f75 after #475-#480 repaired / #474 partial: 624 probes + 1009 mode re-proofs / 129 confirmed (probe, mode) pairs on 103 probes; rt39's 141 all closed). Census TSV `scratchpad/rt40/census.tsv`; the family block below is quoted from `scratchpad/rt40/FINDINGS.txt`.
Witnesses `witnesses-r483/` (12): `g80_a8109_ens_builtins_dict_exec.py`, `g82_c8851_ens_bdict_get_exec.py`, `g82_c8854_ens_bdict_setattr_selfimport.py`, `g82_c8855_ens_bdict_exec_in_func.py`, `g82_c8856_ens_bdict_exec_alias.py`, `g82_c8857_ens_bdict_eval_walrus.py`, `g93_v9700_bdict_setattr_func_ens.py`, `g93_v9701_bdict_exec_redef_ens.py`, `g93_v9705_bdict_two_step_alias_ens.py`, `g93_v9706_bdict_items_loop_ens.py`, `g93_v9707_bdict_exec_str_const_ens.py`, `g93_v9708_bdict_exec_requires_discharge.py`.

Driver repro: `scratchpad/rp40/repro.sh` (session scratchpad) on dcf424f75, 2026-10-30T07:30Z: all 16 rt40 verify exemplars (2+ per family, F5 under --memory-model typed / store) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F2 DEPENDENCY CODE REACHES exec / setattr THROUGH ITS `__builtins__` MAPPING (ENSURES-ONLY CLAIM: ROUTE #474 FOLDS THE STALE CONSTANT) (16)
  WHAT: in an IMPORTED module `__builtins__` is the builtins DICT, so `__builtins__['exec']('K = 0')`, `__builtins__.get('exec')(...)`, `_b = __builtins__; _b['exec'](...)`, `__builtins__['setattr'](_s, 'K', 0)` rebind the dependency's constant (or function) without any of the spellings the #474 writer list and the Weaver's namespace-builtin rules key on; `from h import K` still folds `K = 1`
  EXEMPLAR: g80/a8109_ens_builtins_dict_exec.py (h8009.py: `K = 1` / `__builtins__['exec']('K = 0')`; f: `from h8009 import K`, `#@ ensures \result == n`, `return n * K`)
  CPYTHON: f(1) returns 0 -> VIOLATION contract (all rows); under `no_exception` the same dependencies are refused by route #466 (the call is not a side-effect-free stdlib callable), so the leak is the ensures-only claim; the function-rebinding rows (v9700 setattr on the claimed `g`, v9701 `exec('def g...')`) also prove under --memory-model typed and store (counted as (probe, mode) pairs)
  WHY IT PROVES: frontend/ir_resolve.py:1882-1924 (route #474): the namespace-writer test flags a `Call` whose func is a bare `Name` in {globals, vars, locals, exec, eval, setattr, delattr, __import__} or an `Attribute` named `__dict__` / `modules` -- `__builtins__['exec'](...)` is a Call of a SUBSCRIPT and `__builtins__.get('exec')` a Call of an attribute `get`, so `_dy474` stays False and K (bound once syntactically) is folded. Module3_Weaver.py:3736-3770 deliberately exempts the NAME `__builtins__` from the namespace-builtin rules ('#127's own rules already cover writing through it' -- they cover the main file's module object, not a dependency's dict). Route #466, which would run the dependency, is consulted only under `no_exception`.
  PROPOSED SYSTEMATIC REPAIR: ALLOW-LIST THE DEPENDENCY'S TOP-LEVEL CODE FOR EVERY CLAIM, not only `no_exception`: fold an imported constant / bind an imported function only when route #466's real import of the dependency (already implemented, claim-free run) leaves the name with the folded value (`_mods466[..]['mo'].__dict__[name]` is the literal) -- the residual of #474 asks for the same whole-program fact; until then, treat ANY read of the name `__builtins__` in a dependency (and `builtins` module attribute calls) as a namespace writer in the #474 test (refuse-by-default: no fold). Witness: the F2 probes; control: a dependency `K = 3` bound once with no `__builtins__` read still folds.
  PROBES: g80/a8109_ens_builtins_dict_exec.py g82/c8851_ens_bdict_get_exec.py g82/c8854_ens_bdict_setattr_selfimport.py g82/c8855_ens_bdict_exec_in_func.py g82/c8856_ens_bdict_exec_alias.py g82/c8857_ens_bdict_eval_walrus.py g93/v9700_bdict_setattr_func_ens.py g93@typed/v9700_bdict_setattr_func_ens.py g93@store/v9700_bdict_setattr_func_ens.py g93/v9701_bdict_exec_redef_ens.py g93@typed/v9701_bdict_exec_redef_ens.py g93@store/v9701_bdict_exec_redef_ens.py g93/v9705_bdict_two_step_alias_ens.py g93/v9706_bdict_items_loop_ens.py g93/v9707_bdict_exec_str_const_ens.py g93/v9708_bdict_exec_requires_discharge.py
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
