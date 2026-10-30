# OPEN ROUTE #474 — IMPORTED MODULE CONSTANT FOLDED FROM A FLOW-INSENSITIVE, ASSIGN-ONLY SCAN OF THE DEPENDENCY
**Status: PARTIAL (executor x3, driver run #3, 2026-10-30): all 25 witnesses closed; residual named below), Severity 1.** Red-team round 39 (2026-10-29, on d6abee90b after #463-#473: 918 probes + 1064 mode re-proofs / 141 confirmed (probe, mode) pairs; rt38's 142 counted all closed). Census TSV `scratchpad/rt39/census.tsv`; the family block below is quoted from `scratchpad/rt39/FINDINGS.txt`.
Witnesses `witnesses-r474/` (25): `g42_c950_aug_mul_zero.py`, `g42_c954_tuple_unpack.py`, `g42_c962_if_rebind.py`, `g42_c963_try_rebind.py`, `g46_k1300_x_floordiv_aug.py`, `g46_k1301_x_and_aug.py`, `g46_k1302_x_rshift_aug.py`, `g46_k1303_x_xor_aug.py`, `g46_k1304_x_sub_aug.py`, `g46_k1305_x_mod_aug.py`, `g46_k1307_x_single_unpack.py`, `g46_k1308_x_list_unpack.py`, `g46_k1310_x_if_else_arm.py`, `g46_k1315_x_try_finally.py`, `g46_k1316_x_try_else.py`, `g46_k1317_x_nested_if.py`, `g46_k1318_x_mul_aug_expr.py`, `g49_j1703_str_const_aug.py`, `g49_j1704_str_const_if.py`, `g49_j1705_str_const_index.py`, `g49_j1708_const_requires_discharge.py`, `g51_e1901_const_in_ensures.py`, `g51_e1906_const_aliased_import.py`, `g51_e1908_const_in_pkg_init.py`, `g51_e1909_const_in_submodule.py`.

Driver repro: `scratchpad/rp39/repro.sh` (session scratchpad) on d6abee90b, 2026-10-29T23:41Z: all 16 rt39 verify exemplars (2+ per family) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F1 IMPORTED MODULE CONSTANT FOLDED FROM A FLOW-INSENSITIVE, ASSIGN-ONLY SCAN OF THE DEPENDENCY (25)
  WHAT: a constant the dependency rebinds by an augmented assignment, an unpacking target or inside an if / try / else / finally arm is folded to its FIRST value in the importer (the in-file twin is refused by Module3_Weaver's binding-site guard)
  EXEMPLAR: g46/k1304_x_sub_aug.py (h1304.py = `K = 1` / `K -= 1`; f: `from h1304 import K`, `#@ no_exception \all`, `return n // K`); g42/c962_if_rebind.py (h962: `K = 1` / `if True: K = 0`)
  CPYTHON: ZeroDivisionError (division by zero) -- the dependency's K is 0 when f runs (also: contracts broken through a rebound str constant `S = 'a'; S += 'b'` -> len 2, a callee's requires discharged with the stale value, constants of a package __init__ / submodule / aliased import)
  WHY IT PROVES: frontend/module_collect.py:30-63 `collect_module_constants` counts only top-level `Assign` with ONE Name target and `AnnAssign`: an `AugAssign` (`K -= 1`, `K *= 0`, `K //= 2` ...), an unpacking target (`K, = (0,)`, `[K, J] = [0, 1]`), and any binding inside `if` / `else` / `try` / `finally` / nested blocks are not counted, so K is "bound exactly once" with value 1. frontend/ir_resolve.py:1825-1830 then copies the DEPENDENCY's `module_constants` into the importer (`own[local] = dep_consts[orig]`) and Module 6 folds `K` to `1` (`pycsl_div n (1)` in the emitted WhyML). The same file read in-file is REFUSED (k1400-k1419, all 20 spellings) by Module3_Weaver.py:3280-3335's binding-site guard ("constant `K` of the module bound again in its scope") -- but that guard only fires when the constant is READ in its own module (`_nb_read`), which the dependency never does; and route #466, which really imports the dependency (and computes K == 0), is not consulted for the value.
  PROPOSED SYSTEMATIC REPAIR: ALLOW-LIST THE EXPORT: propagate a dependency constant only when the name has exactly ONE binding of ANY form anywhere in the dependency (walk every Name in Store/Del context, AugAssign / AnnAssign targets, for / with / except / match / walrus / import / def / class / global / nonlocal binders, at every depth) -- i.e. reuse the Weaver's `_nb_sites` binding-site table unconditionally for exported names, not only for names read locally -- AND cross-check the folded value against route #466's REAL import of the module (`_mods466[...]["mo"].__dict__[name]`): any disagreement (or a value #466 marks UNKNOWN) drops the fold (the importer then sees an opaque `val constant`, which is sound). Witness: the 25 F1 probes; control: an imported `K = 3` bound once still folds.
  PROBES: g42/c950_aug_mul_zero.py g42/c954_tuple_unpack.py g42/c962_if_rebind.py g42/c963_try_rebind.py g46/k1300_x_floordiv_aug.py g46/k1301_x_and_aug.py g46/k1302_x_rshift_aug.py g46/k1303_x_xor_aug.py g46/k1304_x_sub_aug.py g46/k1305_x_mod_aug.py g46/k1307_x_single_unpack.py g46/k1308_x_list_unpack.py g46/k1310_x_if_else_arm.py g46/k1315_x_try_finally.py g46/k1316_x_try_else.py g46/k1317_x_nested_if.py g46/k1318_x_mul_aug_expr.py g49/j1703_str_const_aug.py g49/j1704_str_const_if.py g49/j1705_str_const_index.py g49/j1708_const_requires_discharge.py g51/e1901_const_in_ensures.py g51/e1906_const_aliased_import.py g51/e1908_const_in_pkg_init.py g51/e1909_const_in_submodule.py
```

## Repair (executor x3, driver run #3, 2026-10-30)

ALLOW-LIST THE EXPORT, at the one place a dependency constant crosses the file boundary
(`frontend/ir_resolve.py` `_resolve_direct_imports`, the `module_constants` propagation; inline, mirror twin
`\trusted`, no new def, no axiom, NO new refusal): a dependency constant is folded into the importer only when
CPython's own `ast.parse` of the dependency's bytes binds the name at EXACTLY ONE site of any form anywhere in the
file (a Name stored / deleted at any depth -- augmented, annotated, unpacking, for, with, walrus, except, match
targets --, def / class names, import aliases, global / nonlocal), and the file has no namespace writer the table
cannot see (`from M import *`, `globals()`, `vars()`, `locals()`, `exec`, `eval`, `setattr`, `delattr`,
`__import__`, `.__dict__`, `.modules`). Otherwise the importer keeps the opaque `val constant` (route #325 then
refuses an opaque int under `no_exception`; a str claim is NOT PROVED). All 25 witnesses: PROVED at base
8aaa864ca, REFUSED (21, PYCSL-R325-OPAQUE-INT-FALLBACK) or NOT PROVED (4: j1703 j1704 j1705 e1901) at the repair.
Corpus `7450`-`7455` (7450-7454 PROVED at base, FAIL now; 7455 `globals()` write refused at base and now),
controls `7457` / `7458` (a constant bound once still folds). annotations.md 7.310.
RESIDUAL (not in this family's 25, found while repairing; PROVED at base AND at the repair): a constant mutated
from ANOTHER program module -- `import h; h.K = 0` in a peer module the importer imports, or a package
`__init__` doing `from . import sub; sub.K = 0` -- under an `ensures`-only claim (no `no_exception`, so route
#466 does not run): `from h import K` / `from p.sub import K` folds `K = 1`, CPython reads 0. Under
`no_exception` both are refused by #466 (the attribute store is not on its allow-list). Probes
`scratchpad/x3/res/rx5_peer_mutates_ens.py`, `rx6_init_mutates_sub_ens.py` (executor scratchpad). Closing it
needs a whole-program fact (no module of the program writes `h.K`), e.g. #466's real import run claim-free.
