# OPEN ROUTE #345 — AN ATTRIBUTE BASE OF A FOREIGN MODULE RESOLVES BY ITS TAIL TO A SAME-NAMED CLASS OF THE FILE
**Status: REPAIRED, candidate (gen #37, 2026-10-24; r343 executor off b83a217b — see REPAIR). Was OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r345/`: `f01_import_tail_base.py`, `f02_import_tail_base_inv.py`.

`import rt25other as om; class S(om.B)` while this file also defines `class B` with `ensures \result == 1` (f01) or an invariant (f02): S inherits the LOCAL B's contract/invariant in the model; CPython `S().m()` is 2 (rt25other.B.m). Route #341 residual (3) assumed the tail resolution is only reached for a self-import; here the module is foreign. Helper `rt25other.py` in the witness dir.

Repair: Resolve an attribute base by its tail only for a provable self-import; any other module's class is an imported base.

## REPAIR (2026-10-24, r343 executor off b83a217b, repaired with routes #343 / #344; code 9b8ee8b8, corpus 3aa9c2b2, docs e1ea6c14)
**Design: sound refusal (route #341's shape).** The ~20 readers of `ClassDef.bases` take an attribute base by its tail, so
treating `om.B` as an imported base would mean changing all of them; instead, in route #341's block (inline in `_run_pipeline`,
mirror twin `\trusted`), an attribute base that passes the imported-root check is REFUSED (`PYCSL-R341-CLASS-BASE-NOT-A-NAME`,
message names route #345) when its tail names a class of the file, unless it is a SELF-import: its root is a `Name` bound only by
`import <stem> [as r]` where `<stem>` is this file's module name (no `from`-import / other `import` binding it). The advice:
`from m import B as OtherB`. Census: 0 corpus / pyref / mirror movers (byte-diff below).
**Probe table** (full proof via heavy.sh; base = b83a217b; the corpus forms use the stdlib `fractions` module instead of the
helper `rt25other.py`):
| witness | corpus | base | after |
|---|---|---|---|
| f01 `import rt25other as om; class S(om.B)` + local `B` with `ensures \result == 1` | (dir) / 4624 (`fractions.Fraction`) | rc=0 PROVED | rc=1 REFUSED R341/#345 |
| f02 same + local invariant | (dir) / 4625 | rc=0 PROVED | rc=1 REFUSED R341/#345 |
| control: `class S(om.Fraction)`, no local `Fraction` | 4634 | rc=0 PROVED | rc=0 PROVED |
| control (scratch only; a digit-named corpus file cannot self-import): `import f01self as me; class S(me.B)` | — | rc=0 PROVED | rc=0 PROVED |
**Blast radius** (base worktree at b83a217b vs candidate, `bin/byte-diff-sweep.sh` + `bin/byte-diff-compare.py`): root 2284 base /
2293 candidate, 0 MOVED / 0 GONE / 0 APPEARED (9 new witness files emit; the 5 GONE of the first compare were files lost to a
concurrent `check-assumed-facts` sweep in the same tree, re-emitted individually: identical); pyref 2186/2186 0/0/0; mirror
53/53 0/0/0 (`bin/mirror-emit-sweep.sh`, `--min-files 50`) — no mover, no OWED whole-file proof. Ledger 3, no new def, no new
refusal code (the R343 assertion is a VC label; #345 reuses `PYCSL-R341-CLASS-BASE-NOT-A-NAME`), no gate loosened.
**Gates**: see the shared gate list in route #343's REPAIR.
**Residuals.** The self-import test is by module stem (sys.path[0] is the script's directory, so `import <stem>` there is this
file); a package-qualified self-import (`import pkg.me`) is refused (over-refusal, 0 users). A foreign attribute base whose tail
names no file class remains an imported base (unchanged).
