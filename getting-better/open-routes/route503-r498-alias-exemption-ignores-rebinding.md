# OPEN ROUTE #503 — ROUTE #498's SAME-OBJECT EXEMPTION FOLLOWS `b = a` TO THE NAME `a` BUT NOT TO A's BINDING TIME: AFTER `b = a; a = n + 1000` THE TWO OPERANDS SHARE THE ROOT NAME `a`, THE TEST IS SKIPPED, AND `a is b` IS DECIDED AS VALUE EQUALITY
**Status: REPAIRED (executor u6, driver run #4, 2026-11-01, off e5237469f; see REPAIR below), Severity 1.** Red-team round 45 (driver run #4, 2026-11-01, on 0d561a23b = main + the #496 / #498-#500 repairs under integration: 332 probes in g600-g607, 303 CPython-breaching, 15 confirmed in 5 families, all default mode; rt44's 139 pairs: 127 refused by the repairs, #497's 12 still prove = user decision). Census `scratchpad/rt45/census.tsv`; the family block below is quoted from `scratchpad/rt45/FINDINGS.txt`.
Witnesses `witnesses-r503/` (2): `g601_b60100_alias_root_rebound.py`, `g601_b60102_alias_root_rebound_isnot.py`.

Driver repro: session scratchpad `rp45/repro.sh` on 0d561a23b, 2026-11-01T05:35Z: all 8 rt45 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F3 ROUTE #498's SAME-OBJECT EXEMPTION FOLLOWS `b = a` TO THE NAME `a` BUT NOT TO A's BINDING TIME: AFTER `b = a; a = n + 1000` THE TWO OPERANDS SHARE THE ROOT NAME `a`, THE TEST IS SKIPPED, AND `a is b` IS DECIDED AS VALUE EQUALITY (2)
  EXEMPLAR: g601/b60100_alias_root_rebound.py: `#@ ensures \result == True` f(n): `a = n + 1000; b = a; a = n + 1000; return a is b`
  CPYTHON: f(5) -> False (VIOLATION contract False); b60102 (`a = n * 1000; b = a; a = n * 1000; return a is not b`, claimed False) -> True
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt45 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt45/g601/b60100_alias_root_rebound.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt45/g601 && /home/fabrice/git/pycsl-rt45/.venv/bin/python3 -E -s b60100_alias_root_rebound.py)
  WHY: src/pycsl/pycsl.py ~14957-14970 (route #498): `_root498` walks a chain of single plain assignments (`len(_bind498[nm]) == 1`) from each operand. `b` has one binding (`b = a`), so its root is the NAME `a`; `a` has two bindings, so the walk stops at `a`. The roots compare equal and the `_root498[0] == _root498[1]` test `continue`s past the site before the freshness walk ever sees `a = n + 1000`. REPAIR: exempt only when the root's own binding count is 1 (or no rebinding of the root lies between the alias and the test).
  PROBES: g601/b60100_alias_root_rebound.py g601/b60102_alias_root_rebound_isnot.py
```

## REPAIR (executor u6, driver run #4, 2026-11-01; annotations §7.503)

Inline in route #498's pass in `pycsl.py::_run_pipeline` (mirror twin `\trusted`; no new def, no axiom; #498's own message
byte-identical), new code `PYCSL-R503-IS-ALIAS-ROOT-REBOUND`: one name with ITSELF (`a is a`) stays exempt; a common root of
the two alias chains exempts the site only when that root is bound ONCE for the whole call (a parameter never rebound, an
outer name the function never binds, a local with exactly one plain assignment). Otherwise route #498's freshness walk
judges the site and refuses it under the new code when an operand may be fresh. A root bound once inside a loop needs no
extra arm: an alias read in a later iteration is bound twice (the chain stops at it) or is not definitely assigned (route
#264; measured: the loop-carried probe is refused by #264 at base).

Witnesses: both in `witnesses-r503/` REFUSED (`PYCSL-R503-IS-ALIAS-ROOT-REBOUND`) under default, `--memory-model typed` and
`--memory-model store` (6/6 runs). Corpus 7980 / 7981 (PROVED at base, REFUSED), 7982 (a rebound unannotated parameter: NOT
PROVED at base, refused by name); controls 7990 (root bound once, an unrelated name rebound) / 7991 (`a is a` on a rebound
name) PROVED. Advice followed (witnesses-r503/advice): `==` and a renamed second binding VERIFY (default model).
Over-refusal: corpus root 0 MOVED / 0 GONE / 0 APPEARED vs v23/bd (5 new controls emit), pyref 2186/2186 0/0/0, mirror 53/53 0/0/0 vs mir-main14 (a first draft refused 2 mirror files through #504 -- frontend/pure_ast `operator_precedence is not _Precedence.FACTOR` via a class-level dict read on `self`, module6_whyml/statements `stmt.origin is not _ABSENT` against ir_schema's `object()` sentinel -- fixed in fc3e8512f); rt43 / rt44 / rt45 CPython-honest controls (345): 0 refused by #503 / #504 / #505.
Commits: 15b5b3e37 (rule + corpus), fc3e8512f (#504 mirror fix in the same pass), dd736c419 (pathlib read, CTXBIND ratchet kept at 51). Final battery on dd736c419: fidelity 3/3, carriers, advice 217, planes 62/62 fast green; driver runs --slow.
