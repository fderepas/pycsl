# OPEN ROUTE #344 — AN OVERRIDE INHERITED THROUGH THE MRO (MULTIPLE INHERITANCE) ESCAPES R5
**Status: REPAIRED, candidate (gen #37, 2026-10-24; r343 executor off b83a217b — see REPAIR). Was OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r344/`: `c01_mi_override_float.py`.

`class C(B, A)` with no own `m`; `A.m -> int`, `B.m -> float` returning 0.5. pycsl records `c__m refines a__m` and emits `c__m : real`, but R5 (route #338) reads the two defs from source and C has none, so the return annotation is never compared: `g(a: A)` with `ensures a.m() % 1 == 0` PROVES; CPython `g(C())` is 0.5. Contract-level MI variants (c02, j10, j11) FAIL correctly.

Repair: Run R5 over every recorded refinement pair, resolving the inherited def through the C3 MRO.

## REPAIR (2026-10-24, r343 executor off b83a217b, repaired with routes #343 / #345; code 9b8ee8b8, corpus 3aa9c2b2, docs e1ea6c14)
**Design.** In R5 (route #338, inline in `_run_pipeline`'s route #278 block, mirror twin `\trusted`), a pair side whose class has
no def of the method in the source is resolved through Python's C3 linearization of the file's classes (bases by name, computed
iteratively inline: `L[K] = K + merge(L[B1], .., L[Bn], [B1, .., Bn])`, a non-file base taken as `[B]`, a cycle or an
inconsistent merge stopping the walk) to the first MRO class defining the method; that def is compared by R5 as before
(`PYCSL-SEM-OVERRIDE-REFINEMENT`, off under `--assume-class-exact`). No emission change.
**Probe table** (full proof via heavy.sh; base = b83a217b):
| witness | corpus | base | after |
|---|---|---|---|
| c01 `class C(B, A): pass`, `A.m -> int`, `B.m -> float` | 4623 | rc=0 PROVED | rc=1 REFUSED OVERRIDE-REFINEMENT (`c__m` of `a__m`: `float` not <: `int`) |
| control: diamond `C(B, D)`, MRO-picked `D.m -> bool` under `A.m -> int` | 4633 | rc=0 PROVED | rc=0 PROVED |
A diamond latent (`C(B(A), D(A))`, `D.m -> float`, where depth-first would pick A.m) was probed and is REFUSED at base already
(the `d__m`/`a__m` pair itself fails R5), so it is not a witness.
**Blast radius** (base worktree at b83a217b vs candidate, `bin/byte-diff-sweep.sh` + `bin/byte-diff-compare.py`): root 2284 base /
2293 candidate, 0 MOVED / 0 GONE / 0 APPEARED (9 new witness files emit; the 5 GONE of the first compare were files lost to a
concurrent `check-assumed-facts` sweep in the same tree, re-emitted individually: identical); pyref 2186/2186 0/0/0; mirror
53/53 0/0/0 (`bin/mirror-emit-sweep.sh`, `--min-files 50`) — no mover, no OWED whole-file proof. Ledger 3, no new def, no new
refusal code (the R343 assertion is a VC label; #345 reuses `PYCSL-R341-CLASS-BASE-NOT-A-NAME`), no gate loosened.
**Gates**: see the shared gate list in route #343's REPAIR.
**Residuals.** An MRO class outside the file (an imported base) is skipped in the lookup (route #338's imported-base residual);
`__getattr__` / metaclass method resolution is not modelled.
